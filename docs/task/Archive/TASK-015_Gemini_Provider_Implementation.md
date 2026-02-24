# TASK-015: Gemini (Google) Provider 實作 (待啟動 📄)

**建立日期**: 2025-02-23  
**優先級**: 高  
**狀態**: 📋 待啟動 (利用 Google 免費層級建立備援大腦)

---

## 📋 任務概述

目前系統已具備 Ollama 與 OpenAI 基礎支援。本任務旨在實作 Google Gemini 的原生支援。Gemini 在長上下文處理以及 1.5 Flash 提供的免費額度上具有極大優勢，是 MartletMolt 多模型冗餘體系的重要組成部分。

---

## 🎯 任務目標

- [ ] 實作 `GeminiProvider` 類別，繼承自 `BaseProvider`。
- [ ] 支援對話 (Chat) 與原生串流 (Streaming) 響應。
- [ ] **訊息格式配對**: 將 MartletMolt 的 `Message` (role/content) 準確對應至 Gemini 的 `contents` (role/parts)。
- [ ] **工具調用適配**: 支援 Gemini 的 Function Calling 機制。
- [ ] 支援透過 `google-generativeai` SDK 進行溝通。

---

## 🛠️ 技術細節

### 1. 訊息格式轉換
Gemini 使用 `parts` 陣列，且 `role` 名稱為 `user` 與 `model` (而非 `assistant`)。
- `user` -> `user`
- `assistant` -> `model`
- `system` -> `system_instruction` (Gemini API 專用欄位)

### 2. 工具調用
- Gemini 支援 OpenAI 風格的 Json Schema 定義。
- 回傳結果需解析 `function_call` 片段並封裝進系統內部的 `tool_calls` 列表。

### 3. 安全設置 (Safety Settings)
- 預設關閉或調低 Gemini 的過濾器程度，以支援開發場景下的代碼分析需求。

---

## 📁 修改路徑清單

- `backend/system_a/martlet_molt/providers/gemini.py` (新建)
- `backend/system_a/requirements.txt` (新增 `google-generativeai`)
- `tests/test_provider_gemini.py` (新建：單元測試)

---

## ✅ 驗證方式

1. 獲得 Gemini API Key 後，執行 `pytest tests/test_provider_gemini.py`。
2. 透過 `martlet chat` 命令切換至 `gemini-1.5-flash` 進行實戰對話。
