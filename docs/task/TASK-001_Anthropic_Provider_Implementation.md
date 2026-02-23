# TASK-001: Anthropic Provider 實作 (待啟動 📄)

**建立日期**: 2025-02-22  
**優先級**: 高  
**狀態**: ⏸️ 暫停 (缺少 API Key)  
**備註**: 目前無測試金鑰，暫緩執行，待後續資源到位再啟動。

---

## 📋 任務概述

目前系統主要支援 OpenAI 格式的 Provider。本任務旨在實作 Anthropic 的原生支援，以便使用 Claude 3/3.5 系列模型，並支援其特有的串流 (Streaming) 與工具調用 (Tool Use) 語法。

---

## 🎯 目錄與目標

- [ ] 實作 `AnthropicProvider` 類別。
- [ ] 支援對話 (Chat) 接口。
- [ ] 支援原生串流 (Streaming) 響應。
- [ ] 支援 Anthropic 格式的工具調用 (Tool Use)。
- [ ] 整合至 `Agent` 核心，可透過設定檔切換。

---

## 🛠️ 技術實作路徑

### 1. 新增 Provider 模組
在 `martlet_molt/providers/` 下建立 `anthropic.py`。
- 使用 `anthropic` 官方 SDK。
- 繼承自系統的 `BaseProvider`。

### 2. 串流處理
- 將 Anthropic 的事件流轉換為系統內部的 `StreamingBuffer` 格式。

### 3. 工具調用適配
- Anthropic 的工具定義與 OpenAI 略有不同（例如 `input_schema` vs `parameters`），需要進行轉換。

---

## 📁 修改路徑清單

- `backend/system_a/martlet_molt/providers/anthropic.py` (新建)
- `backend/system_a/martlet_molt/core/agent.py` (更新：注入新 Provider)
- `backend/system_a/requirements.txt` (新增 `anthropic`)

---

## ✅ 驗證方式

1. 使用 Claude 模型進行簡單對話，確認串流正常。
2. 呼叫現有工具（如 `web_search`），確認 Claude 能正確產生工具調用指令。
3. 執行 `ruff check --fix` 與 `pyright` 確保代碼品質。
