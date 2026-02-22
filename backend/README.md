# Backend

MartletMolt 的後端系統目錄，採用 **A/B 雙系統架構** 實現零停機進化。

---

## 目錄結構

```
backend/
├── __init__.py
├── system_a/                    # A 系統
│   ├── __init__.py
│   └── martlet_molt/
│       ├── core/               # 核心模組（Agent, Session, Config）
│       ├── providers/          # AI Provider（OpenAI, Anthropic, Ollama）
│       ├── tools/              # 工具系統（Web, Shell, File）
│       ├── gateway/            # API 伺服器（FastAPI, WebSocket）
│       ├── channels/           # 通訊通道（CLI, Web）
│       ├── cli.py              # CLI 入口
│       └── main.py             # 服務入口
└── system_b/                    # B 系統（與 A 結構相同）
    ├── __init__.py
    └── martlet_molt/
        └── ...
```

---

## A/B 雙系統架構

### 設計理念

MartletMolt 使用 **A/B 雙系統架構** 來實現自我進化能力：

| 狀態 | 說明 |
|------|------|
| **Active** | 當前服務中的系統（A 或 B） |
| **Standby** | 待命系統，用於部署新版本 |
| **Synced** | 已與 Active 系統同步代碼 |

### 進化流程

```
1. 偵測到需要進化
2. 檢查當前活躍系統（假設是 A）
3. AI 修改 B 系統程式碼
4. 啟動 B 系統測試
5. 健康檢查
   ├─ 失敗 → 回滾 B，A 繼續服務
   └─ 成功 → 停止 A，B 開始服務
6. 同步 B → A（備份）
```

### 優勢

- **零停機部署**：切換過程服務不中斷
- **快速回滾**：失敗時立即切回原系統
- **安全進化**：AI 可以安全地修改待命系統

---

## 使用方式

### 啟動服務

```bash
# 透過統一入口（根據 settings.yaml 的 active_system 決定）
martlet start

# 直接啟動 A 系統
martlet-a start

# 直接啟動 B 系統
martlet-b start
```

### 同步系統

```bash
# A → B 同步
make sync-a-to-b

# B → A 同步
make sync-b-to-a
```

---

## 相關文件

- [Orchestrator](../orchestrator/) - A/B 系統生命週期管理
- [Frontend](../frontend/) - Web UI 介面
- [AI Context](../docs/AI_CONTEXT.md) - 專案核心架構說明