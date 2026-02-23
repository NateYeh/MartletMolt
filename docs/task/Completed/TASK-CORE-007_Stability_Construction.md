# TASK-CORE-007: 穩定性建設 (Unit Tests) ⏳

## 🎯 任務目標
建立 MartletMolt 的核心測試體系，確保系統在進行「自我進化」或程式碼重寫時，具備自動化的驗證機制以防止功能倒退 (Regression)。

## 📝 詳細規格

### 1. 測試框架選擇
- **工具**: `pytest`, `pytest-asyncio`
- **Mocking**: `unittest.mock` 或 `pytest-mock` (用於模擬 LLM API 調用)
- **API 測試**: `httpx` (FastAPI TestClient)

### 2. 測試覆蓋重點 (優先級)
- **P0: 核心邏輯 (Core)**
    - `session.py`: 會話建立、存儲、歷史記錄清理、Token 計數。
    - `stream_buffer.py`: 串流數據的正確緩衝與拼接。
    - `config.py`: 環境變數讀取與預設值驗證。
- **P1: 提供者接口 (Providers)**
    - `ollama.py` / `openai.py`: 模擬 API 響應，驗證數據格式轉換 (LLM Output -> Internal Message)。
- **P2: 閘道器 API (Gateway)**
    - `routes.py`: 驗證 `/chat` 端點是否能正確接收並轉發請求。
    - `websocket.py`: 驗證 WebSocket 連線握手與基本通訊。
- **P3: 基礎工具 (Tools)**
    - `shell.py`: 驗證命令執行與錯誤捕獲。
    - `file_read.py` / `file_write.py`: 驗證檔案讀寫權限與路徑安全。

## 📍 修改路徑清單
- `/tests/` (新增各模組測試文件)
- `backend/system_a/martlet_molt/` (可能需調整代碼以提高可測試性/依賴注入)

## ✅ 驗證方式
1. 執行 `pytest` 總覆蓋率提升至 60% 以上。
2. 所有測試案例通過且無 Side Effect。

---
**狀態**: ✅ 已完成  
**負責人**: Martlet Guardian (AI)  
**完成日期**: 2025-02-23 (累計測試案例: 52 項)
