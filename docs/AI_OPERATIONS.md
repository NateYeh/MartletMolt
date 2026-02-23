# 🤖 MartletMolt AI 操作快捷指南 (AI Operations Index)

> **目的**：作為 AI Agent 的「高頻操作索引」，確保 AI 在 3 次 Tool Calls 內定位到具體實作細節，避免 `PROJECT_MAP.md` 過於冗長。

---

## 🚀 1. 服務啟動與管理 (Service Startup)
當用戶詢問「如何啟動服務」、「後台運行狀態」或「查看日誌」時：

- **正式/守護模式 (Production/Daemon)**:
    - 檔案路徑: `scripts/start_services.sh`
    - 技術細節: 使用 `screen` 管理 `martlet-orc` (8000) 與 `martlet-web` (8002)。
- **開發模式 (Local Development)**:
    - 檔案路徑: `Makefile`
    - 指令: `make dev`, `make dev-backend`, `make dev-frontend`
- **CLI 互動模式**:
    - 檔案路徑: `martlet.py`
    - 指令: `python martlet.py chat`

---

## 🔄 2. 系統進化與 A/B 切換 (Evolution & Switching)
當涉及「系統升級」、「切換 A/B 環境」或「同步代碼」時：

- **進化流程 (Evolve)**:
    - 檔案路徑: `orchestrator/README.md`
    - 指令: `orchestrator evolve <system>`
- **手動同步 (Sync)**:
    - 檔案路徑: `scripts/sync_systems.py` (或透過 `Makefile` 的 `make sync-*`)
- **健康檢查概念**:
    - 檔案路徑: `orchestrator/health_check.py`

---

## 📋 3. 任務與日常開發 (Task & Dev Workflow)
當涉及「新增功能」、「建立任務」或「代碼品質」時：

- **任務管理 SOP**:
    - 檔案路徑: `docs/task/SOP.md`
    - 包含: 建立規格書、更新 `TASK_LIST.md`、完成後的 Git Push 流程。
- **程式碼規範**:
    - 檔案路徑: `pyproject.toml` (Ruff/Pyright 配置)
    - 指令: `make lint`, `make format`

---

## 📂 4. 配置與環境 (Config & Env)
當涉及「API Key」、「模型切換」或「環境路徑」時：

- **系統配置**: `Config/settings.yaml` (不入 Git)
- **配置模板**: `config_templates/settings.example.yaml`
- **路徑定義**: `PROJECT_MAP.md`

---

*“看到索引，鎖定目標，精準實作。”*
