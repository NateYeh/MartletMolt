# PROJECT_MAP.md — MartletMolt 專案導覽

> 快速定位專案結構，詳細架構請參閱 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 專案概述

自我進化的 AI Agent 系統，透過 A/B 雙系統切換實現零停機自我進化。

## 核心目錄

```
backend/
├── system_a/   # 活性系統 A (Port 8001)
├── system_b/   # 影子系統 B (Port 8002)
└── martlet_molt/
    ├── core/   # Agent 決策邏輯
    ├── tools/  # Agent 工具箱（擴展區）
    └── gateway/# API 端點

orchestrator/   # 流量分發 (Port 8000)
shared/         # A/B 共享數據
skills/         # 動態技能目錄
Config/         # 運行配置
```

## 進化流程

1. 修改非活躍系統
2. 重啟驗證
3. 流量切換
4. Git Push 歸檔