# Frontend

MartletMolt 前端專案目錄。支援多個 Web UI 專案共同存在，讓系統可以選擇不同的前端技術。

## 專案列表

| 專案 | 狀態 | 技術棧 | 說明 |
|------|------|--------|------|
| [web-lite-v2](./web-lite-v2/) | ✅ 推薦使用 | Tailwind + Alpine.js + Jinja2 | **輕量化版 LobeHub UI** |
| [web-lite](./web-lite/) | ⚠️ 舊版本 | Tailwind + HTMX + Jinja2 | 基礎版本（已棄用） |

## 目錄結構

```
frontend/
├── web-lite/                 # 輕量級 UI（目前使用）
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   │   ├── components/
│   │   ├── chat.html
│   │   └── index.html
│   └── README.md
│
├── <未來專案>/               # 第二個 UI 專案（規劃中）
│
└── README.md                 # 本文件
```

## 架構說明

### Web Lite V2（推薦使用）

**輕量化版 LobeHub UI**：

- **LobeHub 風格** - 現代化設計，漸變背景，圓角卡片
- **Tailwind CSS** - 透過 CDN 加載，無需打包工具
- **Alpine.js** - 輕量響應式框架（~15KB）
- **Markdown 渲染** - Marked.js + Highlight.js
- **主題切換** - 明暗雙主題支援
- **AI 友善** - 純 HTML 模板，易於 AI 修改

**詳細說明請參考 [web-lite-v2/README.md](./web-lite-v2/README.md)**

### Web Lite（舊版本）

輕量級、服務端渲染的 Web UI（已棄用）：

- **Tailwind CSS** - 透過 CDN 加載
- **HTMX** - 動態更新
- **Jinja2** - FastAPI 模板渲染

詳細說明請參考 [web-lite/README.md](./web-lite/README.md)

### 技術選擇說明

#### 為什麼選擇 Web Lite V2？

1. **符合專案定位** - 輕量化、快速部署、AI 可修改
2. **現代化 UI** - 採用 LobeHub 設計風格
3. **服務端渲染** - 降低前端複雜度
4. **零構建工具** - 全部使用 CDN，無需 Webpack/Vite
5. **AI 友善** - 純 HTML 模板，AI 可直接修改

#### 為什麼不使用 React/Next.js？

- ❌ 違背「輕量化」設計理念
- ❌ 增加 AI 自我修改的複雜度
- ❌ 需要維護雙技術棧（Python + Node.js）
- ❌ A/B 系統架構難以協調

**詳細討論請參考 [技術架構決策](../docs/architecture-decisions.md)**

## 配置方式

在 `Config/settings.yaml` 中設定要使用的前端：

```yaml
# UI 配置
ui:
  name: web-lite              # 選擇前端專案
  version: 0.1.0              # 版本號

# 路徑覆蓋（可選，若不設定則使用預設）
paths:
  templates_dir: frontend/web-lite/templates
  static_dir: frontend/web-lite/static
```

## 設計理念

1. **多前端支援**：不同需求可選擇不同技術棧
2. **獨立發展**：每個 UI 專案獨立維護，互不干擾
3. **向後兼容**：保留 web-lite 作為穩定基礎
4. **技術探索**：方便嘗試新技術而不影響現有功能

## 切換前端

只需修改配置中的路徑即可切換：

```python
# martlet_molt/core/config.py
templates_dir: Path = Path("frontend/web-lite/templates")
static_dir: Path = Path("frontend/web-lite/static")
```

或是在 `Config/settings.yaml` 中覆蓋。

## 版本歷史

- **v0.2.0** - 新增多前端專案結構，web-lite 遷移至獨立目錄
- **v0.1.0** - 初始版本，單一前端結構