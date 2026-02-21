# AI_CONTEXT.md — LLM-Friendly Project Context

> 目的：讓 AI 不必讀完所有檔案即可理解專案核心架構，減少 Token 消耗。

---

## 專案概述

**MartletMolt** 是一個自我進化的 AI Agent 系統，具備自我修改、自我重啟、自我進化的能力。

- **定位**：Self-Evolving AI Agent System
- **技術棧**：Python 3.11+ / FastAPI / Playwright / HTMX
- **核心特點**：A/B 雙系統架構、零停機進化、網頁自動化

---

## 核心架構（Top-Down）

```
┌─────────────────────────────────────────────────────────────────┐
│  Web UI (HTMX + Tailwind)                                       │
│  - 聊天介面、Tool 結果展示、系統狀態                              │
├─────────────────────────────────────────────────────────────────┤
│  Orchestrator (Guardian)                                        │
│  - A/B 系統生命週期管理、健康檢查、切換、同步 (不可被 AI 修改)    │
├─────────────────────────────────────────────────────────────────┤
│  System A / System B                                            │
│  ├─ Gateway Server (FastAPI)                                    │
│  ├─ Agent Runtime (AI Core + Tools)                             │
│  ├─ Provider Layer (OpenAI, Anthropic, Ollama)                  │
│  └─ Channel Layer (Web, CLI)                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 關鍵目錄結構

| 路徑 | 用途 |
|------|------|
| `orchestrator/` | 守護程序，管理 A/B 生命週期（**不可被 AI 修改**） |
| `system_a/` | A 系統（完整服務） |
| `system_b/` | B 系統（完整服務） |
| `shared/` | 共享配置、資料、日誌 |
| `state/` | 系統狀態（當前活躍系統） |
| `frontend/` | 前端資源（可選，進階用途） |

---

## System A/B 內部結構

```
system_a/martlet_molt/
├── core/                   # 核心模組
│   ├── agent.py           # AI Agent 核心
│   ├── session.py         # 會話管理
│   └── config.py          # 配置管理
├── providers/              # AI Provider 抽象層
│   ├── base.py            # 抽象基類
│   ├── openai.py          # OpenAI
│   ├── anthropic.py       # Anthropic
│   └── ollama.py          # Ollama
├── tools/                  # 工具系統
│   ├── base.py            # 抽象基類
│   ├── web_*.py           # 網頁自動化工具
│   ├── shell.py           # Shell 命令
│   ├── file_*.py          # 檔案操作
│   └── mysql.py           # 資料庫操作
├── gateway/                # API 伺服器
│   ├── server.py          # FastAPI 主程式
│   ├── routes.py          # REST API
│   └── websocket.py       # WebSocket
├── channels/               # 通訊通道
│   └── web/               # Web Channel
├── templates/              # HTML 模板 (Jinja2)
├── static/                 # 靜態資源
├── cli.py                 # CLI 入口
└── main.py                # 服務入口
```

---

## 關鍵類型與介面

### Tool 抽象基類

```python
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel

class ToolResult(BaseModel):
    """Tool 執行結果"""
    success: bool
    data: Any = None
    error: str = ""
    metadata: dict = {}

class BaseTool(ABC):
    """Tool 抽象基類"""
    name: str
    description: str
    parameters_schema: dict  # JSON Schema
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """執行 Tool"""
        pass
```

### Provider 抽象基類

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator
from pydantic import BaseModel

class Message(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str

class BaseProvider(ABC):
    """AI Provider 抽象基類"""
    name: str
    
    @abstractmethod
    async def chat(self, messages: list[Message]) -> str:
        """同步對話"""
        pass
    
    @abstractmethod
    async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
        """串流對話"""
        pass
```

### Channel 抽象基類

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator

class BaseChannel(ABC):
    """通訊通道抽象基類"""
    id: str
    name: str
    
    @abstractmethod
    async def receive(self) -> AsyncIterator[Message]:
        """接收訊息"""
        pass
    
    @abstractmethod
    async def send(self, message: Message) -> bool:
        """發送訊息"""
        pass
```

---

## Orchestrator 職責

| 功能 | 說明 |
|------|------|
| `manager.py` | 啟動/停止 System A/B |
| `health_check.py` | HTTP 健康檢查 |
| `switcher.py` | A/B 切換邏輯 |
| `sync.py` | 程式碼同步（備份） |

**重要**：Orchestrator 不能被 AI Tools 修改！

---

## A/B 切換流程

```
1. AI 決定需要進化
2. 檢查當前活躍系統 (假設是 A)
3. 修改 B 系統程式碼
4. 啟動 B 系統測試
5. 健康檢查
   - 失敗 → 回滾 B，A 繼續服務
   - 成功 → 停止 A，B 開始服務
