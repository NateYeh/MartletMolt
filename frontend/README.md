# Frontend

MartletMolt 前端專案目錄。

## 目前前端

| 專案 | 技術棧 | 說明 |
|------|--------|------|
| [web-lite](./web-lite/) | Tailwind + Alpine.js + Jinja2 | **主要的 Web UI (LobeHub 風格)** |

## 目錄結構

```
frontend/
├── web-lite/                 # 輕量級 UI（目前使用）
│   ├── main.py
│   ├── static/
│   ├── templates/
│   └── README.md
└── README.md                 # 本文件
```

## 技術特性

- **LobeHub 風格** - 現代化設計，漸變背景，圓角卡片
- **Tailwind CSS** - 透過 CDN 加載，無需打包工具
- **Alpine.js** - 輕量響應式框架
- **Markdown 渲染** - Marked.js + Highlight.js
- **主題切換** - 明暗雙主題支援
- **AI 友善** - 純 HTML 模板，極其適合 AI Agent 進行自我進化修改

## 配置方式

系統目前預設指向 `frontend/web-lite`。若需修改詳細配置，可查看 `Config/settings.yaml`。

## 設計理念

1. **極簡化**：移除所有不必要的構建工具 (Vite, Webpack)。
2. **AI 可讀性**：程式碼結構簡單明瞭，讓 Agent 可以直接重寫 HTML/JS 邏輯。
3. **高效運作**：輕量級依賴，啟動速度極快。
