# Web Lite

MartletMolt 的輕量化版 LobeHub UI。這是一個**輕量化、現代化、AI 友善**的前端實作，旨在保持 LobeHub 的設計美感，同時將複雜度降至最低。

## 🎨 設計理念

**輕量化 + 現代化 UI**

- **視覺一致性**: 保留 LobeHub 的現代化介面與色彩系統。
- **卓越性能**: 採用服務端渲染（SSR），大幅縮短首次加載時間。
- **零構建依賴**: 零 JavaScript 打包工具，全部使用 CDN 載入。
- **AI 友善性**: 純 HTML/Tailwind Structure，讓 AI Agent 能輕鬆修改與進化介面。

## 🏗️ 技術架構

### 技術棧
| 技術 | 角色 | 載入方式 |
|------|------|----------|
| **FastAPI** | 後端服務框架 | Python (pip) |
| **Jinja2** | 服務端模板渲染 | Python (pip) |
| **Tailwind CSS** | 樣式框架 | CDN |
| **Alpine.js** | 輕量響應式框架 | CDN |
| **Marked.js** | Markdown 解析 | CDN |
| **Highlight.js** | 代碼高亮 | CDN |

## 📁 目錄結構

```
web-lite/
├── main.py           # FastAPI 入口
├── templates/
│   ├── base.html             # 基礎模板（LobeHub 風格）
│   ├── index.html            # 首頁
│   ├── chat.html             # 聊天頁面
│   └── components/
│       └── sidebar.html      # 側邊欄組件
├── static/
│   ├── css/
│   │   └── app.css           # 自定義樣式
│   └── js/
│       └── app.js            # Alpine.js 應用邏輯
└── README.md
```

## 🚀 快速啟動

### 方法 1：使用 Makefile (推薦)
在專案根目錄執行：
```bash
# 同時啟動後端 + 前端
make dev

# 或分開啟動
make dev-backend   # 後端 API (Port 8001)
make dev-frontend  # 前端服務 (Port 8002)
```

### 方法 2：手動啟動
```bash
cd frontend/web-lite
python main.py
```

- **前端 UI**: [http://localhost:8002](http://localhost:8002)
- **健康檢查**: `http://localhost:8002/health`

## 🎯 核心功能

### ✅ 已實現
- **LobeHub 風格 UI**: 漸變背景、圓角卡片、柔和陰影。
- **主題切換**: 完善的暗色/亮色模式支援（LocalStorage 持久化）。
- **Markdown & 高亮**: 支援完整的 Markdown 語法解析與代碼塊語法高亮。
- **響應式導航**: 側邊欄縮放與移動端適配。
- **即時對話**: 非同步 API 調用與動態消息載入動畫。

---
**MartletMolt** - Self-Evolving AI Agent System 🦅
