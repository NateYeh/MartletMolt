# TASK-ARCH-001: 建立主從通訊橋樑 (The Bridge)

## 1. 目標
實作 Host (Master) 與 Sandbox (Worker) 之間的輕量通訊協議與 LLM 請求代理，確保 Sandbox 環境內完全無 API Key。

## 2. 詳細規格
- **協議選型**: 採用內部 REST API (FastAPI) 進行跨容器通訊。
- **Host 代理端點**:
  - `POST /proxy/v1/chat/completions`: 接收 Sandbox 轉發的請求，注入 `Authorization` Header 後發送至 LLM 供應商。
  - `POST /proxy/v1/tools/execute`: 安全審核並執行特定工具請求（部分敏感工具）。
  - **WebSocket 密鑰注入**: 負責在 Sandbox 嘗試與外部裝置通訊時，自動從 Host 端注入 `X-Device-Key`，確保 Sandbox 無需持有全域金鑰。
- **Sandbox 路由改造**:
  - 將 `core/providers` 中的請求網址導向 Host 提供的代理位址。
  - 確保 Sandbox 啟動時不再從環境變數讀取任何 API Keys。

## 3. 修改路徑清單 (預計)
- `backend/system_{a|b}/martlet_molt/gateway/host_proxy.py` (新增)
- `backend/system_{a|b}/martlet_molt/providers/base_provider.py` (修改代理邏輯)
- `Config/config.yaml` (新增內部通訊位址設定)

## 4. 驗證方式
- 在 Sandbox 容器中嘗試訪問 `env` 命令，確認無 API Keys。
- 發送一次對話請求，確認請求能正確透過 Host 代理並獲得回應。
- 檢查 Host 日誌，確保 API Key 注入過程正確。

---
**狀態**: 📋 待啟動 (Planned)
**建立日期**: 2025-02-23
