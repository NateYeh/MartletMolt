# Frontend

前端專案目錄，與後端獨立分離。

## 目錄結構

```
frontend/
├── templates/          # HTML 模板 (Jinja2)
│   ├── index.html     # 首頁
│   └── chat.html      # 聊天頁面
└── static/            # 靜態資源
    ├── css/           # 樣式表
    └── js/            # JavaScript
```

## 設計理念

- **前後端分離**：後端提供 REST API，前端獨立發展
- **技術棧**：目前使用 HTMX + Tailwind CSS（透過 CDN）
- **未來擴展**：可遷移到 React/Vue 等現代前端框架

## 後端整合

FastAPI 會掛載此目錄：

```python
# system_a/martlet_molt/gateway/server.py
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")
```