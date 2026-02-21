# Shared

運行時共享資料目錄，存放系統運行時產生的資料。

## 目錄結構

```
shared/
├── data/              # 共享資料
│   ├── sessions/     # 對話歷史 (JSONL)
│   └── transcripts/  # 逐字稿
├── logs/             # 系統日誌
└── state/            # 系統狀態
    └── state.json    # 當前活躍系統
```

## 設計理念

- **資料共享**：System A 和 System B 共用同一份資料
- **持久化**：資料在系統重啟後仍然保留
- **敏感性**：包含對話歷史，不應上傳至 Git

## .gitignore

已在專案根目錄的 .gitignore 中排除：

```gitignore
shared/data/*
shared/logs/*
!shared/data/.gitkeep
!shared/logs/.gitkeep
```