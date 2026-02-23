import json
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from loguru import logger

from ..core.device_registry import device_registry
from ..core.config import settings
from ..core.device_persistence import persistence

router = APIRouter()

@router.websocket("/ws/devices")
async def device_websocket_handler(
    websocket: WebSocket, 
    key: str = Query(None), 
    device_id: str = Query(None)
):
    """
    IoT 裝置專用的 WebSocket 入口。
    
    兩層驗證：
    1. key: 全域萬能鑰匙 (必需)
    2. device_id: 裝置識別碼 (可選，新裝置則由伺服器分配)
    """
    
    # --- 第一道防線：萬能鑰匙驗證 ---
    if not settings.gateway.device_key:
        logger.warning("系統未設定 device_key，拒絕所有裝置連線。")
        await websocket.close(code=4003) # Forbidden
        return

    if key != settings.gateway.device_key:
        logger.warning(f"攔截到錯誤的連線金鑰: {key}")
        await websocket.close(code=4003)
        return

    await websocket.accept()

    # --- 第二道防線：身份識別與分配 ---
    current_device_id = device_id
    
    if not current_device_id or not persistence.is_registered(current_device_id):
        # 如果是新裝置或 ID 無效，分配一個新 ID
        current_device_id = persistence.register_new_device()
        logger.info(f"偵測到新裝置，分配 ID: {current_device_id}")
        # 主動告知裝置它的新身份
        await websocket.send_text(json.dumps({
            "type": "assignment",
            "device_id": current_device_id,
            "message": "請儲存此 ID 並在下次連線時使用 ?device_id= 參數帶入。"
        }))
    else:
        logger.info(f"裝置 {current_device_id} (老朋友) 已連線。")

    try:
        # 第一步：等待能力註冊封包
        data = await websocket.receive_text()
        payload = json.loads(data)

        if payload.get("type") == "register":
            capabilities = payload.get("capabilities", [])

            async def send_to_device(message: str):
                await websocket.send_text(message)

            await device_registry.register(current_device_id, capabilities, send_to_device)
            await websocket.send_text(json.dumps({
                "type": "verified", 
                "device_id": current_device_id,
                "message": "Welcome to MartletMolt Hive!"
            }))
        else:
            logger.warning(f"裝置 {current_device_id} 未送出正確註冊資訊，即將斷開。")
            await websocket.close(code=1003)
            return

        # 第二步：維持連線循環
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "pong":
                logger.debug(f"裝置 {current_device_id} 心跳正常。")
            elif message.get("type") == "result":
                logger.info(f"裝置 {current_device_id} 回報執行結果: {message.get('data')}")

    except WebSocketDisconnect:
        logger.info(f"裝置 {current_device_id} 已斷開連線。")
    except Exception:
        logger.exception(f"裝置 {current_device_id} 通訊發生意外。")
    finally:
        device_registry.unregister(current_device_id)
