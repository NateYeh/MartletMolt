# TASK-ARCH-003: 整合 A/B 進化循環 (The Evolution Loop)

## 1. 目標
重構 Orchestrator，使其能引導 A/B 系統在沙盒環境中進行進化、測試與切換。

## 2. 詳細規格
- **進化流程自動化**:
  - 當接收到進化請求時，Orchestrator 複製程式碼並啟動一個「臨時測試沙盒」。
  - 在臨時沙盒中執行全套 `pytest` 測試集。
- **動態更新機制**:
  - 測試通過後，Orchestrator 更新 Sandbox 映像檔或重新啟動 Sandbox 容器。
  - 確保切換過程對前端 UI 透明 (Zero-Downtime)。
- **回滾機制 (Rollback)**:
  - 若新版 Sandbox 啟動失敗或健康檢查未通過，自動回滾至上一版的 Docker Image。

## 3. 修改路徑清單 (預計)
- `orchestrator/main.py` (新增 Docker 控制邏輯)
- `orchestrator/evolution_manager.py` (修改進化流程)
- `scripts/health_check.py` (更新為 Sandbox 檢查)

## 4. 驗證方式
- 手動觸發一次進化請求，觀察測試沙盒的建立、測試與銷毀流程。
- 故意注入錯誤程式碼，驗證 Orchestrator 能正確攔截並防止錯誤進入正式版。

---
**狀態**: 📋 待啟動 (Planned)
**建立日期**: 2025-02-23
