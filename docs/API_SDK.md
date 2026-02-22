# MartletMolt 後端 API SDK 文件

> **版本**: v0.1.0  
> **Base URL**: `http://localhost:8001`  
> **最後更新**: 2025-01-15

---

## 📋 目錄

- [概覽](#概覽)
- [快速開始](#快速開始)
- [API 端點總覽](#api-端點總覽)
- [詳細 API 文件](#詳細-api-文件)
  - [1. 健康檢查](#健康檢查)
  - [2. 系統狀態](#系統狀態)
  - [3. 同步對話](#同步對話)
  - [4. 串流對話](#串流對話)
  - [5. 列出所有會話](#列出所有會話)
  - [6. 取得會話詳情](#取得會話詳情)
  - [7. 刪除會話](#刪除會話)
- [錯誤處理](#錯誤處理)
- [JavaScript/TypeScript SDK](#javascripttypescript-sdk)
- [使用範例](#使用範例)
- [常見問題](#常見問題)

---

## 概覽

MartletMolt 後端提供純 API 服務，支援 AI 對話功能。
所有端點均返回 JSON 格式數據，並支援 CORS 跨域請求。


### 核心特性

- ✅ **RESTful API**: 標準 HTTP 方法與狀態碼
- ✅ **串流支援**: Server-Sent Events (SSE) 即時串流回應
- ✅ **會話管理**: 持久化對話歷史
- ✅ **多 Provider**: 支援 OpenAI、Anthropic、Ollama 等
- ✅ **Tool Calling**: 支援 AI 工具調用

### 技術規格

- **框架**: FastAPI
- **數據格式**: JSON
- **編碼**: UTF-8
- **CORS**: 已啟用

---

## 快速開始

### 1. 啟動後端服務

```bash
# 方式一：使用 Makefile（推薦）
make dev-backend

# 方式二：直接執行
python -m martlet_molt.main

# 後端將運行於
# http://localhost:8001

```
### 2. 驗證服務狀態

```bash
# 健康檢查
curl http://localhost:8001/health

# 查看系統狀態
curl http://localhost:8001/status

```
### 3. 發送第一個請求

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，請介紹一下你自己"}'
```

---

## API 端點總覽

### 系統端點

| 方法 | 路徑 | 描述 |
| ------ | ------ | ------ |
| `GET` | `/health` | 健康檢查 |
| `GET` | `/status` | 系統狀態 |

### 對話端點

| 方法 | 路徑 | 描述 | 是否串流 |
| ------ | ------ | ------ | ------ |
| `POST` | `/chat` | 同步對話 | ❌ |
| `POST` | `/chat/stream` | 串流對話 | ✅ |

### 會話管理端點

| 方法 | 路徑 | 描述 |
| ------ | ------ | ------ |
| `GET` | `/sessions` | 列出所有會話 |
| `GET` | `/sessions/{session_id}` | 取得會話詳情 |
| `DELETE` | `/sessions/{session_id}` | 刪除會話 |


---

## 詳細 API 文件


### 1. 健康檢查

**端點**: `GET /health`

**描述**: 檢查後端服務是否正常運行

**請求**:
```http
GET /health HTTP/1.1
Host: localhost:8001
```



**回應**:
```json
{
  "status": "running",
  "system": "SystemA",
  "version": "0.1.0"
}
```

**回應欄位**:

| 欄位 | 類型 | 描述 |
|------|------|------|
| `status` | `string` | 服務狀態（"running" 或 "error"） |
| `system` | `string` | 當前活躍系統名稱（"SystemA" 或 "SystemB"） |
| `version` | `string` | API 版本號 |


**範例**:
```javascript
const response = await fetch('http://localhost:8001/health');
const data = await response.json();
console.log(data);
```

---

### 2. 系統狀態

**端點**: `GET /status`

**描述**: 取得詳細的系統狀態資訊，包括可用的工具列表

**請求**:
```http
GET /status HTTP/1.1
Host: localhost:8001
```



**回應**:
```json
{
  "active": true,
  "model": "gpt-4o",
  "provider": "openai",
  "system": "SystemA",
  "tools": [
    "shell",
    "file_read",
    "file_write",
    "web_navigate",
    "web_extract"
  ]
}
```

**回應欄位**:

| 欄位 | 類型 | 描述 |
|------|------|------|
| `system` | `string` | 當前活躍系統名稱 |
| `active` | `boolean` | 系統是否活躍 |
| `tools` | `array[string]` | 可用工具列表 |
| `provider` | `string` | 當前 AI Provider（"openai", "anthropic", "ollama"） |
| `model` | `string` | 當前使用的模型名稱 |


**範例**:
```javascript
const response = await fetch('http://localhost:8001/status');
const data = await response.json();
console.log('Available tools:', data.tools);
console.log('Current model:', data.model);
```

---

### 3. 同步對話

**端點**: `POST /chat`

**描述**: 發送訊息並等待完整回應（非串流）

**請求**:
```http
POST /chat HTTP/1.1
Host: localhost:8001
Content-Type: application/json

{
  "message": "\u8acb\u5e6b\u6211\u5217\u51fa\u5c08\u6848\u76ee\u9304\u7d50\u69cb",
  "session_id": "default"
}
```

**請求參數**:

| 參數 | 類型 | 必填 | 預設值 | 描述 |
|------|------|------|--------|------|
| `message` | `string` | ✅ | - | 用戶訊息內容 |
| `session_id` | `string` | ❌ | `default` | 會話 ID，用於持久化對話歷史 |
| `stream` | `boolean` | ❌ | - | 是否使用串流（此端點忽略此參數） |


**回應**:
```json
{
  "message": "\u597d\u7684\uff0c\u6211\u5e6b\u60a8\u5217\u51fa\u5c08\u6848\u76ee\u9304\u7d50\u69cb...\n\n\u5c08\u6848\u6839\u76ee\u9304\u5305\u542b\uff1a\n- orchestrator/\n- system_a/\n- system_b/\n- frontend/\n- shared/\n- Config/\n",
  "session_id": "default"
}
```

**回應欄位**:

| 欄位 | 類型 | 描述 |
|------|------|------|
| `message` | `string` | AI 的完整回應 |
| `session_id` | `string` | 會話 ID（可能與請求不同，若請求未提供則自動生成） |

**狀態碼**:
- `200 請求成功`: 請求成功
- `400 請求參數錯誤`: 請求參數錯誤
- `500 服務器內部錯誤`: 服務器內部錯誤

**範例**:
```javascript
const response = await fetch('http://localhost:8001/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: '你好',
    session_id: 'my-session-123'
  })
});

const data = await response.json();
console.log(data.message);
```

---

### 4. 串流對話

**端點**: `POST /chat/stream`

**描述**: 發送訊息並以 Server-Sent Events (SSE) 格式串流接收回應

**請求**:
```http
POST /chat/stream HTTP/1.1
Host: localhost:8001
Content-Type: application/json

{
  "message": "\u8acb\u5beb\u4e00\u500b Python \u5feb\u901f\u6392\u5e8f\u7b97\u6cd5",
  "session_id": "coding-session"
}
```

**請求參數**:

| 參數 | 類型 | 必填 | 預設值 | 描述 |
|------|------|------|--------|------|
| `message` | `string` | ✅ | - | 用戶訊息內容 |
| `session_id` | `string` | ❌ | - | 會話 ID |


**回應**:
```
data: 這是

data: 一個

data: Python

data: 快速排序

data: 算法...

data: [DONE]

```


**狀態碼**:
- `200 請求成功（開始串流）`: 請求成功（開始串流）
- `400 請求參數錯誤`: 請求參數錯誤
- `500 服務器內部錯誤`: 服務器內部錯誤

**範例**:
```javascript
const response = await fetch('http://localhost:8001/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: '寫一個 Python 快速排序',
    session_id: 'coding-session'
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = line.substring(6);
      if (data === '[DONE]') {
        console.log('串流結束');
        break;
      } else if (data.startsWith('[ERROR]')) {
        console.error('錯誤:', data.substring(8));
      } else {
        console.log('收到:', data);
      }
    }
  }
}
```

---

### 5. 列出所有會話

**端點**: `GET /sessions`

**描述**: 取得所有會話的基本資訊列表

**請求**:
```http
GET /sessions HTTP/1.1
Host: localhost:8001
```



**回應**:
```json
{
  "sessions": [
    {
      "created_at": "2025-01-15T10:00:00",
      "id": "default",
      "message_count": 10,
      "metadata": {},
      "tool_call_count": 2,
      "updated_at": "2025-01-15T10:30:00"
    },
    {
      "created_at": "2025-01-15T09:00:00",
      "id": "coding-session",
      "message_count": 25,
      "metadata": {},
      "tool_call_count": 5,
      "updated_at": "2025-01-15T11:00:00"
    }
  ],
  "total": 2
}
```

**回應欄位**:

| 欄位 | 類型 | 描述 |
|------|------|------|
| `sessions` | `array[SessionInfo]` | 會話列表 |
| `total` | `integer` | 總會話數 |


**範例**:
```javascript
const response = await fetch('http://localhost:8001/sessions');
const data = await response.json();

console.log('總會話數:', data.total);
data.sessions.forEach(session => {
  console.log(`- ${session.id}: ${session.message_count} 條訊息`);
});
```

---

### 6. 取得會話詳情

**端點**: `GET /sessions/{session_id}`

**描述**: 取得指定會話的詳細資訊，包含完整的訊息歷史

**請求**:
```http
GET /sessions/{session_id} HTTP/1.1
Host: localhost:8001
```


**路徑參數**:

| 參數 | 類型 | 描述 |
|------|------|------|
| `session_id` | `string` | 會話 ID |

**回應**:
```json
{
  "created_at": "2025-01-15T10:00:00",
  "id": "default",
  "messages": [
    {
      "content": "\u4f60\u597d",
      "id": "msg123",
      "name": null,
      "role": "user",
      "timestamp": "2025-01-15T10:00:00",
      "tool_call_id": null,
      "tool_calls": null
    },
    {
      "content": "\u4f60\u597d\uff01\u6709\u4ec0\u9ebc\u6211\u53ef\u4ee5\u5e6b\u4f60\u7684\u55ce\uff1f",
      "id": "msg456",
      "name": null,
      "role": "assistant",
      "timestamp": "2025-01-15T10:00:05",
      "tool_call_id": null,
      "tool_calls": null
    }
  ],
  "metadata": {},
  "tool_calls": [],
  "updated_at": "2025-01-15T10:30:00"
}
```

**回應欄位**:

| 欄位 | 類型 | 描述 |
|------|------|------|
| `id` | `string` | 會話 ID |
| `created_at` | `string` | 建立時間（ISO 8601） |
| `updated_at` | `string` | 最後更新時間（ISO 8601） |
| `messages` | `array[Message]` | 完整訊息列表 |
| `tool_calls` | `array` | 工具調用記錄 |
| `metadata` | `object` | 會話元數據 |

**狀態碼**:
- `200 請求成功`: 請求成功
- `404 會話不存在`: 會話不存在

**範例**:
```javascript
const response = await fetch('http://localhost:8001/sessions/default');
const session = await response.json();

console.log('會話 ID:', session.id);
console.log('訊息數量:', session.messages.length);

// 遍歷所有訊息
session.messages.forEach(msg => {
  console.log(`[${msg.role}] ${msg.content}`);
});
```

---

### 7. 刪除會話

**端點**: `DELETE /sessions/{session_id}`

**描述**: 刪除指定的會話及其所有歷史記錄

**請求**:
```http
DELETE /sessions/{session_id} HTTP/1.1
Host: localhost:8001
```


**路徑參數**:

| 參數 | 類型 | 描述 |
|------|------|------|
| `session_id` | `string` | 會話 ID |

**回應**:
```json
{
  "message": "Session \u0027default\u0027 deleted successfully",
  "success": true
}
```

**回應欄位**:

| 欄位 | 類型 | 描述 |
|------|------|------|
| `success` | `boolean` | 是否成功刪除 |
| `message` | `string` | 操作結果訊息 |

**狀態碼**:
- `200 刪除成功`: 刪除成功
- `404 會話不存在`: 會話不存在

**範例**:
```javascript
const response = await fetch('http://localhost:8001/sessions/old-session', {
  method: 'DELETE'
});

const result = await response.json();
console.log(result.message); // Session 'old-session' deleted successfully
```

---

## 錯誤處理

### 錯誤回應格式

當 API 發生錯誤時，會返回 HTTP 錯誤狀態碼和以下格式的 JSON：

```json
{
  "detail": "錯誤描述訊息"
}
```

### 常見錯誤碼

| 狀態碼 | 描述 | 可能原因 |
|--------|------|----------|
| `400 Bad Request` | 請求參數錯誤 | 缺少必填欄位, 格式錯誤 |
| `404 Not Found` | 找不到資源 | 錯誤的 API 路徑 |
| `422 Unprocessable Entity` | 數據驗證失敗 | JSON 格式錯誤, 欄位類型不符 |
| `500 Internal Server Error` | 服務器內部錯誤 | Provider API 錯誤, 系統異常 |
| `503 Service Unavailable` | 服務不可用 | 系統維護中, 過載 |

### 錯誤處理範例

```javascript
try {
  const response = await fetch('http://localhost:8001/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: '你好' })
  });

  if (!response.ok) {
    const error = await response.json();
    console.error(`HTTP ${response.status}:`, error.detail);
    return;
  }

  const data = await response.json();
  console.log(data.message);
  
} catch (error) {
  console.error('網絡錯誤:', error.message);
}
```

---

## JavaScript/TypeScript SDK

MartletMolt 後端 API 客戶端 SDK，提供完整的 TypeScript 類型定義和使用範例。


### SDK 檔案: `MartletMoltClient.ts`

```typescript
// ============================================
// 類型定義
// ============================================

export interface HealthResponse {
  status: string;
  system: string;
  version: string;
}

export interface StatusResponse {
  system: string;
  active: boolean;
  tools: string[];
  provider: string;
  model: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  stream?: boolean;
}

export interface ChatResponse {
  message: string;
  session_id: string;
}

export interface SessionInfo {
  id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  tool_call_count: number;
  metadata: Record<string, any>;
}

export interface SessionListResponse {
  sessions: SessionInfo[];
  total: number;
}

export interface Message {
  id: string;
  role: string;
  content: string;
  name?: string | null;
  tool_call_id?: string | null;
  tool_calls?: any[] | null;
  timestamp: string;
}

export interface SessionDetailResponse {
  id: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
  tool_calls: any[];
  metadata: Record<string, any>;
}

export interface DeleteSessionResponse {
  success: boolean;
  message: string;
}

export interface ApiError {
  detail: string;
}


// ============================================
// SDK 類別
// ============================================

export class MartletMoltClient {
  private baseUrl: string;
  private timeout: number;

  /**
   * 建立客戶端實例
   * 
   * @param baseUrl - API 基礎 URL（預設: http://localhost:8001）
   * @param timeout - 請求超時時間（毫秒，預設: 30000）
   */
  constructor(baseUrl: string = 'http://localhost:8001', timeout: number = 30000) {
    this.baseUrl = baseUrl.replace(/\/$/, ''); // 移除結尾斜線
    this.timeout = timeout;
  }

  /**
   * 健康檢查
   * 
   * @returns 健康狀態
   */
  async health(): Promise<HealthResponse> {
    const response = await this.request('GET', '/health');
    return response.json();
  }

  /**
   * 取得系統狀態
   * 
   * @returns 系統狀態資訊
   */
  async status(): Promise<StatusResponse> {
    const response = await this.request('GET', '/status');
    return response.json();
  }

  /**
   * 同步對話
   * 
   * @param message - 用戶訊息
   * @param sessionId - 會話 ID（可選）
   * @returns AI 回應
   */
  async chat(message: string, sessionId?: string): Promise<ChatResponse> {
    const body: ChatRequest = { message };
    if (sessionId) body.session_id = sessionId;

    const response = await this.request('POST', '/chat', body);
    return response.json();
  }

  /**
   * 串流對話
   * 
   * @param message - 用戶訊息
   * @param sessionId - 會話 ID（可選）
   * @param onChunk - 接收數據塊的回調函數
   * @param onError - 錯誤處理回調函數（可選）
   */
  async chatStream(
    message: string,
    sessionId: string | undefined,
    onChunk: (chunk: string) => void,
    onError?: (error: string) => void
  ): Promise<void> {
    const body: ChatRequest = { message };
    if (sessionId) body.session_id = sessionId;

    const response = await this.request('POST', '/chat/stream', body);
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('無法讀取串流數據');
    }

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.substring(6).trim();
            
            if (data === '[DONE]') {
              return;
            } else if (data.startsWith('[ERROR]')) {
              const errorMsg = data.substring(8);
              if (onError) {
                onError(errorMsg);
              } else {
                throw new Error(errorMsg);
              }
            } else if (data) {
              onChunk(data);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * 列出所有會話
   * 
   * @returns 會話列表
   */
  async listSessions(): Promise<SessionListResponse> {
    const response = await this.request('GET', '/sessions');
    return response.json();
  }

  /**
   * 取得會話詳情
   * 
   * @param sessionId - 會話 ID
   * @returns 會話詳細資訊
   */
  async getSession(sessionId: string): Promise<SessionDetailResponse> {
    const response = await this.request('GET', `/sessions/${sessionId}`);
    return response.json();
  }

  /**
   * 刪除會話
   * 
   * @param sessionId - 會話 ID
   * @returns 刪除結果
   */
  async deleteSession(sessionId: string): Promise<DeleteSessionResponse> {
    const response = await this.request('DELETE', `/sessions/${sessionId}`);
    return response.json();
  }

  /**
   * 發送 HTTP 請求
   * 
   * @private
   */
  private async request(
    method: string,
    path: string,
    body?: any
  ): Promise<Response> {
    const url = `${this.baseUrl}${path}`;
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    options.signal = controller.signal;

    try {
      const response = await fetch(url, options);
      
      if (!response.ok) {
        const error: ApiError = await response.json();
        throw new Error(`HTTP ${response.status}: ${error.detail}`);
      }

      return response;
    } catch (error: any) {
      if (error.name === 'AbortError') {
        throw new Error('請求超時');
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }
}

```

---

## 使用範例

### Python 範例

```python
import requests

# 初始化客戶端
BASE_URL = "http://localhost:8001"

# 健康檢查
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# 同步對話
response = requests.post(
    f"{BASE_URL}/chat",
    json={"message": "你好", "session_id": "test-session"}
)
print(response.json())

# 串流對話
import sseclient  # pip install sseclient-py

response = requests.post(
    f"{BASE_URL}/chat/stream",
    json={"message": "寫一首詩", "session_id": "test-session"},
    stream=True
)

client = sseclient.SSEClient(response)
for event in client.events():
    if event.data == "[DONE]":
        break
    elif event.data.startswith("[ERROR]"):
        print(f"錯誤: {event.data[8:]}")
    else:
        print(event.data, end='', flush=True)
```

### Shell/cURL 範例

```bash
# 健康檢查
curl http://localhost:8001/health

# 系統狀態
curl http://localhost:8001/status

# 同步對話
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'

# 串流對話
curl -X POST http://localhost:8001/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "寫一首詩"}'

# 列出會話
curl http://localhost:8001/sessions

# 取得會話詳情
curl http://localhost:8001/sessions/default

# 刪除會話
curl -X DELETE http://localhost:8001/sessions/old-session
```

---

## 常見問題

### Q: 如何保持對話上下文？

**A**: 使用 `session_id` 參數即可。相同的 `session_id` 會共享對話歷史：

```javascript
// 第一次對話
await client.chat('我叫小明', 'my-session');

// 第二次對話（會記住之前說過的名字）
await client.chat('我叫什麼名字？', 'my-session');
```

### Q: 串流對話如何處理錯誤？

**A**: 監聽 `[ERROR]` 標記：

```javascript
await client.chatStream(
  '問題',
  'session-id',
  (chunk) => console.log(chunk),
  (error) => console.error('錯誤:', error)
);
```

### Q: 支援哪些 AI Provider？

**A**: 目前支援：
- **OpenAI** (GPT-4o, GPT-3.5 Turbo 等)
- **Anthropic** (Claude 系列)
- **Ollama** (本地模型)

### Q: 如何設定超時時間？

**A**: 在 SDK 初始化時設定：

```javascript
const client = new MartletMoltClient('http://localhost:8001', 60000); // 60 秒超時
```

### Q: 會話資料儲存在哪裡？

**A**: 預設使用本地檔案系統儲存，未來將支援：
- Redis
- PostgreSQL
- SQLite

---

## 更多資源

- [GitHub Repository](https://github.com/your-org/martletmolt)
- [Issue Tracker](https://github.com/your-org/martletmolt/issues)
- [Contributing Guide](../CONTRIBUTING.md)

---

**最後更新**: 2025-01-15  
**文件版本**: v0.1.0