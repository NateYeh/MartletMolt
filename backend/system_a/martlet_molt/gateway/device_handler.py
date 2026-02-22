import json

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from loguru import logger

from ..core.device_registry import device_registry

router = APIRouter()

@router.websocket("/ws/devices/{device_id}")
async def device_websocket_handler(
    websocket: WebSocket,
    device_id: str,
    token: str | None = Query(None)
):
    """
    IoT 裝置專用的 WebSocket 入口。
    裝置連線後需主動發送註冊資訊。
    """
    # 簡易驗證 (雷，目前先留個坑，你可以之後在 Config 加入金鑰驗證)
    # if token != EXPECTED_TOKEN:
    #     await websocket.close(code=4003)
    #     return

    await websocket.accept()
    logger.info(f"裝置 {device_id} 已連線，等待註冊資訊...")

    try:
        # 第一步：等待註冊封包
        # 預期格式: {"type": "register", "capabilities": [...]}
        data = await websocket.receive_text()
        payload = json.loads(data)

        if payload.get("type") == "register":
            capabilities = payload.get("capabilities", [])

            # 定義發送函數給 Registry 使用
            async def send_to_device(message: str):
                await websocket.send_text(message)

            await device_registry.register(device_id, capabilities, send_to_device)
            await websocket.send_text(json.dumps({"type": "verified", "message": "Welcome to MartletMolt Hive!"}))
        else:
            logger.warning(f"裝置 {device_id} 未送出正確註冊資訊，即將斷開。")
            await websocket.close(code=1003)
            return

        # 第二步：維持連線並聆聽回傳或心跳
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # 這裡可以擴展處理裝置回傳的執行結果 (result) 或心跳 (ping)
            if message.get("type") == "pong":
                logger.debug(f"裝置 {device_id} 心跳正常。")
            elif message.get("type") == "result":
                logger.info(f"裝置 {device_id} 回報執行結果: {message.get('data')}")

    except WebSocketDisconnect:
        logger.info(f"裝置 {device_id} 已斷開連線。")
    except Exception:
        logger.exception(f"裝置 {device_id} 通訊發生意外。")
    finally:
        device_registry.unregister(device_id)
