# TASK-WEB-FIX-001: 遠端存取 WebSocket 連線失敗修復 🚨

- **任務編號**: TASK-WEB-FIX-001
- **優先級**: P0 (阻斷性 Bug)
- **狀態**: ⏳ Active Sprint (進行中)
- **建立日期**: 2025-02-23

## 🧩 問題描述
當用戶透過遠端 IP (如 `192.168.77.140`) 存取前端網頁時，儘管 Web UI 顯示的後端地址已正確修正，但 WebSocket 連線依然維持「未連線」狀態，導致訊息無法發送且提示「無法連線至伺服器」。

## 🔍 現狀分析 (Audit Findings)
1. **IP 修正已生效**: 前端 `main.py` 已能動態注入正確的 Host IP (不再是 127.0.0.1)。
2. **WebSocket 斷點**: 連線指示器顯示紅色，代表 `new WebSocket(wsUrl)` 握手失敗。
3. **可能原因**:
    - **Orchestrator Proxy 轉發問題**: `orchestrator/proxy.py` 中的 WebSocket 代理邏輯可能未正確處理特定的路徑轉發或 Header。
    - **CORS/Security Policy**: 瀏覽器可能封鎖了不同埠號間的 WebSocket 握手。
    - **JS 初始化順序**: `chat.html` 中的 `connectWebSocket` 可能在 `backendUrl` 尚未完全注入或校正前就已觸發。

## 📋 待辦事項 (Todo List)
1. [ ] **Proxy 日誌審計**: 檢查 `martlet-orc` 的日誌，確認是否有收到來自遠端 IP 的 WS 請求。
2. [ ] **路徑校驗**: 檢查 `orchestrator/proxy.py` 的 `proxy_websocket` 裝飾器路徑匹配是否包含 `/ws/{session_id}`。
3. [ ] **JS 強化**: 在 `chat.html` 增加連線失敗的具體錯誤捕捉 (Error Event Details)，並確保連線前 URL 是最終校正後的版本。
4. [ ] **Orchestrator 接收端檢查**: 確認 Orchestrator 的 `uvicorn` 是否允許來自非 localhost 的連線請求（目前的代理層）。

## ✅ 驗證方式
- 前端連線指示器變為 **綠色「已連線」**。
- 遠端存取時能正常進行對話且接收串流響應。
