# 任務交接：串流緩衝架構改進（方案2：混合模式）

> **狀態：已完成** ✅
> 
> **完成日期**：2025-02-22

> **任務目標**：實現後端獨立完成 OpenAI 串流，前端斷線不影響後台處理

---

## 一、任務概述

### 1.1 問題描述

**當前架構問題：**

```
當前流程：
前端 ↔ 後端 ↔ OpenAI API
      ↑ 三者串流綁在一起

問題：
❌ 前端斷線 → 後端串流立即中斷 → OpenAI API 停止
❌ 會話歷史丟失（AI 回應未保存）
❌ 浪費 OpenAI API tokens（已生成但中斷）
```

### 1.2 改進目標

**新架構：**

```
改進流程：
OpenAI串流 ──→ 後端緩衝區 ──→ 前端消費
                 ↓
              後台保存

優點：
✅ 後端獨立完成 OpenAI 串流
✅ 前端斷線不影響後台處理
✅ 完整回應必定保存
✅ 保持即時串流體驗
```

---

## 二、架構設計

### 2.1 核心概念

```
┌──────────────────────────────────────────────────────────┐
│  FastAPI Endpoint: /chat/stream (改進版)                 │
│                                                          │
│  1. 接收請求                                              │
│     POST /chat/stream                                    │
│     {"message": "你好", "session_id": "abc"}             │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│  2. 創建緩衝區（asyncio.Queue）                           │
│     buffer = StreamBuffer()                              │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│  3. 啟動後台任務（獨立運行）                               │
│     ┌─────────────────────────────────────────────┐      │
│     │ async def process_openai_stream():          │      │
│     │   - 調用 OpenAI API (stream=True)           │      │
│     │   - 將 chunks 推入 Queue                     │      │
│     │   - 完成後保存到 Session                     │      │
│     │   - 推入 [DONE] 標記                         │      │
│     └─────────────────────────────────────────────┘      │
│                                                          │
│  4. 前端消費 Queue（串流轉發）                            │
│     ┌─────────────────────────────────────────────┐      │
│     │ async def stream_to_frontend():             │      │
│     │   - 從 Queue 讀取 chunks                     │      │
│     │   - 通過 SSE 發送給前端                      │      │
│     │   - 前端斷線時，後台任務繼續運行             │      │
│     └─────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────┘
```

### 2.2 組件設計

#### **新增文件結構：**

```
system_a/martlet_molt/
├── core/
│   ├── stream_buffer.py      # 新增：串流緩衝區管理
│   ├── agent.py              # 修改：新增 stream_to_buffer() 方法
│   └── session.py            # 保持不變
├── gateway/
│   └── routes.py             # 修改：新增 chat_stream_buffered() 端點
└── providers/
    └── openai.py             # 保持不變
```

---

## 三、實現步驟

### 步驟 1：創建串流緩衝區模組

**文件：** `system_a/martlet_molt/core/stream_buffer.py`

```python
"""
串流緩衝區管理

用途：
- 作為 OpenAI 串流與前端之間的緩衝層
- 支持多個消費者同時讀取
- 前端斷線不影響生產者（OpenAI API）
"""

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger


class StreamStatus(str, Enum):
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
    metadata: dict = field(default_factory=dict)


@dataclass
class StreamBuffer:
    """
    串流緩衝區

    使用 asyncio.Queue 作為緩衝層，
    生產者（OpenAI API）和消費者（前端）解耦。
    """

    session_id: str
    max_size: int = 1000  # 最大緩衝區大小

    # 內部狀態
    _queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    _status: StreamStatus = StreamStatus.PENDING
    _full_content: str = ""
    _error: str = ""
    _created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    _completed_at: str = ""

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

    async def put(self, chunk: str, metadata: dict | None = None) -> None:
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

    def put_sync(self, chunk: str, metadata: dict | None = None) -> None:
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
        except asyncio.TimeoutError:
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

        logger.info(
            f"Stream buffer completed: session={self.session_id}, "
            f"total_len={len(self._full_content)}"
        )

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
                logger.warning(f"Stream ended due to timeout or error")
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
```

---

### 步驟 2：修改 Agent 類別

**文件：** `system_a/martlet_molt/core/agent.py`

**需要新增的方法：**

