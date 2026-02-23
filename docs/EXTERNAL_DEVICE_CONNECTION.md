# MartletMolt 外部裝置連線指南 (External Device Connection Guide) - V2

本文件說明如何讓外部硬體（如 ESP32、樹莓派、或其他伺服器）連線至 MartletMolt 後端。為了區分相同硬體的裝置並確保安全性，我們採用了「金鑰驗證」與「動態識別」機制。

---

## 1. 通訊協議概覽

- **協議**: WebSocket
- **數據格式**: JSON (UTF-8)
- **連線位址**: `ws://<SERVER_IP>:8001/ws/devices`
- **必備參數**:
    - `key`: 系統生成的萬能鑰匙 (必須)。
    - `device_id`: 裝置識別碼 (可選)。初次連線請忽略，由伺服器分配。

---

## 2. 身份核對流程 (Authentication Flow)

### 第一階段：初次連線 (配對)
若裝置尚未擁有 `device_id`，請僅帶入 `key` 連線：
`ws://<SERVER_IP>:8001/ws/devices?key=YOUR_GLOBAL_KEY`

**伺服器回應 (Assignment Event):**
後端會立即核發一個 ID 給你：
```json
{
  "type": "assignment",
  "device_id": "device-a1b2c3d4",
  "message": "請儲存此 ID 並在下次連線時使用。"
}
```
*裝置必須將此 `device_id` 永久存儲在本地（如 NVS, SPIFFS, 或 .env 文件）。*

### 第二階段：正式連線 (識別)
擁有 ID 後，請使用以下網址連線：
`ws://<SERVER_IP>:8001/ws/devices?key=YOUR_GLOBAL_KEY&device_id=device-a1b2c3d4`

---

## 3. 功能註冊與通訊

連線驗證成功後，裝置需按照以下步驟操作：

### 步驟 A：發送註冊封包
```json
{
  "type": "register",
  "capabilities": [
    {
      "name": "toggle_light",
      "description": "控制客廳電燈開關",
      "parameters": {
        "type": "object",
        "properties": { "state": { "type": "boolean" } },
        "required": ["state"]
      }
    }
  ]
}
```

### 步驟 B：接收驗證確認
```json
{
  "type": "verified",
  "device_id": "device-a1b2c3d4",
  "message": "Welcome to MartletMolt Hive!"
}
```

---

## 4. 指令與回饋 (與 V1 相同)

### 接收指令 (Backend -> Device)
```json
{ "type": "execute", "method": "toggle_light", "params": { "state": true } }
```

### 回報結果 (Device -> Backend)
```json
{ "type": "result", "data": "OK" }
```

---

## 5. 安全性與維護

1. **更新金鑰**: 管理員可以執行 `scripts/generate_device_key.py` 來更換全球萬能鑰匙。一旦更換，所有舊裝置需更新 key 才能連線。
2. **裝置管理**: 註冊過的裝置資訊存儲於 `shared/data/registered_devices.json`，若要強迫裝置重新配對，只需從該 JSON 中刪除對應的 ID。
3. **心跳**: 建議每 30 秒發送一次 `{"type": "pong"}` 以維持 WebSocket 通道。
