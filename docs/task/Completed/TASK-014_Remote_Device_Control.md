# TASK-014: 遠端裝置動態註冊與控制系統 (已啟動 ⏳)

## 📋 任務資訊
- **任務編號**: TASK-014
- **優先級**: 高
- **負責人**: MartletMolt (Your Dev Bestie)
- **建立日期**: 2025-02-22
- **目標**: 實作一個基於 WebSocket 的動態裝置註冊機制，讓遠端硬體能主動連線並被 MartletMolt 調度。

---

## 🏗️ 技術規格

### 1. 通訊架構 (Gateway)
- **路徑**: `backend/system_x/martlet_molt/gateway/device_handler.py`
- **協議**: WebSocket
- **端點**: `/ws/devices/{device_id}`
- **安全**: 簡易 Token 驗證 (初步實作，預留擴展介面)

### 2. 註冊中心 (Core)
- **路徑**: `backend/system_x/martlet_molt/core/device_registry.py`
- **功能**:
    - 維持在線裝置清單 (記憶體內，未來可選 Redis)。
    - 存儲裝置的能力清單 (Methods, Parameters, Docstrings)。
    - 處理裝置心跳 (Heartbeat) 與斷線清理。

### 3. 動態工具映射 (Tools)
- **路徑**: `backend/system_x/martlet_molt/tools/device_tool.py`
- **邏輯**:
    - 定義一個 `RemoteDeviceDispatcher` 類。
    - 當 Agent 請求 `get_tools` 時，掃描 `DeviceRegistry` 並將每個裝置的方法封裝成符合 OpenAI 工具規範的 JSON。
    - 轉發 Agent 的工具調用指令至對應的 WebSocket 通道。

---

## 📂 修改路徑清單
- `backend/system_x/martlet_molt/gateway/device_handler.py` (New)
- `backend/system_x/martlet_molt/core/device_registry.py` (New)
- `backend/system_x/martlet_molt/tools/device_tool.py` (New)
- `backend/system_x/martlet_molt/main.py` (修改以掛載新的 WS 路由)

---

## ✅ 驗證方式
1. **Mock Device 測試**: 撰寫一個簡單的 Python 腳本模擬 ESP32，連線後註冊一個 `toggle_light(state: bool)` 方法。
2. **詢問 Agent**: 問 MartletMolt：「現在有哪些可用裝置？」，應返回 Mock 裝置資訊。
3. **執行控制**: 指令 MartletMolt：「幫我關燈」，Mock 裝置應收到對應的 JSON 指令。

---

## 📝 備註
- 第一階段不處理跨 Session 的長連接，以穩定性與動態註冊邏輯為優先。
