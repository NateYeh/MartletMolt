---
name: python-reviewer
description: 使用 Ruff 對 Python 原始碼進行靜態分析與規範檢查。當用戶要求「檢查代碼」、「審核 Python」或「分析規範」時使用。支援 JSON 格式輸出錯誤詳情。
metadata:
  emoji: 🐍
  version: 1.1.0
  tags: ["dev", "quality", "lint"]
---

# Python Reviewer Skill

本技能整合了高效的 `ruff` 工具，旨在幫助開發者維持 Python 代碼品質。

## 什麼時候使用
- 當你需要確保代碼符合 PEP 8 規範。
- 當你收到一段外部代碼，想要快速掃描潛在的 bug (如未引用的變數)。
- 當你需要進行系統進化(Evolution)前的代碼自檢。

## 參數說明
- `code`: (必填) 字串格式的 Python 原始碼。

## 使用範例
```bash
# AI 會調用此技能並傳入代碼
skill_manager.execute(skill_name="python-reviewer", parameters={"code": "import os\n..."})
```

## 注意事項
- 僅支援 Python 3.10+ 的語法解析。
- 本技能不執行代碼，僅進行靜態檢查。
