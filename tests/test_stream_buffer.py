"""
串流緩衝區測試

測試 StreamBuffer 和 StreamBufferManager 的功能。
"""

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
            await asyncio.sleep(0.05)
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
    assert "Chunk 0" in buffer.full_content
    assert "Chunk 9" in buffer.full_content


@pytest.mark.asyncio
async def test_stream_buffer_timeout():
    """測試超時場景"""
    buffer = StreamBuffer(session_id="test-session")
    buffer.start()

    # 不推入任何資料，測試 get 超時
    chunk = await buffer.get(timeout=0.5)
    assert chunk is None


@pytest.mark.asyncio
async def test_stream_buffer_fail():
    """測試失敗場景"""
    buffer = StreamBuffer(session_id="test-session")
    buffer.start()

    # 標記失敗（不推入任何資料）
    buffer.fail("Test error")

    assert buffer.status == StreamStatus.FAILED
    assert buffer.error == "Test error"

    # 讀取應該收到錯誤標記
    chunk = await buffer.get(timeout=1.0)
    assert chunk is not None
    assert "[ERROR]" in chunk.content


@pytest.mark.asyncio
async def test_stream_buffer_cancel():
    """測試取消場景"""
    buffer = StreamBuffer(session_id="test-session")
    buffer.start()

    # 推入一些資料
    await buffer.put("Some content")

    # 取消
    buffer.cancel()

    assert buffer.status == StreamStatus.CANCELLED


def test_stream_buffer_manager_create():
    """測試緩衝區管理器創建"""
    manager = StreamBufferManager()

    buffer = manager.create("session-1")
    assert buffer.session_id == "session-1"
    assert buffer.status == StreamStatus.PENDING

    # 取得緩衝區
    retrieved = manager.get("session-1")
    assert retrieved is buffer


def test_stream_buffer_manager_remove():
    """測試緩衝區管理器移除"""
    manager = StreamBufferManager()

    manager.create("session-1")
    assert manager.get("session-1") is not None

    # 移除
    result = manager.remove("session-1")
    assert result is True
    assert manager.get("session-1") is None

    # 移除不存在的
    result = manager.remove("non-existent")
    assert result is False


def test_stream_buffer_manager_max_buffers():
    """測試緩衝區管理器最大數量限制"""
    manager = StreamBufferManager(max_buffers=3)

    # 創建 3 個緩衝區
    manager.create("session-1")
    manager.create("session-2")
    manager.create("session-3")

    # 標記前兩個為完成
    manager.get("session-1").complete()
    manager.get("session-2").complete()

    # 創建第 4 個，應該觸發清理
    manager.create("session-4")

    # session-1 和 session-2 應該被清理
    assert manager.get("session-1") is None
    assert manager.get("session-2") is None
    assert manager.get("session-3") is not None
    assert manager.get("session-4") is not None


def test_stream_buffer_to_dict():
    """測試序列化"""
    buffer = StreamBuffer(session_id="test-session")
    buffer.start()
    buffer.complete()

    data = buffer.to_dict()

    assert data["session_id"] == "test-session"
    assert data["status"] == "completed"
    assert "created_at" in data
    assert "completed_at" in data


@pytest.mark.asyncio
async def test_stream_buffer_put_sync():
    """測試同步推入"""
    buffer = StreamBuffer(session_id="test-session")
    buffer.start()

    # 同步推入
    buffer.put_sync("Hello ")
    buffer.put_sync("World!")

    assert buffer.full_content == "Hello World!"

    # 非同步讀取
    chunk1 = await buffer.get(timeout=1.0)
    chunk2 = await buffer.get(timeout=1.0)

    assert chunk1 is not None
    assert chunk2 is not None
    assert chunk1.content == "Hello "
    assert chunk2.content == "World!"
