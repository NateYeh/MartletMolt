# Web Lite

MartletMolt 的輕量級 Web UI 實現。

## 技術棧

- **Tailwind CSS**（透過 CDN）- 樣式框架
- **HTMX**（透過 CDN）- 動態更新（已引入，待擴展使用）
- **Jinja2** - 服務端模板渲染
- **原生 JavaScript** - 前端邏輯

## 目錄結構

```
web-lite/
├── static/
│   ├── css/           # 本地 CSS 檔案（目前使用 CDN）
│   └── js/            # 本地 JavaScript 檔案
├── templates/
│   ├── components/    # 可重用的模板元件
│   ├── chat.html      # 聊天頁面
│   └── index.html     # 首頁
└── README.md          # 本文件
```

## 功能特點

### 目前實現

- ✅ 響應式暗色主題 UI
- ✅ 同步聊天介面（POST /chat）
- ✅ 會話管理（session_id）
- ✅ 系統狀態顯示

### 待實現

- 🔲 串流回應支援（SSE）
- 🔲 WebSocket 即時通訊
- 🔲 HTMX 動態更新
- 🔲 模組化 JavaScript

## 後端整合

FastAPI 會掛載此目錄：

```python
# martlet_molt/gateway/server.py
static_dir = settings.static_dir  # frontend/web-lite/static
templates_dir = settings.templates_dir  # frontend/web-lite/templates

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
app.state.templates = Jinja2Templates(directory=str(templates_dir))
```

## 配置

在 `Config/settings.yaml` 中設定：

```yaml
# 選擇 web-lite 作為前端
ui:
  name: web-lite

# 路徑設定（若使用非預設前端）
templates_dir: frontend/web-lite/templates
static_dir: frontend/web-lite/static
```

## 開發建議

### 擴展 HTMX 使用

```html
<!-- 使用 HTMX 發送聊天訊息 -->
<form hx-post="/chat" 
      hx-target="#chat-messages" 
      hx-swap="beforeend">
    <input type="text" name="message" />
    <button type="submit">Send</button>
</form>
```

### 加入串流支援

```javascript
// 使用 EventSource 處理串流
const eventSource = new EventSource('/chat/stream');
eventSource.onmessage = (event) => {
    if (event.data === '[DONE]') {
        eventSource.close();
        return;
    }
    // 處理串流資料
    addMessageChunk(event.data);
};
```

## 版本

- **v0.1.0** - 初始版本，基礎聊天功能