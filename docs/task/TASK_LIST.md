# MartletMolt 任務總覽

> **最後更新**：2025-02-22

---

## 📊 任務統計

| 類別 | 高優先級 | 中優先級 | 低優先級 | 總計 |
|------|---------|---------|---------|------|
| 後端 | 2 | 1 | 1 | 4 |
| Web UI | 1 | 0 | 1 | 2 |
| 通訊通道 | 1 | 0 | 0 | 1 |
| **總計** | **4** | **1** | **2** | **7** |

---

## 🔴 高優先級任務

### TASK-011: Web UI 遷移至 WebSocket (WebChannel)

| 項目 | 內容 |
|------|------|
| **位置** | `frontend/web-lite-v2/` & `backend/system_b/martlet_molt/gateway/` |
| **說明** | 將前後端通訊從 SSE 遷移至基於 Commit `b9af744` 的 WebSocket `WebChannel` |
| **影響** | 統一通訊架構，支援更複雜的雙向互動 |
| **預估工時** | 3-5 小時 |
| **狀態** | ⏳ 進行中 |

**待實作：**
- [x] 後端 CORS 與連通性修復 (Commit: 766b5b3)
- [x] 前端動態 URL 解析與預檢 (Commit: 766b5b3)
- [ ] 後端實作 WebSocket 路由並調用 `WebChannel`
- [ ] 前端從 `fetch` 遷移至 `WebSocket` 客戶端
- [ ] 介接 `ChannelMessage` / `ChannelResponse` 模型

**詳細規格：** [TASK_web_connectivity_and_channel_sync.md](./TASK_web_connectivity_and_channel_sync.md)

---

### TASK-001: Anthropic Provider 實作

| 項目 | 內容 |
|------|------|
| **位置** | `system_a/martlet_molt/providers/anthropic.py` |
| **說明** | 目前是空殼，有 3 個 `TODO: Implement` |
| **影響** | 無法使用 Claude 模型 |
| **預估工時** | 4-6 小時 |
| **狀態** | ❌ 未開始 |

**待實作方法：**
- `__init__()` - 初始化 Anthropic Client
- `chat()` - 同步對話
- `stream()` - 串流對話

---

### TASK-002: Tool 參數驗證

| 項目 | 內容 |
|------|------|
| **位置** | `system_a/martlet_molt/tools/base.py` |
| **說明** | `validate_parameters()` 只是 `return True`，未實際驗證 |
| **影響** | 可能傳入錯誤參數導致執行失敗 |
| **預估工時** | 2-3 小時 |
| **狀態** | ❌ 未開始 |

**待實作：**
- 使用 JSON Schema 驗證參數
- 返回詳細的驗證錯誤訊息

---

## 🟡 中優先級任務

### TASK-007: 單元測試補充

| 項目 | 內容 |
|------|------|
| **位置** | `tests/` |
| **說明** | 目前只有 `test_stream_buffer.py`，需要更多測試 |
| **預估工時** | 持續進行 |
| **狀態** | ⏳ 進行中 |

**待補充測試：**
- [ ] Provider 測試 (OpenAI, Anthropic, Ollama)
- [ ] Tool 測試
- [ ] Channel 測試
- [ ] Session 測試
- [ ] Agent 測試

---

## 🟢 低優先級任務

### TASK-WEB-ADV: Web Lite V2 進階功能整合

| 項目 | 內容 |
|------|------|
| **位置** | `frontend/web-lite-v2/` |
| **說明** | 會話管理、歷史記錄、文件上傳、Agent 設定、工具管理整合任務 |
| **預估工時** | 8-12 小時 |
| **狀態** | 📄 已規劃 |

**包含任務：**
- 會話管理系統（多會話列表、切換、刪除）
- 歷史記錄功能（持久化、載入、搜索）
- 文件上傳功能
- Agent 設定介面
- 工具管理面板

**詳細規格：** [TASK_web_lite_v2_advanced_features.md](./TASK_web_lite_v2_advanced_features.md)

---

### TASK-008: Skills 系統

| 項目 | 內容 |
|------|------|
| **位置** | `system_a/martlet_molt/skills/` |
| **說明** | 動態學習技能模組，讓 AI 能創建可重用技能 |
| **預估工時** | 2-3 天 |
| **狀態** | 📄 已規劃 |

**詳細規格：** [skills_plan.md](../skills_plan.md)

---

## 📁 已完成任務

| 任務 | 完成日期 | 說明 |
|------|---------|------|
| BaseChannel 抽象類 | 2025-02-22 | Channels 模組化架構 |
| CLIChannel 實作 | 2025-02-22 | 命令行互動通道 |
| WebChannel 實作 | 2025-02-22 | WebSocket 通訊通道 |
| Web UI 連通性修復 | 2025-02-22 | CORS, Pre-check, Dynamic URL |
| Web UI 串流響應 (SSE) | 2025-02-22 | 實現打字機效果顯示 AI 回應 |
| System A/B 同步工具 | 2025-02-22 | `make sync-a-to-b` / `make sync-b-to-a` |
| 串流緩衝架構 | 2025-02-22 | 後端獨立串流處理 |
| Web Lite V2 核心功能 | 2025-02-22 | LobeHub 風格 UI、聊天介面、主題切換、SSE 串流 |

---

## 🔄 任務狀態說明

| 狀態 | 符號 | 說明 |
|------|------|------|
| 未開始 | ❌ | 尚未開始實作 |
| 進行中 | ⏳ | 正在實作 |
| 已完成 | ✅ | 實作完成 |
| 已規劃 | 📄 | 有詳細規格書 |
| 暫停 | ⏸️ | 暫時擱置 |

---

## 📝 任務新增指南

新增任務時，請依以下格式建立檔案：

```
docs/task/TASK_XXX_任務名稱.md
```

---

*此文件由 MartletMolt AI 自動生成並維護*