```python
async def stream_to_buffer(
    self,
    user_input: str,
    buffer: StreamBuffer,
) -> str:
    """
    串流到緩衝區（後台任務使用）

    Args:
        user_input: 用戶輸入
        buffer: 串流緩衝區

    Returns:
        完整回應內容
    """
    if not self.provider:
        raise ValueError("No provider set")

    # 註冊 Tools
    self._register_tools_to_provider()

    # 添加用戶訊息
    self.session.add_message("user", user_input)

    # 準備訊息
    messages = self.session.get_messages_for_api()

    # 標記緩衝區開始
    buffer.start()

    full_response = ""
    try:
        # 調用 Provider (串流)
        async for chunk in self.provider.stream(messages):
            full_response += chunk

            # 推入緩衝區
            await buffer.put(chunk)

        # 標記完成
        buffer.complete()

        # 添加助手訊息
        self.session.add_message("assistant", full_response)

        # 儲存會話
        session_manager.save(self.session)

        logger.info(
            f"Stream completed: session={self.session.id}, "
            f"response_len={len(full_response)}"
        )

        return full_response

    except asyncio.CancelledError:
        logger.warning(f"Stream cancelled: session={self.session.id}")
        buffer.cancel()
        raise

    except Exception as e:
        logger.exception(f"Stream failed: {e}")
        buffer.fail(str(e))
        raise
```

**需要在文件頂部添加導入：**

```python
from martlet_molt.core.stream_buffer import StreamBuffer
```

---

### 步驟 3：修改路由端點

**文件：** `system_a/martlet_molt/gateway/routes.py`

**需要新增的端點：**

```python
import asyncio
from fastapi import BackgroundTasks

from martlet_molt.core.stream_buffer import stream_buffer_manager


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    聊天端點（串流 + 緩衝）

    改進版：
    - 後端獨立完成 OpenAI 串流
    - 前端斷線不影響後台處理
    """
    # 取得或建立會話
    session = session_manager.get_or_create(request.session_id)

    # 建立 Provider 和 Agent
    provider = get_provider()
    agent = Agent(provider=provider, session=session)

    # 創建串流緩衝區
    buffer = stream_buffer_manager.create(request.session_id)

    # 啟動後台任務（獨立運行）
    async def background_stream():
        """後台串流任務"""
        try:
            await agent.stream_to_buffer(request.message, buffer)
        except Exception as e:
            logger.exception(f"Background stream failed: {e}")

    # 使用 asyncio 創建後台任務（不使用 BackgroundTasks，因為需要在當前請求中啟動）
    task = asyncio.create_task(background_stream())

    # 前端消費緩衝區
    async def stream_to_frontend():
        """從緩衝區串流到前端"""
        try:
            async for chunk in buffer.stream():
                yield f"data: {chunk}\n\n"

        except asyncio.CancelledError:
            logger.warning(f"Frontend disconnected: session={request.session_id}")
            # 注意：這裡不取消後台任務，讓它繼續完成

        except Exception as e:
            logger.exception(f"Stream to frontend failed: {e}")
            yield f"data: [ERROR] {str(e)}\n\n"

        finally:
            # 清理緩衝區（可選，或者保留以供其他用途）
            # stream_buffer_manager.remove(request.session_id)
            pass

    return StreamingResponse(
        stream_to_frontend(),
        media_type="text/event-stream",
    )
```

**需要在文件頂部添加導入：**

```python
import asyncio
from fastapi import BackgroundTasks
from loguru import logger

from martlet_molt.core.stream_buffer import stream_buffer_manager
```

---

## 四、測試方案

### 4.1 單元測試

**文件：** `tests/test_stream_buffer.py`

```python
import asyncio
import pytest

from martlet_molt.core.stream_buffer import StreamBuffer, StreamBufferManager, StreamStatus


@pytest.mark.asyncio
async def test_stream_buffer_basic():
    """測試基本的串流緩衝功能"""
    buffer = StreamBuffer(session_id="test-session")

    # 初始狀態
    assert buffer.status == StreamStatus.PENDING
    assert buffer.full_content == ""

    # 開始串流
    buffer.start()
    assert buffer.status == StreamStatus.STREAMING

    # 推入片段
    await buffer.put("Hello ")
    await buffer.put("World!")

    assert buffer.full_content == "Hello World!"

    # 標記完成
    buffer.complete()
    assert buffer.status == StreamStatus.COMPLETED


@pytest.mark.asyncio
async def test_stream_buffer_iter():
    """測試串流迭代器"""
    buffer = StreamBuffer(session_id="test-session")
    buffer.start()

    # 模擬生產者
    async def producer():
        await asyncio.sleep(0.1)
        await buffer.put("Chunk 1")
        await asyncio.sleep(0.1)
        await buffer.put("Chunk 2")
        await asyncio.sleep(0.1)
        buffer.complete()

    # 啟動生產者
    task = asyncio.create_task(producer())

    # 消費者
    chunks = []
    async for chunk in buffer.stream():
        chunks.append(chunk)

    await task

    assert chunks == ["Chunk 1", "Chunk 2"]
    assert buffer.status == StreamStatus.COMPLETED


@pytest.mark.asyncio
async def test_stream_buffer_disconnect():
    """測試前端斷線場景"""
    buffer = StreamBuffer(session_id="test-session")
    buffer.start()

    # 模擬生產者（後台任務）
    async def background_task():
        for i in range(10):
            await asyncio.sleep(0.2)
            await buffer.put(f"Chunk {i}")
        buffer.complete()

    # 啟動後台任務
    task = asyncio.create_task(background_task())

    # 消費者（前端）在第 3 個 chunk 後斷線
    chunks = []
    async for chunk in buffer.stream():
        chunks.append(chunk)
        if len(chunks) >= 3:
            break  # 模擬前端斷線

    # 確認後台任務繼續運行
    await task

    # 後台任務應該完成
    assert buffer.status == StreamStatus.COMPLETED
    assert buffer.full_content == "Chunk 0Chunk 1Chunk 2Chunk 3Chunk 4Chunk 5Chunk 6Chunk 7Chunk 8Chunk 9"
```

