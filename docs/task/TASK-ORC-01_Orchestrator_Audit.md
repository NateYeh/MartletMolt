# TASK-ORC-01: Orchestrator 深度審計與 README 補完 (待啟動)

- **任務編號**: TASK-ORC-01
- **優先級**: 高
- **狀態**: Pending 📄
- **建立日期**: 2025-02-23

## 🎯 目標
在進行大規模代碼重構前，對現有 `orchestrator/` 目錄進行完整的架構審計，找出與當前 A/B 進化需求不符的邏輯，並撰寫一份詳細的維護說明文檔。

## 📋 詳細規格
1.  **代碼審計**:
    - 檢查 `switcher.py` 的切換安全性（鎖定機制）。
    - 檢查 `manager.py` 對於進程存活的判斷機制。
    - 找出所有硬編碼的路徑與埠號。
2.  **文檔撰寫**:
    - 建立 `orchestrator/README.md`。
    - 定義 A/B 系統切換的預期工作流。
    - 列出當前版本的已知限制（Known Limitations）。

## ✅ 驗證方式
- [ ] 完成審計報告（記錄於本文件或 README）。
- [ ] `orchestrator/README.md` 存在並包含架構說明。
