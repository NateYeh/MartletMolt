# Web Lite V2 進階功能開發任務

**建立日期**: 2025-02-22  
**優先級**: 中  
**預估工時**: 8-12 小時  
**狀態**: 📋 待開發

---

## 📋 任務概述

Web Lite V2 的核心功能（聊天介面、串流響應、主題切換）已經完成。本任務旨在實現**會話管理**和**進階功能**，讓前端更加完整。

---

## ✅ 已完成功能（無需處理）

| 功能 | 狀態 | 說明 |
|------|------|------|
| 核心架構 | ✅ | FastAPI + Jinja2 + Tailwind CSS (CDN) + Alpine.js |
| UI 設計 | ✅ | LobeHub 風格，暗色/亮色主題切換 |
| 聊天功能 | ✅ | 完整的對話介面，支援 Markdown + 代碼高亮 |
| 串流響應 (SSE) | ✅ | 實現打字機效果，支援中斷 |
| Favicon | ✅ | SVG 格式，漸變設計 |

---

## 🎯 待開發任務

### 任務 1：會話管理系統 (Session Management)

**目標**: 讓用戶可以管理多個對話會話

#### 1.1 後端 API 擴展

需要在 `martlet_molt/api/routes/chat.py` 或新建 `session.py` 新增以下端點：

```python
# 建議的新 API 端點

# GET /api/sessions - 獲取所有會話列表
# POST /api/sessions - 建立新會話
# GET /api/sessions/{session_id} - 獲取會話詳情（含歷史訊息）
# DELETE /api/sessions/{session_id} - 刪除會話
# PATCH /api/sessions/{session_id} - 重命名會話
```

#### 1.2 前端 UI 實現

修改 `frontend/web-lite-v2/templates/components/sidebar.html`：

**當前狀態**（第 40-75 行）：
- 「Agent 設定」、「工具管理」、「歷史記錄」按鈕都是 `opacity-50 cursor-not-allowed`

**需要實現**：
1. 會話列表區域（顯示最近會話）
2. 新建會話按鈕（已存在，需綁定功能）
3. 會話切換功能
4. 會話重命名（點擊編輯）
5. 會話刪除功能

**參考結構**：
```html
<!-- 在 sidebar.html 的導航區域加入 -->
<div class="px-3 py-2">
    <div class="text-xs text-gray-400 dark:text-slate-500 uppercase tracking-wider font-medium mb-2">
        最近的對話
    </div>
    <div id="session-list" x-data="sessionList()">
        <template x-for="session in sessions" :key="session.id">
            <a :href="'/chat?session=' + session.id"
               class="flex items-center px-3 py-2 rounded-lg text-sm truncate
                      hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors"
               :class="{'bg-blue-50 dark:bg-blue-900/20 text-blue-600': session.id === currentSessionId}">
                <span x-text="session.title"></span>
            </a>
        </template>
    </div>
</div>
```

#### 1.3 Session 資料結構

建議在 `martlet_molt/models/` 建立：

```python
# martlet_molt/models/session.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Session:
    """對話會話"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message: Optional[str] = None
    
@dataclass
class SessionManager:
    """會話管理器"""
    sessions: dict[str, Session] = field(default_factory=dict)
    
    def create_session(self, title: str = "新對話") -> Session: ...
    def get_session(self, session_id: str) -> Optional[Session]: ...
    def delete_session(self, session_id: str) -> bool: ...
    def list_sessions(self, limit: int = 20) -> list[Session]: ...
```

---

### 任務 2：歷史記錄功能 (Chat History)

**目標**: 持久化對話記錄，支援跨會話查看

#### 2.1 儲存機制

選項 A（輕量）：使用 JSON 檔案儲存
```
data/
└── sessions/
    ├── session_abc123.json
    ├── session_def456.json
    └── ...
```

選項 B（進階）：使用 SQLite
```python
# martlet_molt/storage/chat_history.py

import sqlite3
from pathlib import Path

class ChatHistoryStore:
    def __init__(self, db_path: str = "data/chat_history.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self):
        # 建立 sessions 和 messages 表
        ...
    
    def save_message(self, session_id: str, role: str, content: str): ...
    def get_messages(self, session_id: str, limit: int = 100) -> list: ...
    def search_messages(self, query: str) -> list: ...
```

#### 2.2 前端載入歷史訊息

修改 `frontend/web-lite-v2/templates/chat.html` 的 `chatApp()` 函數：

```javascript
// 在 init() 中加入
async init() {
    this.loadSessionId();
    this.adjustBackendUrl();
    await this.loadHistory();  // 新增：載入歷史訊息
},

async loadHistory() {
    if (this.sessionId === 'default') return;
    
    try {
        const response = await fetch(`${this.backendUrl}/api/sessions/${this.sessionId}`);
        if (response.ok) {
            const data = await response.json();
            this.messages = data.messages || [];
        }
    } catch (error) {
        console.error('[ChatApp] 載入歷史失敗:', error);
    }
}
```

---

### 任務 3：文件上傳功能 (File Upload)

**目標**: 支援用戶上傳文件作為對話附件

#### 3.1 後端 API

```python
# POST /api/upload - 上傳文件
# GET /api/files/{file_id} - 獲取文件

# 建議在 martlet_molt/api/routes/upload.py
from fastapi import UploadFile, File

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    # 儲存到 data/uploads/
    # 返回 file_id 和預覽資訊
    ...
```

#### 3.2 前端 UI

