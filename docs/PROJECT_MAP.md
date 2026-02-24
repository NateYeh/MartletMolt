# PROJECT_MAP.md — MartletMolt 專案地圖 (V3.0 - 容器进化版)

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

- **技術棧**：Python 3.11+ / FastAPI / Playwright / Docker (DooD 模式)
- **核心能力**：網頁自動化、Shell 執行、程式碼自我重寫、A/B 系統熱切換。

---

## 🏗️ 系統運作架構 (V3.0 Deployment)

- **主入口 (Orchestrator)**：`Port 8000` (負責流量調度、監控與容器管理)。
- **活性系統 (System A)**：`Port 8001` (當前對外服務實體)。
- **影子系統 (System B)**：`Port 8002` (進化實驗室/測試路徑)。
- **宿主機 IP**: `192.168.77.140`

---

## 🗺️ 關鍵目錄與開發場景 (Developer Guide)

| 路徑 | 角色定位 | AI 修改權限 | 鏡像映射 / 備註 |
|:--- |:--- |:--- |:--- |
| `orchestrator/` | **系統流量分發** | ✅ 可修改 | `/app` in Orchestrator。非必要不修改。 |
| `backend/system_{a|b}/martlet_molt/core/` | **系統大腦** | ✅ 可修改 | 修改 Agent 決策邏輯、Session 儲存、環境配置。 |
| `backend/system_{a|b}/martlet_molt/tools/` | **Agent 工具箱** | ✅ 可修改 | **功能核心**。當你想賦予 Agent 新能力時。 |
| `backend/system_{a|b}/martlet_molt/gateway/` | **API 門戶** | ✅ 可修改 | 修改 REST API 端點、WebSocket 傳輸邏輯。 |
| `shared/` | **數據生命線** | ✅ 可修改 | `/app/shared`。存儲資料庫、Session、Logs，A/B 共享。 |
| `skills/` | **擴展技能中心** | ✅ 可修改 | 存放所有動態加載的 Python/Markdown 技能目錄。 |
| `Config/` | **運行配置** | ✅ 可修改 | 調整 API Key 或系統參數（不加入 Git 控制）。 |
| `docs/AI_OPERATIONS.md` | **AI 操作捷徑** | ✅ 可修改 | **AI 必讀**。收錄切換、重啟、任務管理指令。 |

---

## 🔄 進化與切換流程 (Evolution Loop)

1.  **觸發優化**：AI 辨識模組缺陷或收到優化請求。
2.  **手術修改**：AI 修改當前**非活躍系統 (Inactive System)**（例如從 A 修改 B 的映射路徑 `/mnt/evolution/b`）。
3.  **重啟驗證**：透過 Orchestrator 重啟非活躍系統並進行健康檢查。
4.  **流量切換**：驗證通過後，Orchestrator 將流量導向新系統，舊系統進入待命。
5.  **環境對齊**：歸檔進化成果 (Git Push)。

---

## 🛡️ 安全與命名規範

- **安全約束**：嚴禁修改 `orchestrator.py` 的基礎代理邏輯，除非獲得明確授權。
- **命名約定**：
  - 類別：`PascalCase`
  - 函式/變數：`snake_case`
- **錯誤處理**：統一使用 `loguru`，Exception 必須包含完整堆疊。
- **禁絕 Hardcoding**：嚴禁硬編碼敏感資訊、環境變數或絕對路徑，應統一由 `Config/` 管理。

---

**Last Updated**: 2024-02-24
**Guardian Status**: Docker-Enabled / GPU-Linked / A-B Live