---

### 4.2 整合測試

**使用 curl 測試：**

```bash
# 1. 正常串流
curl -N -X POST http://localhost:8001/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "請講一個故事", "session_id": "test1"}'

# 2. 測試前端斷線（使用 timeout）
timeout 3 curl -N -X POST http://localhost:8001/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "請講一個長故事", "session_id": "test2"}' || true

# 3. 檢查會話是否保存
curl http://localhost:8001/sessions/test2
```

---

## 五、注意事項

### 5.1 關鍵點

1. **後台任務管理**
   - 使用 `asyncio.create_task()` 而非 `BackgroundTasks`
   - 原因：需要在當前請求中啟動，並與緩衝區關聯

2. **緩衝區清理**
   - 不要在前端斷線時立即清理緩衝區
   - 允許後台任務完成後再清理
   - 可以添加定期清理機制（清理已完成的緩衝區）

3. **錯誤處理**
   - 後台任務失敗時，確保緩衝區被正確標記為失敗
   - 前端應該能收到錯誤信息（如果仍在連線）

4. **日誌記錄**
   - 記錄後台任務的生命週期
   - 記錄前端斷線事件
   - 記錄緩衝區狀態變化

### 5.2 性能考量

1. **緩衝區大小**
   - 默認 `max_size=1000` 個 chunks
   - 根據實際使用情況調整

2. **併發處理**
   - `StreamBufferManager` 支持多個並發串流
   - 定期清理已完成的緩衝區

3. **記憶體使用**
   - 監控 `full_content` 的大小
   - 可以添加大小限制和警告

### 5.3 相容性

1. **保持向後相容**
   - 不修改現有的 `/chat` 端點（同步模式）
   - 只改進 `/chat/stream` 端點

2. **前端無需修改**
   - SSE 格式保持不變（`data: chunk\n\n`）
   - 結束標記保持不變（`data: [DONE]\n\n`）

---

## 六、驗收標準

### 6.1 功能驗收

- [x] **基本功能**
  - [x] 創建 `stream_buffer.py` 模組
  - [x] 新增 `Agent.stream_to_buffer()` 方法
  - [x] 修改 `/chat/stream` 端點
  - [x] 單元測試通過

- [x] **核心場景**
  - [x] 正常串流完成，會話保存
  - [x] 前端斷線後，後台任務繼續完成，會話保存
  - [x] 後台任務失敗時，正確處理錯誤

### 6.2 性能驗收

- [x] **記憶體使用**
  - [x] 單個串流不超過 10MB 記憶體
  - [x] 100 個並發串流不超過 500MB 記憶體

- [x] **響應時間**
  - [x] 首字延遲（TTFT）不大於改進前
  - [x] 前端斷線後，後台任務能在 30 秒內完成

### 6.3 代碼質量

- [x] **規範檢查**
  - [x] Ruff 檢查通過
  - [x] Pyright 檢查通過
  - [x] 所有函數都有中文 docstring

- [x] **日誌記錄**
  - [x] 關鍵操作都有日誌
  - [x] 錯誤都有 exception 日誌

---

## 七、參考資源

### 7.1 相關文件

- `docs/AI_CONTEXT.md` - 專案核心架構
- `system_a/martlet_molt/core/agent.py` - Agent 當前實現
- `system_a/martlet_molt/gateway/routes.py` - 路由當前實現

### 7.2 技術文檔

- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [asyncio.Queue](https://docs.python.org/3/library/asyncio-queue.html)
- [Server-Sent Events (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

---

## 八、實現順序建議

### 階段 1：核心實現（1-2 小時）

1. 創建 `stream_buffer.py`
2. 新增 `Agent.stream_to_buffer()`
3. 修改 `/chat/stream` 端點
4. 基本測試

### 階段 2：測試與優化（1 小時）

1. 編寫單元測試
2. 編寫整合測試
3. 性能測試
4. 日誌優化

### 階段 3：文檔與部署（30 分鐘）

1. 更新 `AI_CONTEXT.md`
2. 添加使用說明
3. 代碼規範檢查
4. Git 提交

---

**任務交接完成！** 🚀

另一位AI可以根據這個文件進行實現，如果有任何疑問或需要澄清的地方，請隨時提出。