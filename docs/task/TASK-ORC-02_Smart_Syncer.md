# TASK-ORC-02: 強化同步機制 (Smart Syncer Implementation) (待啟動)

- **任務編號**: TASK-ORC-02
- **優先級**: 中
- **狀態**: Pending 📄
- **建立日期**: 2025-02-23

## 🎯 目標
將目前 `orchestrator/switcher.py` 中極其暴力的「全刪全建」同步邏輯，升級為更智能、更安全的增量同步機制，確保開發環境中的私有檔案（如 `.git`, `.venv`, `.env`）不會被誤刪。

## 📋 詳細規格
1.  **邏輯改造**:
    - 替換 `shutil.rmtree`，改用基於 `filecmp` 或增量寫入的邏輯。
    - 支援從 `config.yaml` 讀取 `exclude_patterns`。
2.  **安全性提升**:
    - 在同步前執行路徑合法性檢查，防止目錄穿越。
    - 增加「模擬執行 (Dry Run)」模式。

## ✅ 驗證方式
- [ ] 執行 `orchestrator sync` 後，目標目錄的 `.git` 或 `.env` 依然存在。
- [ ] 程式碼修改能正確從 System A 同步至 System B。
- [ ] 通過 `ruff` 與 `pyright` 檢查。
