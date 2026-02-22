"""
串流緩衝區管理

用途：
- 作為 OpenAI 串流與前端之間的緩衝層
- 支持多個消費者同時讀取
- 前端斷線不影響生產者（OpenAI API）
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger


class StreamStatus(str, Enum):  # noqa: UP042
    """串流狀態"""

    PENDING = "pending"  # 等待開始
    STREAMING = "streaming"  # 串流中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失敗
    CANCELLED = "cancelled"  # 已取消


@dataclass
class StreamChunk:
    """串流片段"""

    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamBuffer:
    """
    串流緩衝區

    使用 asyncio.Queue 作為緩衝層，
    生產者（OpenAI API）和消費者（前端）解耦。
    """

    session_id: str
    max_size: int = 1000  # 最大緩衝區大小

    # 內部狀態（使用 field 工廠函數避免 mutable 預設值問題）
    _status: StreamStatus = field(default=StreamStatus.PENDING, init=False)
    _full_content: str = field(default="", init=False)
    _error: str = field(default="", init=False)
    _created_at: str = field(default_factory=lambda: datetime.now().isoformat(), init=False)
    _completed_at: str = field(default="", init=False)
    _queue: asyncio.Queue[StreamChunk] = field(default_factory=asyncio.Queue, init=False)

    def __post_init__(self) -> None:
        """初始化 Queue（避免 dataclass 默認值問題）"""
        if not isinstance(self._queue, asyncio.Queue):
            self._queue = asyncio.Queue(maxsize=self.max_size)

    @property
    def status(self) -> StreamStatus:
        """取得當前狀態"""
        return self._status

    @property
    def full_content(self) -> str:
        """取得完整內容"""
        return self._full_content

    @property
    def error(self) -> str:
        """取得錯誤信息"""
        return self._error

    def start(self) -> None:
        """標記串流開始"""
        self._status = StreamStatus.STREAMING
        logger.info(f"Stream buffer started: session={self.session_id}")

    async def put(self, chunk: str, metadata: dict[str, Any] | None = None) -> None:
        """
        推入片段到緩衝區

        Args:
            chunk: 片段內容
            metadata: 可選的元數據
        """
        if self._status != StreamStatus.STREAMING:
            logger.warning(f"Buffer not in streaming status: {self._status}")
            return

        # 累積完整內容
        self._full_content += chunk

        # 推入 Queue
        stream_chunk = StreamChunk(content=chunk, metadata=metadata or {})
        await self._queue.put(stream_chunk)

        logger.debug(f"Buffer put: session={self.session_id}, chunk_len={len(chunk)}")

    def put_sync(self, chunk: str, metadata: dict[str, Any] | None = None) -> None:
        """
        同步推入片段（用於非異步環境）

        Args:
            chunk: 片段內容
            metadata: 可選的元數據
        """
        if self._status != StreamStatus.STREAMING:
            return

        self._full_content += chunk
        stream_chunk = StreamChunk(content=chunk, metadata=metadata or {})
        self._queue.put_nowait(stream_chunk)

    async def get(self, timeout: float = 30.0) -> StreamChunk | None:
        """
        從緩衝區讀取片段

        Args:
            timeout: 超時時間（秒）

        Returns:
            StreamChunk 或 None（超時或結束）
        """
        try:
            chunk = await asyncio.wait_for(self._queue.get(), timeout=timeout)
            return chunk
        except TimeoutError:
            logger.warning(f"Buffer get timeout: session={self.session_id}")
            return None
        except Exception as e:
            logger.exception(f"Buffer get error: {e}")
            return None

    def complete(self) -> None:
        """標記串流完成"""
        self._status = StreamStatus.COMPLETED
        self._completed_at = datetime.now().isoformat()

        # 推入結束標記
        self._queue.put_nowait(StreamChunk(content="[DONE]"))

        logger.info(f"Stream buffer completed: session={self.session_id}, total_len={len(self._full_content)}")

    def fail(self, error: str) -> None:
        """標記串流失敗"""
        self._status = StreamStatus.FAILED
        self._error = error
        self._completed_at = datetime.now().isoformat()

        # 推入錯誤標記
        self._queue.put_nowait(StreamChunk(content=f"[ERROR] {error}"))

        logger.error(f"Stream buffer failed: session={self.session_id}, error={error}")

    def cancel(self) -> None:
        """標記串流取消"""
        self._status = StreamStatus.CANCELLED
        self._completed_at = datetime.now().isoformat()

        # 清空 Queue
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        logger.warning(f"Stream buffer cancelled: session={self.session_id}")

    async def stream(self) -> AsyncIterator[str]:
        """
        串流迭代器（用於前端消費）

        Yields:
            片段內容
        """
        while True:
            chunk = await self.get()
            if chunk is None:
                # 超時或錯誤
                logger.warning("Stream ended due to timeout or error")
                break

            if chunk.content == "[DONE]":
                logger.info(f"Stream completed: session={self.session_id}")
                break

            if chunk.content.startswith("[ERROR]"):
                logger.error(f"Stream error: {chunk.content}")
                break

            yield chunk.content

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典（用於序列化）"""
        return {
            "session_id": self.session_id,
            "status": self._status.value,
            "full_content": self._full_content,
            "error": self._error,
            "created_at": self._created_at,
            "completed_at": self._completed_at,
            "queue_size": self._queue.qsize(),
        }


class StreamBufferManager:
    """
    串流緩衝區管理器

    管理所有活躍的串流緩衝區。
    """

    def __init__(self, max_buffers: int = 100):
        self._buffers: dict[str, StreamBuffer] = {}
        self._max_buffers = max_buffers

    def create(self, session_id: str, max_size: int = 1000) -> StreamBuffer:
        """
        創建新的串流緩衝區

        Args:
            session_id: 會話 ID
            max_size: 最大緩衝區大小

        Returns:
            StreamBuffer 實例
        """
        if len(self._buffers) >= self._max_buffers:
            # 清理舊的緩衝區
            self._cleanup_old_buffers()

        buffer = StreamBuffer(session_id=session_id, max_size=max_size)
        self._buffers[session_id] = buffer

        logger.info(f"Created stream buffer: session={session_id}")
        return buffer

    def get(self, session_id: str) -> StreamBuffer | None:
        """取得串流緩衝區"""
        return self._buffers.get(session_id)

    def remove(self, session_id: str) -> bool:
        """移除串流緩衝區"""
        if session_id in self._buffers:
            buffer = self._buffers[session_id]
            buffer.cancel()
            del self._buffers[session_id]
            logger.info(f"Removed stream buffer: session={session_id}")
            return True
        return False

    def _cleanup_old_buffers(self) -> None:
        """清理已完成的舊緩衝區"""
        to_remove = []
        for session_id, buffer in self._buffers.items():
            if buffer.status in [
                StreamStatus.COMPLETED,
                StreamStatus.FAILED,
                StreamStatus.CANCELLED,
            ]:
                to_remove.append(session_id)

        for session_id in to_remove:
            self.remove(session_id)

        logger.info(f"Cleaned up {len(to_remove)} old buffers")


# 全域串流緩衝區管理器
stream_buffer_manager = StreamBufferManager()