修改 `frontend/web-lite-v2/templates/chat.html` 的上傳按鈕（第 161-167 行）：

```html
<!-- 當前是 disabled 狀態，需要啟用並實現功能 -->
<button type="button" 
        @click="triggerUpload()"
        class="p-2 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors group"
        title="上傳文件">
    <svg>...</svg>
</button>

<!-- 隱藏的文件輸入 -->
<input type="file" 
       id="file-input" 
       class="hidden" 
       accept=".txt,.md,.pdf,.png,.jpg,.jpeg"
       @change="handleUpload($event)">
```

---

### 任務 4：Agent 設定介面 (Agent Settings)

**目標**: 可視化調整 Agent 參數

#### 4.1 設定頁面

建立 `frontend/web-lite-v2/templates/settings.html`：

```html
{% extends "base.html" %}

{% block title %}設定 - MartletMolt{% endblock %}

{% block content %}
<!-- Agent 設定表單 -->
<div class="max-w-2xl mx-auto p-6">
    <h1>Agent 設定</h1>
    
    <!-- 模型選擇 -->
    <select x-model="settings.model">
        <option value="gpt-4">GPT-4</option>
        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
        <option value="claude-3-opus">Claude 3 Opus</option>
    </select>
    
    <!-- 溫度滑桿 -->
    <input type="range" min="0" max="1" step="0.1" x-model="settings.temperature">
    
    <!-- 系統提示詞 -->
    <textarea x-model="settings.system_prompt"></textarea>
    
    <!-- 工具啟用/停用 -->
    ...
</div>
{% endblock %}
```

#### 4.2 後端 API

```python
# GET /api/settings - 獲取當前設定
# PUT /api/settings - 更新設定
```

---

### 任務 5：工具管理面板 (Tools Management)

**目標**: 啟用/停用/配置工具

#### 5.1 工具列表頁面

建立 `frontend/web-lite-v2/templates/tools.html`：

```html
{% block content %}
<div class="max-w-4xl mx-auto p-6">
    <h1>工具管理</h1>
    
    <!-- 工具列表 -->
    <div class="space-y-4">
        <template x-for="tool in tools" :key="tool.name">
            <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border">
                <div class="flex items-center justify-between">
                    <div>
                        <h3 x-text="tool.name"></h3>
                        <p x-text="tool.description"></p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" :checked="tool.enabled" @change="toggleTool(tool.name)">
                        <!-- Toggle Switch -->
                    </label>
                </div>
            </div>
        </template>
    </div>
</div>
{% endblock %}
```

#### 5.2 後端 API

```python
# GET /api/tools - 獲取工具列表
# PUT /api/tools/{tool_name}/toggle - 啟用/停用工具
```

---

## 📁 相關檔案路徑

```
frontend/web-lite-v2/
├── main.py                          # FastAPI 路由（需新增頁面路由）
├── templates/
│   ├── base.html                    # 基礎模板
│   ├── chat.html                    # 聊天頁面（需修改）
│   ├── index.html                   # 首頁
│   ├── settings.html                # 待建立
│   ├── tools.html                   # 待建立
│   └── components/
│       └── sidebar.html             # 側邊欄（需修改）
└── static/
    ├── css/app.css
    ├── js/app.js                    # 可擴展
    └── favicon.svg

martlet_molt/
├── api/routes/
│   ├── chat.py                      # 聊天 API
│   ├── session.py                   # 待建立
│   ├── upload.py                    # 待建立
│   └── settings.py                  # 待建立
├── models/
│   └── session.py                   # 待建立
└── storage/
    └── chat_history.py              # 待建立
```

---

## 🔧 開發規範

### 程式碼風格
- 遵循 PEP 8 規範
- 使用 `snake_case` 命名變數和函數
- 使用 `PascalCase` 命名類別
- 所有公開函數需包含 Docstring（中文）

### 型別註解
- 所有函數參數和返回值需加型別註解
- 字串預設 `''`，串列預設 `[]`

### 錯誤處理
- 使用 `logger.exception` 記錄完整堆疊

### 驗證
- 完成後使用 `ruff check --fix` 和 `pyright` 檢查

---

## 🧪 測試驗證清單

完成後請驗證：

- [ ] 會話列表正確顯示
- [ ] 新建會話功能正常
- [ ] 切換會話載入歷史訊息
- [ ] 刪除會話功能正常
- [ ] 文件上傳功能正常
- [ ] Agent 設定可儲存
- [ ] 工具開關可切換
- [ ] 暗色/亮色主題在所有新頁面正常
- [ ] 響應式設計在手機端正常

---

## 📚 參考資源

- [MartletMolt AI Context](../AI_CONTEXT.md) - 專案整體架構
- [Web Lite V2 README](../../frontend/web-lite-v2/README.md) - 前端說明文件
- [LobeHub UI](https://lobehub.com) - UI 設計參考

---

## 💡 開發建議

1. **優先順序**: 先完成會話管理（任務 1-2），再處理進階功能（任務 3-5）
2. **漸進式開發**: 每完成一個功能就驗證，不要一次改太多
3. **保持輕量**: 遵循 Web Lite V2 的設計理念，避免引入複雜的前端框架
4. **AI 可修改性**: 保持 HTML 模板的簡潔，讓 AI 未來能輕鬆修改

---

**祝開發順利！🦅**

如有問題，請參考 `/mnt/work/py_works/external_projects/MartletMolt/docs/AI_CONTEXT.md`