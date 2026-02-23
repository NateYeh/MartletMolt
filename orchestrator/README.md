# 🛡️ MartletMolt Orchestrator (守護者)

Orchestrator 是 MartletMolt 的核心控制塔，負責管理 A/B 雙系統的生命週期、健康監控、以及關鍵的「進化切換」邏輯。

## 🏗️ 核心架構

Orchestrator 獨立於業務邏輯之外，透過 `subprocess` 管理兩個對等的工作系統：
- **System A**: 位於 `backend/system_a/` (預設 Port: 8001)
- **System B**: 位於 `backend/system_b/` (預設 Port: 8002)

## 🔄 A/B 進化工作流 (Evolution Workflow)

1. **離線修改**: 開發者或 AI 對目前「非活躍」的系統進行程式碼修改。
2. **觸發進化**: 透過指令 `orchestrator evolve <system>` 啟動流程。
3. **健康驗證**: Orchestrator 啟動目標系統，並連續執行多輪 `/health` 檢查。
4. **熱切換**: 驗證通過後，將 `Active` 狀態指針切換至新系統，並停止舊系統。
5. **環境對齊**: 將新系統的變更同步至備份系統，確保下次進化的基準是一致的。

## 🛠️ 常用指令

```bash
# 啟動 Orchestrator 並監控活躍系統
orchestrator start --daemon

# 檢查所有系統狀態
orchestrator status

# 手動切換活躍系統
orchestrator switch <a|b>

# 執行進化切換（包含啟動、檢查、切換、同步）
orchestrator evolve <system>
```

## ⚠️ 已知限制 (Current Limitations)

- **狀態遺失**: 當前進程管理 (PID) 僅存於記憶體。若 Orchestrator 重啟，會失去對子系統的跟蹤。
- **同步風險**: 目標同步採用全刪全建模型。請勿在 `system_a/b` 目錄下存放重要的非 Git 追蹤檔案 (如 `.env`, `.venv`)。
- **日誌阻塞**: 目前未排空子進程輸出管道，高頻率日誌輸出可能導致系統掛起。

## 📁 目錄結構

- `main.py`: 命令列接口 (CLI) 與守護入口。
- `manager.py`: 進程生命週期管理。
- `switcher.py`: A/B 切換與進化邏輯實作。
- `state.py`: 系統持久化狀態 (Active/Version) 管理。
- `config.py`: 配置定義。
- `sync.py`: 程式碼同步邏輯。
