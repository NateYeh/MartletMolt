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
  - [系統端點](#系統端點)
  - [對話端點](#對話端點)
  - [會話管理端點](#會話管理端點)
- [錯誤處理](#錯誤處理)
- [JavaScript/TypeScript SDK](#javascripttypescript-sdk)
- [使用範例](#使用範例)
- [常見問題](#常見問題)

---

## 概覽

MartletMolt 後端提供純 API 服務，支援 AI 對話功能。所有端點均返回 JSON 格式數據，並支援 CORS 跨域請求。

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
|------|------|------|
| `GET` | `/health` | 健康檢查 |
| `GET` | `/status` | 系統狀態 |

### 對話端點

| 方法 | 路徑 | 描述 | 是否串流 |
|------|------|------|----------|
| `POST` | `/chat` | 同步對話 | ❌ |
| `POST` | `/chat/stream` | 串流對話 | ✅ |

### 會話管理端點

| 方法 | 路徑 | 描述 |
|------|------|------|
| `GET` | `/sessions` | 列出所有會話 |
| `GET` | `/sessions/{session_id}` | 取得會話詳情 |
| `DELETE` | `/sessions/{session_id}` | 刪除會話 |

---

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
| `status` | `string` | 服務狀態（`"running"` 或 `"error"`） |
| `system` | `string` | 當前活躍系統名稱（`"SystemA"` 或 `"SystemB"`） |
| `version` | `string` | API 版本號 |

**狀態碼**:
- `200 OK`: 服務正常

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
  "system": "SystemA",
  "active": true,
  "tools": [
    "shell",
    "file_read",
    "file_write",
    "web_navigate",
    "web_extract"
  ],
  "provider": "openai",
  "model": "gpt-4o"
}
```

**回應欄位**:

| 欄位 | 類型 | 描述 |
|------|------|------|
| `system` | `string` | 當前活躍系統名稱 |
| `active` | `boolean` | 系統是否活躍 |
| `tools` | `array[string]` | 可用工具列表 |
| `provider` | `string` | 當前 AI Provider（`"openai"`, `"anthropic"`, `"ollama"`） |
| `model` | `string` | 當前使用的模型名稱 |

**狀態碼**:
- `200 OK`: 請求成功

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
  "message": "請幫我列出專案目錄結構",
  "session_id": "default"
}
```

**請求參數**:

| 參數 | 類型 | 必填 | 預設值 | 描述 |
|------|------|------|--------|------|
| `message` | `string` | ✅ | - | 用戶訊息內容 |
| `session_id` | `string` | ❌ | `"default"` | 會話 ID，用於持久化對話歷史 |
| `stream` | `boolean` | ❌ | `false` | 是否使用串流（此端點忽略此參數） |

**回應**:
```json
{
  "message": "好的，我幫您列出專案目錄結構...\n\n專案根目錄包含：\n- orchestrator/\n- system_a/\n- system_b/\n- frontend/\n- shared/\n- Config/",
  "session_id": "default"
}
```

**回應欄位**:

| 欄位 | 類型 | 描述 |
|------|------|------|
| `message` | `string` | AI 的完整回應 |
| `session_id` | `string` | 會話 ID（可能與請求不同，若請求未提供則自動生成） |

**狀態碼**:
- `200 OK`: 請求成功
- `400 Bad Request`: 請求參數錯誤
- `500 Internal Server Error`: 服務器內部錯誤

**範例**:
```javascript
// JavaScript 範例
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
  "message": "請寫一個 Python 快速排序算法",
  "session_id": "coding-session"
}
```

**請求參數**: 與 `/chat` 相同

**回應格式**: Server-Sent Events (SSE)

```
data: 這是

data: 一個

data: Python

data: 快速排序

data: 算法...

data: [DONE]
```

**SSE 訊息格式**:
- 正常訊息: `data: <chunk>\n\n`
- 結束標記: `data: [DONE]\n\n`
- 錯誤訊息: `data: [ERROR] <error_message>\n\n`

**狀態碼**:
- `200 OK`: 請求成功（開始串流）
- `400 Bad Request`: 請求參數錯誤
- `500 Internal Server Error`: 服務器內部錯誤

**範例**:
```javascript
// JavaScript 範例（使用 EventSource 或 fetch）
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

```

---

## 會話管理端點

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
      "id": "default",
      "created_at": "2025-01-15T10:00:00",
      "updated_at": "2025-01-15T10:30:00",
      "message_count": 10,
      "tool_call_count": 2,
      "metadata": {}
    },
    {
      "id": "coding-session",
      "created_at": "2025-01-15T09:00:00",
      "updated_at": "2025-01-15T11:00:00",
      "message_count": 25,
      "tool_call_count": 5,
      "metadata": {}
    }
  ],
  "total": 2
}
```

**回應欄位**:

| 欄位 | 類型 | 描述 |
|------|------|------|
| `sessions` | `array` | 會話列表 |
| `sessions[].id` | `string` | 會話 ID |
| `sessions[].created_at` | `string` | 建立時間（ISO 8601） |
| `sessions[].updated_at` | `string` | 最後更新時間（ISO 8601） |
| `sessions[].message_count` | `integer` | 訊息數量 |
| `sessions[].tool_call_count` | `integer` | 工具調用次數 |
| `sessions[].metadata` | `object` | 會話元數據 |
| `total` | `integer` | 總會話數 |

**狀態碼**:
- `200 OK`: 請求成功

---

### 6. 取得會話詳情

**端點**: `GET /sessions/{session_id}`

**描述**: 取得指定會話的詳細資訊，包含完整的訊息歷史

**請求**:
```http
GET /sessions/default HTTP/1.1
Host: localhost:8001
```

**路徑參數**:

| 參數 | 類型 | 描述 |
|------|------|------|
| `session_id` | `string` | 會話 ID |

**回應**:
```json
{
  "id": "default",
  "created_at": "2025-01-15T10:00:00",
  "updated_at": "2025-01-15T10:30:00",
  "messages": [
    {
      "id": "msg123",
      "role": "user",
      "content": "你好",
      "name": null,
      "tool_call_id": null,
      "tool_calls": null,
      "timestamp": "2025-01-15T10:00:00"
    },
    {
      "id": "msg456",
      "role": "assistant",
      "content": "你好！有什麼我可以幫你的嗎？",
      "name": null,
      "tool_call_id": null,
      "tool_calls": null,
      "timestamp": "2025-01-15T10:00:05"
    }
  ],
  "tool_calls": [],
  "metadata": {}
}
```

**回應欄位**:

| 欄位 | 類型 | 描述 |
|------|------|------|
| `id` | `string` | 會話 ID |
| `created_at` | `string` | 建立時間（ISO 8601） |
| `updated_at` | `string` | 最後更新時間（ISO 8601） |
| `messages` | `array` | 完整訊息列表 |
| `messages[].id` | `string` | 訊息 ID |
| `messages[].role` | `string` | 角色（`user`, `assistant`, `system`, `tool`） |
| `messages[].content` | `string` | 訊息內容 |
| `messages[].timestamp` | `string` | 訊息時間戳（ISO 8601） |
| `tool_calls` | `array` | 工具調用記錄 |
| `metadata` | `object` | 會話元數據 |

**狀態碼**:
- `200 OK`: 請求成功
- `404 Not Found`: 會話不存在

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
DELETE /sessions/default HTTP/1.1
Host: localhost:8001
```

**路徑參數**:

| 參數 | 類型 | 描述 |
|------|------|------|
| `session_id` | `string` | 會話 ID |

**回應**:
```json
{
  "success": true,
  "message": "Session 'default' deleted successfully"
}
```

**回應欄位**:

| 欄位 | 類型 | 描述 |
|------|------|------|
| `success` | `boolean` | 是否成功刪除 |
| `message` | `string` | 操作結果訊息 |

**狀態碼**:
- `200 OK`: 刪除成功
- `404 Not Found`: 會話不存在

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
| `400 Bad Request` | 請求參數錯誤 | 缺少必填欄位、格式錯誤 |
| `404 Not Found` | 找不到資源 | 錯誤的 API 路徑 |
| `422 Unprocessable Entity` | 數據驗證失敗 | JSON 格式錯誤、欄位類型不符 |
| `500 Internal Server Error` | 服務器內部錯誤 | Provider API 錯誤、系統異常 |
| `503 Service Unavailable` | 服務不可用 | 系統維護中、過載 |

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

以下提供完整的 JavaScript/TypeScript SDK 封裝：

### SDK 檔案: `MartletMoltClient.ts`

```typescript
/**
 * MartletMolt 後端 API 客戶端 SDK
 * 
 * @version 0.1.0
 * @author MartletMolt Team
 */

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

// ============================================
// 使用範例
// ============================================

/**
 * 範例 1: 基本對話
 */
async function exampleBasicChat() {
  const client = new MartletMoltClient();
  
  const response = await client.chat('你好，請介紹一下你自己');
  console.log('AI 回應:', response.message);
  console.log('會話 ID:', response.session_id);
}

/**
 * 範例 2: 串流對話
 */
async function exampleStreamChat() {
  const client = new MartletMoltClient();
  
  console.log('AI: ');
  await client.chatStream(
    '寫一個 Python 快速排序算法',
    'coding-session',
    (chunk) => {
      process.stdout.write(chunk); // 即時輸出
    },
    (error) => {
      console.error('錯誤:', error);
    }
  );
  console.log('\n');
}

/**
 * 範例 3: 持續對話（使用 session_id）
 */
async function exampleContinuousChat() {
  const client = new MartletMoltClient();
  const sessionId = 'my-conversation-123';

  // 第一次對話
  const response1 = await client.chat('我叫小明', sessionId);
  console.log('AI:', response1.message);

  // 第二次對話（會記住上下文）
  const response2 = await client.chat('我叫什麼名字？', sessionId);
  console.log('AI:', response2.message); // 應該會回答「小明」
}

/**
 * 範例 4: 檢查系統狀態
 */
async function exampleCheckStatus() {
  const client = new MartletMoltClient();
  
  const health = await client.health();
  console.log('服務狀態:', health.status);
  console.log('系統:', health.system);

  const status = await client.status();
  console.log('可用的工具:', status.tools);
  console.log('當前模型:', status.model);
}

/**
 * 範例 5: 會話管理
 */
async function exampleSessionManagement() {
  const client = new MartletMoltClient();

  // 列出所有會話
  const sessions = await client.listSessions();
  console.log('總會話數:', sessions.total);
  sessions.sessions.forEach(session => {
    console.log(`- ${session.id}: ${session.message_count} 條訊息`);
  });

  // 取得特定會話詳情
  const sessionDetail = await client.getSession('my-session');
  console.log('會話 ID:', sessionDetail.id);
  sessionDetail.messages.forEach(msg => {
    console.log(`[${msg.role}] ${msg.content}`);
  });

  // 刪除會話
  const result = await client.deleteSession('old-session');
  console.log(result.message);
}
```

---

## 使用範例

## 使用範例

### Python 範例

```python
import requests
import json

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
        break
    else:
        print(event.data, end="", flush=True)
```

### cURL 範例

```bash
# 健康檢查
curl http://localhost:8001/health

# 系統狀態
curl http://localhost:8001/status

# 同步對話
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "session_id": "test"}'

# 串流對話
curl -X POST http://localhost:8001/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "寫一首詩"}' \
  --no-buffer

# 列出所有會話
curl http://localhost:8001/sessions

# 取得會話詳情
curl http://localhost:8001/sessions/default

# 刪除會話
curl -X DELETE http://localhost:8001/sessions/old-session
```

---

## 常見問題

### Q1: 如何持久化對話歷史？

**A**: 使用 `session_id` 參數。相同 `session_id` 的對話會被保存，AI 會記住上下文。

```javascript
// 第一次對話
await client.chat('我叫小明', 'user-123');

// 第二次對話（AI 會記住你的名字）
await client.chat('我叫什麼？', 'user-123');
```

### Q2: 串流和同步模式如何選擇？

**A**: 
- **同步模式 (`/chat`)**: 適合短訊息、需要完整回應的場景
- **串流模式 (`/chat/stream`)**: 適合長篇回應、即時顯示的場景

### Q3: 如何處理 CORS 錯誤？

**A**: 後端已啟用 CORS，允許跨域請求。若仍有問題，請檢查：
1. Base URL 是否正確
2. 是否有代理服務器限制

### Q4: 請求超時怎麼辦？

**A**: 可以在 SDK 中設置更長的超時時間：

```javascript
const client = new MartletMoltClient('http://localhost:8001', 60000); // 60秒
```

### Q5: 如何獲取可用的工具列表？

**A**: 調用 `/status` 端點：

```javascript
const status = await client.status();
console.log('可用工具:', status.tools);
```

### Q6: 支援哪些 AI Provider？

**A**: 目前支援：
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Ollama (本地模型)

可在 `Config/settings.yaml` 中配置。

---

## 更新日誌

### v0.1.0 (2025-01-15)
- ✨ 初始版本
- ✅ 基礎 API 端點（健康檢查、狀態、對話）
- ✅ 串流對話支援
- ✅ 會話管理
- ✅ JavaScript/TypeScript SDK

---

## 相關連結

- [專案文檔](./AI_CONTEXT.md)
- [前端開發指南](../frontend/README.md)
- [配置說明](./config_templates/README.md)
- [GitHub](https://github.com/NateYeh/MartletMolt)

---

## 支援與反饋

如有問題或建議，請：
1. 查看專案 [Issues](https://github.com/NateYeh/MartletMolt/issues)
2. 提交新的 Issue
3. 聯繫開發團隊

---

**📚 完整 API 文件**: 可訪問 `http://localhost:8001/docs` 查看 FastAPI 自動生成的交互式 API 文件（Swagger UI）。