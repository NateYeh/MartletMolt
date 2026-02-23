# TASK-CORE-009: 後端緊急恢復與 UI 體驗補完 (已完成 ✅)

## 📋 任務資訊
- **ID**: TASK-CORE-009
- **負責人**: MartletMolt AI
- **建立日期**: 2025-02-23
- **完成日期**: 2025-02-23
- **狀態**: ✅ 已完成 (Completed)

## 🎯 目標
1. **緊急修復 (Recovery)**: 修正 `core/agent.py` 中的語法錯誤 (SyntaxError)，使後端服務恢復正常。
2. **會話管理補完 (Session Polish)**:
    - 實作「新對話」按鈕生成唯一 ID 的邏輯。
    - 實作「自動生成標題」功能，在第一輪對話後更新會話元數據。
3. **體驗優化 (UX)**: 前端 UI 頂部標題與 Session ID 動態同步。

## 🛠️ 實作細節
### 1. 後端修復 (Backend)
- **檔案**: `backend/system_a/martlet_molt/core/agent.py`
- **動作**: 
    - 修正 `stream_to_buffer` 結尾的 `try-finally` 縮排。
    - 確保 `_generate_session_title` 方法獨立且正確定義在 `Agent` 類別下。
    - 使用 `asyncio.create_task` 觸發標題總結，避免阻塞回應。

### 2. 前端修復 (Frontend)
- **檔案**: `frontend/web-lite-v2/templates/components/sidebar.html`
    - 更新 `createNewChat()` 函數生成隨機 ID。
- **檔案**: `frontend/web-lite-v2/templates/chat.html`
    - 綁定 `sessionMetadata.title` 到頁面標題。
    - 確保 `fetchHistory` 會更新 `sessionMetadata`。

## ✅ 驗證清單
- [x] 後端啟動無語法錯誤
- [x] Orchestrator 成功代理流量 (8000 -> 8001/8002)
- [x] 歷史紀錄列表能看到自動生成的標題
- [x] Ruff 格式檢查通過

## 歷史記錄
- 2025-02-23: 任務啟動，確立修復路徑。
- 2025-02-23: 修復 agent.py 語法與標題生成邏輯，更新前端 UI 同步，任務完成。
