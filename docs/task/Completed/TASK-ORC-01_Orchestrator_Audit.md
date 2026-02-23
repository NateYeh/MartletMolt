# TASK-ORC-01: Orchestrator 深度審計與 README 補完 (待啟動)

- **任務編號**: TASK-ORC-01
- **優先級**: 高
- **狀態**: ✅ 已完成 (2025-02-23)
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

## 🔍 審計發現 (Internal Audit Results)

1. **同步風險**: `switcher.py` 採用 `shutil.rmtree` 進行同步前的清理，會導致目標目錄非 Git 檔案遺失。
2. **進程孤兒化**: `manager.py` 未將 PID 持久化至磁碟，Orchestrator 重啟後會失去對 A/B 系統的控制。
3. **管道堵塞風險**: 子進程的 `stdout` 未被正確消耗，大量 Log 輸出可能導致子系統卡死。
4. **硬編碼配置**: `config.py` 中存在部分預設路徑與埠號的寫死現象。

## ✅ 驗證方式
- [x] 完成審計報告（已記錄於 README 與本文件）。
- [x] `orchestrator/README.md` 存在並包含架構說明。
- [x] 已將任務狀態更新為可交付。
