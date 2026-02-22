# 任務交接：Web 前後端連通性修復與 WebSocket 遷移準備

## 1. 任務背景
在 Commit `b9af744` 中引入了新的 `BaseChannel` 架構與 `WebChannel` (WebSocket) 實作，但 `frontend/web-lite-v2` 當時仍使用舊有的 SSE (`/chat/stream`) 模式，且存在跨來源資源共用 (CORS) 限制與固定 IP 綁定問題，導致外部存取時連線失敗。

## 2. 已完成工作 (Commit: 766b5b3)
- **後端 CORS 解鎖**: 在 `backend/system_b/martlet_molt/gateway/server.py` 中加入了 `CORSMiddleware`。
- **前端連線性預檢**: 修正 `frontend/web-lite-v2/main.py`，啟動時會自動呼叫後端 `/health` 接口，確認後端服務狀態。
- **動態 URL 解析**: 修正 `chat.html` 中的 JavaScript，使其能根據瀏覽器網址列自動轉換 `backendUrl`，解決從非 localhost 環境存取時的 `Failed to fetch` 錯誤。
- **環境統一**: 將預設連線地址統一為 `127.0.0.1` 以確保開發環境的一致性。

## 3. 待執行任務 (後續交接路徑)
本階段僅解決了「連通性」問題，尚未將通訊協定升級至 WebSocket。接手的 AI 應執行以下步驟：

### A. 實作 WebSocket GateWay 入口
- 在 `backend/system_b/martlet_molt/gateway/routes.py` 或 `server.py` 中新增一個 `@app.websocket("/ws/{session_id}")` 路由。
- 該路由應實例化 `martlet_molt.channels.web.WebChannel`。

### B. 前端協定遷移
- 修改 `frontend/web-lite-v2/templates/chat.html` 中的 `sendMessage()` 方法。
- 由現有的 `fetch(..., {method: 'POST'})` 遷移至 `new WebSocket(...)`。
- 對接 `WebChannel` 定義的 `ChannelMessage` 與 `ChannelResponse` JSON 格式。

### C. 狀態同步
- 確保前端 UI 能夠顯示 WebSocket 的連線狀態（連線中、已連線、已斷開）。

## 4. 驗證方式
1. 啟動後端：`python backend/system_b/martlet_molt/main.py`
2. 啟動前端：`python frontend/web-lite-v2/main.py`
3. 外部存取：使用其他裝置連線至伺服器 IP:8002，確認聊天功能運作正常。

---
**交接人**: MartletMolt AI Assistant
**日期**: 2026-02-22
