# MartletMolt 外部裝置連線指南 (External Device Connection Guide)

本文件說明如何讓外部硬體（如 ESP32、樹莓派、或其他伺服器）連線至 MartletMolt 後端，並將其功能映射為 Agent 可調用的「超能力」。

---

## 1. 通訊協議概覽

- **協議**: WebSocket
- **數據格式**: JSON (UTF-8)
- **連線位址**: `ws://<SERVER_IP>:8001/ws/devices/<DEVICE_ID>`
    - `<SERVER_IP>`: 後端伺服器 IP。
    - `<DEVICE_ID>`: 你的裝置唯一識別碼（例如 `living-room-esp32`）。

---

## 2. 連線與註冊流程

連線建立後，裝置必須在第一時間發送 **註冊資訊**，否則連線會被自動斷開。

### 第一步：發送註冊封包
裝置需定義其具備的功能清單（capabilities），格式與 OpenAI Tool Definition 相似。

**請求範例 (Device -> Backend):**
```json
{
  "type": "register",
  "capabilities": [
    {
      "name": "toggle_light",
      "description": "控制客廳電燈開關",
      "parameters": {
        "type": "object",
        "properties": {
          "state": { "type": "boolean", "description": "True 表示開燈，False 表示關燈" }
        },
        "required": ["state"]
      }
    },
    {
      "name": "get_temperature",
      "description": "讀取當前環境溫度",
      "parameters": {
        "type": "object",
        "properties": {}
      }
    }
  ]
}
```

### 第二步：接收驗證確認
如果註冊成功，後端會回傳驗證成功的訊息。

**回應範例 (Backend -> Device):**
```json
{
  "type": "verified",
  "message": "Welcome to MartletMolt Hive!"
}
```

---

## 3. 指令執行與回饋

當 MartletMolt 的 Agent 決定使用你的裝置功能時，後端會發送執行指令。

### 接收執行指令 (Backend -> Device)
**封包範例:**
```json
{
  "type": "execute",
  "method": "toggle_light",
  "params": {
    "state": true
  }
}
```

### 回傳執行結果 (Device -> Backend)
裝置處理完指令後，應回報執行結果。

**回報範例:**
```json
{
  "type": "result",
  "data": "燈已成功開啟"
}
```
*註：`data` 可以是字串或結構化 JSON，這將作為 Agent 觀察到的執行結果。*

---

## 4. 維護連線 (Heartbeat)

雖然 WebSocket 本身有 Ping/Pong 機制，但為了保持穩定性，建議裝置定期發送輕量封包。

**心跳範例 (Device -> Backend):**
```json
{
  "type": "pong"
}
```

---

## 5. 安全性 (Security)

目前的開發階段支援透過 Query Parameter 帶入 Token：
`ws://<SERVER_IP>:8001/ws/devices/<DEVICE_ID>?token=your_secret_token`

> ⚠️ **注意**：目前後端僅預留 Token 驗證邏輯，尚未強制啟用，建議在受信任的內網環境測試。

---

## 6. Python 模擬客戶端範例

以下是一個簡單的 Python 腳本，可用於測試連線：

```python
import asyncio
import websockets
import json

async def mock_device():
    uri = "ws://localhost:8001/ws/devices/test-python-device"
    async with websockets.connect(uri) as websocket:
        # 註冊
        reg = {
            "type": "register",
            "capabilities": [{
                "name": "say_hello",
                "description": "讓裝置打招呼",
                "parameters": {"type": "object", "properties": {"name": {"type": "string"}}}
            }]
        }
        await websocket.send(json.dumps(reg))
        
        while True:
            msg = await websocket.recv()
            data = json.loads(msg)
            
            if data.get("type") == "execute":
                method = data.get("method")
                params = data.get("params")
                print(f"收到指令: {method} 參數: {params}")
                
                # 回報結果
                result = {"type": "result", "data": f"Hello {params.get('name', 'stranger')}, I am a mock device!"}
                await websocket.send(json.dumps(result))

asyncio.run(mock_device())
```
