# TASK-ORC-03: Orchestrator 流量代理層實作 (待啟動)

- **任務編號**: TASK-ORC-03
- **優先級**: 高
- **狀態**: ✅ 已完成 (2025-02-23)
- **建立日期**: 2025-02-23

## 🎯 目標
讓 Orchestrator (Port 8000) 成為系統的單一入口，實現真正的「零停機切換」。前端與外部 API 僅需對接 Port 8000，由 Orchestrator 根據當前活躍系統內部轉發流量。

## 📋 詳細規格
1.  **代理功能實作**:
    - 在 `orchestrator/main.py` 或新模組中整合極輕量級的 HTTP 反向代理。
    - 支援 WebSocket 流量轉發（確保 `/chat` 功能正常）。
2.  **狀態動態切換**:
    - 當執行 `switch` 指令時，代理目標應在毫秒級完成切換，不中斷長連接。

## ✅ 驗證方式
- [x] 在 `orchestrator/proxy.py` 中實作反向代理邏輯。
- [x] 在 `orchestrator/main.py` 中整合代理啟動與監控流程。
- [x] 通過單元測試驗證 HTTP 轉發與錯誤處理。
- [x] 存取 `http://localhost:8000` 即可自動導航至活躍系統。
