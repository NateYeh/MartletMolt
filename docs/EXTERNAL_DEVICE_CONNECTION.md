# MartletMolt 外部裝置連線指南 (External Device Connection Guide) - V3 (Secure Header Edition)

本文件說明如何讓外部硬體連線至 MartletMolt 後端。為了最高安全性，我們不使用網址傳遞密鑰，而是透過 **HTTP Headers**。

---

## 1. 通訊協議概覽

- **協議**: WebSocket
- **數據格式**: JSON (UTF-8)
- **連線位址**: `ws://<SERVER_IP>:8001/ws/devices`
- **必備 Headers**:
    - `X-Device-Key`: 系統生成的萬能鑰匙 (必須)。
    - `X-Device-ID`: 裝置識別碼 (可選)。初次連線請忽略。

---

## 2. 身份核對流程

### 第一階段：初次連線 (配對)
裝置連線時僅帶入 `X-Device-Key` Header。

**伺服器回應 (Assignment Event):**
後端會立即核發一個 ID 給你：
```json
{
  "type": "assignment",
  "device_id": "device-a1b2c3d4",
  "message": "請儲存此 ID 並在下次連線時於 Header 中帶入 X-Device-ID。"
}
```

### 第二階段：正式連線 (識別)
擁有 ID 後，連線時請帶入兩個 Headers：
1. `X-Device-Key: YOUR_GLOBAL_KEY`
2. `X-Device-ID: device-a1b2c3d4`

---

## 3. Python 測試範例 (使用 Header)

```python
import asyncio
import websockets
import json

async def connect_device():
    uri = "ws://localhost:8001/ws/devices"
    headers = {
        "X-Device-Key": "-ZmE8QvCPnOsgWwcZfOndUn0HMhLDiaDFA12n5sksz4",
        # "X-Device-ID": "device-previous-id"  # 如果已有 ID 則帶入
    }
    
    async with websockets.connect(uri, extra_headers=headers) as websocket:
        # 1. 處理配對與註冊...
        pass

asyncio.run(connect_device())
```

---

## 4. 安全優點
1. **防日誌洩漏**: URL 保持簡潔，敏感金鑰不會出現在伺服器訪問日誌中。
2. **防緩存劫持**: Headers 內容不會被瀏覽器歷史紀錄或 proxy 緩存。
3. **隱蔽性**: 在網路監控中，Payload 與 Header 都受到 TLS 加密（若使用 WSS），比 URL 參數更隱蔽。