6. 同步 B → A (備份)
```

---

## 配置系統

### 配置檔位置

```
shared/config/settings.yaml    # 主配置
shared/data/sessions/          # 對話歷史 (JSONL)
state/state.json               # 系統狀態
```

### 配置結構

```yaml
# shared/config/settings.yaml
gateway:
  host: "0.0.0.0"
  port: 8000

providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4o"
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-sonnet-4-20250514"

agent:
  max_tokens: 4096
  temperature: 0.7

tools:
  web:
    enabled: true
    headless: true
  shell:
    enabled: true
    sandbox: true

orchestrator:
  health_check_interval: 30
  health_check_retries: 3
```

### 狀態檔案

```json
// state/state.json
{
  "active": "a",
  "version": {
    "a": "0.1.0",
    "b": "0.1.0"
  },
  "last_switch": "2025-01-15T10:30:00Z",
  "health_status": {
    "a": {"status": "running", "uptime": 3600},
    "b": {"status": "synced", "uptime": 0}
  }
}
```

---

## CLI 命令

| 命令 | 用途 |
|------|------|
| `martlet start` | 啟動服務 |
| `martlet stop` | 停止服務 |
| `martlet status` | 查看狀態 |
| `martlet chat` | CLI 對話模式 |
| `martlet evolve` | 觸發進化流程 |
| `martlet switch` | 手動切換 A/B |
| `martlet doctor` | 診斷問題 |
| `martlet config` | 配置管理 |

---

## 開發命令

```bash
# 安裝依賴
pip install -e ".[dev]"

# 安裝 Playwright 瀏覽器
playwright install chromium

# 啟動開發伺服器
martlet start --dev

# CLI 對話模式
martlet chat

# 執行測試
pytest

# Lint + Format
ruff check .
ruff format .
```

---

## Tool 系統

### 網頁自動化 Tool

| Tool | 功能 |
|------|------|
| `web_navigate` | 導航到 URL |
| `web_extract` | 提取網頁內容（文字、HTML、連結） |
| `web_click` | 點擊元素 |
| `web_fill` | 填寫表單 |
| `web_evaluate` | 執行 JavaScript |
| `web_screenshot` | 截圖（可選） |

### 檔案操作 Tool

| Tool | 功能 |
|------|------|
| `file_read` | 讀取檔案 |
| `file_write` | 寫入檔案 |
| `file_replace` | 區塊替換 |

### 其他 Tool

| Tool | 功能 |
|------|------|
| `shell` | 執行 Shell 命令 |
| `mysql` | 執行 SQL |

---

## 安全設計

| 機制 | 說明 |
|------|------|
| **Orchestrator 保護** | `/orchestrator/` 目錄不可被 AI Tool 修改 |
| **沙箱執行** | Shell 命令在受限環境執行 |
| **API Key 保護** | 從環境變數讀取，不寫入程式碼 |
| **健康檢查** | 進化失敗自動回滾 |

---

## 命名慣例

- **產品名稱**：MartletMolt（標題、文檔）
- **CLI 命令**：`martlet`（小寫）
- **型別/介面**：PascalCase
- **函數/變數**：snake_case
- **檔案**：snake_case

---

## 快速定位問題

| 問題類型 | 查看位置 |
|---------|---------|
| Orchestrator 錯誤 | `orchestrator/` |
| A/B 切換問題 | `orchestrator/switcher.py` |
| Gateway 啟動失敗 | `system_a/martlet_molt/gateway/` |
| Tool 執行問題 | `system_a/martlet_molt/tools/` |
| Provider 調用失敗 | `system_a/martlet_molt/providers/` |
| 配置問題 | `shared/config/settings.yaml` |

---

## 編碼規範摘要

- Python 3.11+，使用型別註解
- FastAPI 非同步風格
- Pydantic 進行資料驗證
- 使用 Loguru 記錄日誌
- Ruff 進行 Lint 和 Format
- 每個模組都要有 `__init__.py`

---

## 重要連結

- **GitHub**：https://github.com/NateYeh/MartletMolt
- **詳細文檔**：`docs/`