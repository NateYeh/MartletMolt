# TASK-008: Skills 學習系統 (待啟動 📄)

**建立日期**: 2025-02-22  
**優先級**: 高  
**狀態**: 📋 待開發

---

## 📋 任務概述

SKILLS 系統是 MartletMolt 自我進化的核心組件。它允許 AI Agent 在與用戶互動的過程中，動態地編寫 Python 代碼並將其保存為可重複使用的「技能 (Skill)」。這與一次性的工具呼叫不同，技能是可以持久化、並在之後的會話中被主動檢索和運用的能力模組。

---

## 🎯 目錄與目標

- [ ] 建立 `BaseSkill` 抽象類別與元數據結構。
- [ ] 實作 `SkillManager` 負責技能的載入、註冊與生命週期管理。
- [ ] 實作 `SkillTool` 讓 AI 模型能透過自然語言進行「進修（創建/更新技能）」。
- [ ] 實作基於 `RestrictedPython` 的安全沙箱執行環境。
- [ ] 建立共享的 `skills/` 目錄，確保 A/B 系統能同步獲取新技能。

---

## 🛠️ 技術實作路徑

詳細設計請參考文件：[`docs/plan/skills_plan.md`](../plan/skills_plan.md)

### 1. 核心框架 (Phase 1)
- 定義 `SkillMetadata` 與 `SkillResult`。
- 實作動態載入器 (`loader.py`)，使用 `importlib` 載入 `skills/` 下的 `.py` 檔案。

### 2. AI 介面 (Phase 2)
- 提供 `skill_tool` 給 Agent，包含 `create`, `list`, `execute` 等 Action。

### 3. 安全防護 (Phase 3)
- 引入 `RestrictedPython` 限制代碼可執行的系統操作。

---

## 📁 修改路徑清單

- `backend/system_a/martlet_molt/skills/` (新目錄：含 base.py, manager.py, loader.py)
- `backend/system_a/martlet_molt/tools/skill.py` (新工具)
- `skills/` (根目錄：存放生成的技能模組)
- `backend/system_a/requirements.txt` (新增 `RestrictedPython`)

---

## ✅ 驗證方式

1. 用戶要求：「請學會如何計算斐波那契數列並存為技能」，確認 `skills/` 下產生正確檔案。
2. 在新對話中要求 Agent 使用該技能，確認其能正確讀取並執行。
3. 測試注入危險代碼（如 `os.system`），確認沙箱能正確攔截。
4. 執行 `ruff check --fix` 與 `pyright`。
