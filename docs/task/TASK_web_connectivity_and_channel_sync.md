# TASK-011: Web 前後端連通性修復與 WebSocket 遷移 (已完成 ✅)

## 1. 任務背景
在 Commit `b9af744` 中引入了新的 `BaseChannel` 架構與 `WebChannel` (WebSocket) 實作，但 `frontend/web-lite-v2` 當時仍使用舊有的 SSE (`/chat/stream`) 模式，且存在跨來源資源共用 (CORS) 限制與固定 IP 綁定問題，導致外部存取時連線失敗。

## 2. 已完成工作

### 階段一：連通性修復 (Commit: 766b5b3)
- **後端 CORS 解鎖**: 在 `backend/system_b/martlet_molt/gateway/server.py` 中加入了 `CORSMiddleware`。
- **前端連線性預檢**: 修正 `frontend/web-lite-v2/main.py`，啟動時會自動呼叫後端 `/health` 接口，確認後端服務狀態。
- **動態 URL 解析**: 修正 `chat.html` 中的 JavaScript，使其能根據瀏覽器網址列自動轉換 `backendUrl`，解決從非 localhost 環境存取時的 `Failed to fetch` 錯誤。
- **環境統一**: 將預設連線地址統一為 `127.0.0.1` 以確保開發環境的一致性。

### 階段二：WebSocket 協定遷移 ✅
- **後端 WebSocket 端點**: 在 `routes.py` 新增 `@router.websocket("/ws/{session_id}")` 路由
- **前端 WebSocket 連線**: 將 `chat.html` 的 `fetch POST` 改為 `WebSocket` 連線
- **串流處理**: 實作 WebSocket 串流接收與即時渲染
- **連線狀態 UI**: 新增連線狀態指示器（已連線/未連線）
- **自動重連機制**: 斷線後 3 秒自動重連

## 3. 技術實作詳情

### 後端 (routes.py)
```python
@router.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    # 建立 WebChannel
    channel = WebChannel(websocket, session_id)
    
    # 啟動 Channel
    await channel.start()
    
    # 訊息循環
    async for message in channel.receive():
        # 串流處理
        async for chunk in agent.stream(message.content):
            await channel.send(ChannelResponse(
                content=chunk,
                success=True,
                metadata={"type": "stream", "session_id": session_id}
            ))
        
        # 發送完成訊號
        await channel.send(ChannelResponse(
            content="",
            success=True,
            metadata={"type": "done"}
        ))
```

### 前端 (chat.html)
- **Alpine.js Store**: 使用全局 store 共享 WebSocket 連線狀態
- **WebSocket URL 轉換**: HTTP URL 自動轉換為 WebSocket URL
- **串流渲染**: 即時附加串流片段到訊息內容
- **狀態指示器**: 顯示「已連線」或「未連線」

## 4. 驗證方式
1. 啟動後端：`python backend/system_b/martlet_molt/main.py`
2. 啟動前端：`python frontend/web-lite-v2/main.py`
3. 瀏覽器開啟 `http://127.0.0.1:8002`
4. 確認連線狀態顯示「已連線」（綠色）
5. 發送訊息，確認串流回應正常顯示

---
**交接人**: MartletMolt AI Assistant
**完成日期**: 2025-02-22