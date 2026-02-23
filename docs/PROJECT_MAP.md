# PROJECT_MAP.md — MartletMolt 專案地圖

> 目的：提供專案高階架構與路徑引導，讓 AI 快速定位修改目標而不消耗過多 Token。

---

## 🛠️ 文檔維護準則 (Maintenance Guidelines) —— **必讀**

1.  **同步更新**：當目錄結構發生變更（新增、改名、刪除目錄）時，**必須優先更新**此文件的 `關鍵目錄與開發場景` 列表。
2.  **嚴禁代碼灌水**：禁止在本文件中貼入具體的類別 (Class) 或函式 (Function) 實作原始碼。應以「功能描述 + 檔案路徑」代替。
3.  **單一事實來源**：具體實作邏輯、參數說明應寫在該模組的 `Docstring` 或該目錄下的 `README.md`。此文件僅保留「導航」功能。
4.  **開發場景導向**：更新目錄說明時，必須註明「開發者在什麼情況下應進入該目錄」。

---

## 🚀 專案概述
**MartletMolt** 是一個自我進化的 AI Agent 系統。其核心價值在於透過 **A/B 雙系統切換** 實現「邊執行、邊優化」的零停機自我進化流程。

- **技術棧**：Python 3.11+ / FastAPI / Playwright / LobeHub 風格前端 (Jinja2)
- **核心能力**：網頁自動化、Shell 執行、程式碼自我重寫、健康狀態監控。

---

## 🗺️ 關鍵目錄與開發場景 (Developer Guide)

> **註註**：`system_x` 為佔位符，實際路徑依 A/B 環境而定（例如 `backend/system_a/...` 或 `backend/system_b/...`）。開發時應針對當前非活躍系統進行修改。

| 路徑 | 角色定位 | 開發者/AI 何時該來這裡？ | AI 修改權限 |
|:--- |:--- |:--- |:--- |
| `backend/system_{a|b}/martlet_molt/core/` | **系統大腦** | 修改 Agent 決策邏輯、Session 儲存、環境配置讀取。 | ✅ 可修改 |
| `backend/system_{a|b}/martlet_molt/tools/` | **Agent 工具箱** | **功能核心**。當你想賦予 Agent 新能力（如對接新 API、新檔案處理等）。 | ✅ 可修改 |
| `backend/system_{a|b}/martlet_molt/providers/` | **LLM 接口層** | 切換模型供應商或調整模型呼叫參數（如溫度、Max Tokens）。 | ✅ 可修改 |
| `backend/system_{a|b}/martlet_molt/gateway/` | **API 門戶** | 修改 REST API 端點、WebSocket 傳輸邏輯。 | ✅ 可修改 |
| `orchestrator/` | **守護程序 (Guardian)** | 涉及 A/B 切換邏輯、系統同步、部署自動化時。 | ❌ **限人手動** |
| `frontend/web-lite-v2/` | **介面層** | 修改聊天 UI、前端元件、Jinja2 模板或靜態資源。 | ✅ 可修改 |
| `scripts/` | **基礎設施腳本** | 用於服務啟動、System A/B 同步及底層維護。 | ✅ 可修改 |
| `skills/` | **擴展技能中心** | **Agent 的演化靈魂**。存放所有動態加載的 Python/Markdown 技能目錄。 | ✅ 可修改 |
| `Config/` | **運行配置** | 調整執行中的 API Key 或系統參數（不加入 Git 控制）。 | ✅ 可修改 |
| `docs/` | **文件核心** | 查閱開發規範、API 文件及 **[外部裝置連線指南](EXTERNAL_DEVICE_CONNECTION.md)**。 | ✅ 可修改 |
| `docs/AI_OPERATIONS.md` | **AI 操作捷徑** | **AI 必讀**。收錄啟動、切換、任務管理等高頻操作的原始碼路徑索引。 | ✅ 可修改 |

---

## 🏗️ 系統運作架構

1.  **Orchestrator (Port 8000+)**：根基，管理 A/B 系統狀態，負責流量導向與監控。
2.  **API Server (Port 8001)**：活動後端，負責 `/chat` 請求，驅動 Agent 思考與 Tool 調用。
3.  **Frontend (Port 8002)**：輕量 UI，透過 API 與後端通訊。

---

## 🔄 進化與切換流程 (Evolution Loop)

1.  **觸發優化**：AI 辨識模組缺陷或收到優化請求。
2.  **離線修改**：修改當前**非活躍系統 (Inactive System)** 的原始碼。
3.  **健康驗證**：Orchestrator 啟動非活躍系統並進行自動化測試（Health Check）。
4.  **流量切換**：驗證通過後，Orchestrator 將流量導向新系統，舊系統停止。
5.  **環境對齊**：將變更同步回備份，確保下次進化的起點是最新的。

---

## 🛡️ 安全與命名規範

- **安全約束**：嚴禁 AI 修改 `orchestrator/` 目錄，任何更動必須徵詢人類。
- **命名約定**：
  - 類別：`PascalCase`
  - 函式/變數：`snake_case`
  - 工具命名：`web_*.py`, `file_*.py`
- **錯誤處理**：統一使用 `loguru`，Exception 必須包含完整堆疊。
- **禁絕 Hardcoding**：嚴禁硬編碼敏感資訊（如 Key）、環境變數或絕對路徑，應統一由 `Config/` 管理。

---

## 🛠️ 開發常用命令

- `make dev`：啟動全套環境（A/B 後端 + 前端）。
- `martlet chat`：進入互動式 CLI 測試 Agent 能力。
- `pytest`：執行系統核心測試。

---

**注意**：特定模組的實作細節，請查閱原始碼檔案內的 `Docstring`。
