# 🧠 MartletMolt 擴展技能中心 (Skills Center)

這是 MartletMolt 自我進化的核心存儲庫。這裡的每一項技能都是 Agent 靈魂的一部分，採用 **OpenClaw 風格** 進行目錄化封裝。

## 📂 封裝規範

每個技能必須是一個獨立目錄，且結構如下：
```
skills/your-skill-name/
├── SKILL.md              # 說明書 (包含 YAML Metadata 與實作指南)
└── scripts/              # 實作邏輯
    └── main.py           # 繼承 BaseSkill 的 Python 類別
```

## 📜 技能清單 (核心)

- **`hello-world`**: 基礎測試技能。
- **`python-reviewer`**: 代碼品質自檢，整合 `ruff`。
- **`api-docs-generator`**: 自動化 API 文件產出。
- **`yaml-wizard`**: 設定檔格式維護與修復。

## 🔄 共享機制
由於 `/skills` 位於根目錄且獨立於 backend，它是 **System A 與 System B 共享** 的。這確保了 Agent 在任何一個環境學習到的技能，都能在全系統生效。
