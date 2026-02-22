# TASK-002: Tool 參數嚴格驗證 (待啟動 📄)

**建立日期**: 2025-02-22  
**優先級**: 中  
**狀態**: 📋 待開發

---

## 📋 任務概述

目前工具 (Tools) 的參數驗證較為鬆散，容易導致 AI 產生錯誤格式的參數時造成系統報錯。本任務旨在引入 **JSON Schema** 驗證機制，在工具執行前強行驗證參數合法性。

---

## 🎯 目錄與目標

- [ ] 統一 `BaseTool` 的 `parameters_schema` 定義格式。
- [ ] 在 `BaseTool.call()` 或執行入口處加入 `jsonschema` 驗證。
- [ ] 完善錯誤回傳機制，讓 AI 知道參數錯在哪裡並能自我修正。

---

## 🛠️ 技術實作路徑

### 1. 更新基類
修改 `martlet_molt/tools/base.py`，增加驗證邏輯。
```python
from jsonschema import validate

def validate_args(self, args: dict):
    validate(instance=args, schema=self.parameters_schema)
```

### 2. 錯誤捕捉
當驗證失敗時，拋出具備詳細描述的 `ValidationError`，並將錯誤描述回傳給 Agent，而不是直接讓系統崩潰。

---

## 📁 修改路徑清單

- `backend/system_a/martlet_molt/tools/base.py` (核心修改)
- `backend/system_a/martlet_molt/core/agent.py` (處理驗證錯誤的重試邏輯)
- `backend/system_a/requirements.txt` (新增 `jsonschema`)

---

## ✅ 驗證方式

1. 撰寫單元測試，模擬傳入錯誤參數給工具，確認系統會攔截並報錯。
2. 觀察 Agent 在收到參數報錯後，是否能根據報錯內容修正並重新呼叫。
3. 執行 `ruff check --fix` 與 `pyright`。
