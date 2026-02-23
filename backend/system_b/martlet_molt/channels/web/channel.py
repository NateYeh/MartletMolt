"""
Web Channel 實現
WebSocket 通訊通道
"""

from collections.abc import AsyncIterator
from typing import Any

from fastapi import WebSocket
from loguru import logger

from martlet_molt.channels.base import (
    BaseChannel,
    ChannelMessage,
    ChannelResponse,
    ChannelStatus,
)


class WebChannel(BaseChannel):
    """WebSocket 通訊通道"""

    id = "web"
    name = "Web Channel"
    description = "WebSocket 通訊通道"

    def __init__(self, websocket: WebSocket, session_id: str = ""):
        """
        初始化 Web Channel

        Args:
            websocket: FastAPI WebSocket 連線
            session_id: 會話 ID
        """
        self._websocket = websocket
        self._session_id = session_id

    async def start(self) -> bool:
        """
        接受 WebSocket 連線

        Returns:
            bool: 是否啟動成功
        """
        try:
            await self._websocket.accept()
            self._status = ChannelStatus.RUNNING
            logger.info(f"WebSocket 連線已建立，session_id: {self._session_id}")
            return True
        except Exception as e:
            logger.exception(f"接受 WebSocket 連線失敗: {e}")
            self._status = ChannelStatus.ERROR
            return False

    async def receive(self) -> AsyncIterator[ChannelMessage]:
        """
        從 WebSocket 接收訊息

        Yields:
            ChannelMessage: 接收到的訊息
        """
        while self.is_running:
            try:
                # 接收 JSON 格式訊息
                data: dict[str, Any] = await self._websocket.receive_json()

                content = data.get("content", "")
                if not content:
                    continue

                yield ChannelMessage(
                    content=content,
                    user_id=data.get("user_id", "web_user"),
                    session_id=self._session_id,
                    metadata={
                        "source": "web",
                        "raw": data,
                    },
                )

            except Exception as e:
                logger.exception(f"接收 WebSocket 訊息時發生錯誤: {e}")
                self._status = ChannelStatus.ERROR
                break

    async def send(self, response: ChannelResponse) -> bool:
        """
        通過 WebSocket 發送回應

        Args:
            response: 回應內容

        Returns:
            bool: 是否發送成功
        """
        try:
            await self._websocket.send_json(response.model_dump())
            return True
        except Exception as e:
            logger.exception(f"發送 WebSocket 訊息時發生錯誤: {e}")
            return False

    async def send_stream(self, content: str) -> bool:
        """發送串流片段"""
        return await self.send(ChannelResponse(
            content=content,
            metadata={"type": "stream"}
        ))

    async def send_done(self) -> bool:
        """發送完成訊號"""
        return await self.send(ChannelResponse(
            content="",
            metadata={"type": "done"}
        ))

    async def send_error(self, error: str) -> bool:
        """發送錯誤訊息"""
        return await self.send(ChannelResponse(
            content="",
            success=False,
            error=error,
            metadata={"type": "error"}
        ))

    async def stop(self) -> bool:
        """
        關閉 WebSocket 連線

        Returns:
            bool: 是否停止成功
        """
        try:
            await self._websocket.close()
            self._status = ChannelStatus.STOPPED
            logger.info(f"WebSocket 連線已關閉，session_id: {self._session_id}")
            return True
        except Exception as e:
            logger.exception(f"關閉 WebSocket 連線時發生錯誤: {e}")
            self._status = ChannelStatus.ERROR
            return False

    async def health_check(self) -> bool:
        """
        健康檢查

        Returns:
            bool: 是否健康
        """
        if self._status != ChannelStatus.RUNNING:
            return False

        # 檢查 WebSocket 連線狀態
        try:
            # 嘗試發送一個 ping（如果支援的話）
            # WebSocket 本身沒有內建的 ping/pong，這裡只是檢查狀態
            return self._websocket.client_state.name == "CONNECTED"
        except Exception:
            return False
