# Web Lite

MartletMolt 的輕量級前端服務（獨立運行）。

## 架構

```
┌─────────────────────────────────────────────────────────────┐
│  Web Lite Frontend (Port 8002)                              │
│  ├── /              ← 首頁 HTML                             │
│  ├── /chat          ← 聊天頁面 HTML                         │
│  └── /static/*      ← 靜態資源                              │
│         │                                                    │
│         └──→ HTTP 呼叫後端 API                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ HTTP
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend API (Port 8001)                                    │
│  ├── /health        ← 健康檢查                              │
│  ├── /status        ← 系統狀態                              │
│  ├── /chat          ← 聊天 API                              │
│  └── /chat/stream   ← 串流 API                              │
└─────────────────────────────────────────────────────────────┘
```

## 技術棧

- **FastAPI** - 前端服務框架
- **Jinja2** - 服務端模板渲染
- **Tailwind CSS** (CDN) - 樣式框架
- **HTMX** (CDN) - 動態更新
- **httpx** - HTTP 客戶端（呼叫後端 API）

## 快速啟動

### 方法 1：使用 Makefile（推薦）

```bash
# 同時啟動後端 + 前端
make dev

# 或分開啟動
make dev-backend   # 只啟動後端 (Port 8001)
make dev-frontend  # 只啟動前端 (Port 8002)
```

### 方法 2：手動啟動

```bash
# 終端機 1：啟動後端
python -m martlet_molt.main

# 終端機 2：啟動前端
cd frontend/web-lite
python main.py
```

## 配置

### 環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `BACKEND_HOST` | `0.0.0.0` | 後端 API 主機 |
| `BACKEND_PORT` | `8001` | 後端 API 端口 |
| `FRONTEND_HOST` | `0.0.0.0` | 前端服務主機 |
| `FRONTEND_PORT` | `8002` | 前端服務端口 |
| `WEB_LITE_DEBUG` | `false` | 除錯模式 |

### 範例

```bash
# 使用不同的後端地址
BACKEND_HOST=192.168.1.100 BACKEND_PORT=8001 python main.py
```

## 目錄結構

```
web-lite/
├── main.py           # FastAPI 入口
├── config.py         # 配置管理
├── routes.py         # 前端路由
├── templates/
│   ├── components/   # 可重用元件
│   ├── chat.html     # 聊天頁面
│   └── index.html    # 首頁
├── static/
│   ├── css/          # 本地 CSS
│   └── js/           # 本地 JavaScript
└── README.md
```

## API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | 首頁 |
| `/chat` | GET | 聊天頁面 |
| `/api/chat` | POST | 代理到後端的聊天 API |
| `/api/status` | GET | 代理到後端的狀態 API |

**注意**：前端頁面直接使用 JavaScript 呼叫後端 API（`http://0.0.0.0:8001/chat`），代理端點為可選功能。

## 開發

### 安裝依賴

```bash
pip install fastapi uvicorn jinja2 httpx pydantic-settings loguru
```

### 除錯模式

```bash
WEB_LITE_DEBUG=true python main.py
```

## 版本

- **v0.1.0** - 初始版本，前後端分離架構
