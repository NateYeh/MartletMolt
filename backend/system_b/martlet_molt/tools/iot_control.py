import asyncio
from typing import Any

from loguru import logger

from martlet_molt.core.device_registry import device_registry
from martlet_molt.tools.base import BaseTool, ToolResult


class IOTControlTool(BaseTool):
    """
    IoT 裝置控制工具。
    讓 Agent 能透過此工具向已連線的遠端裝置發送指令。
    """
    name = "iot_control"
    description = (
        "控制已連線的遠端 IoT 裝置。你可以使用此工具執行特定的裝置操作，"
        "如開關燈、調整空調溫度、讀取傳感器數值等。"
        "使用前可以先詢問當前有哪些可用裝置。"
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "device_id": {
                "type": "string",
                "description": "目標裝置的 ID。"
            },
            "method": {
                "type": "string",
                "description": "要對裝置執行的動作名稱 (例如 'toggle_light' 或 'set_brightness')。"
            },
            "params": {
                "type": "object",
                "description": "該動作所需的參數鍵值對。"
            }
        },
        "required": ["device_id", "method"]
    }

    def execute(self, device_id: str, method: str, params: dict[str, Any] = None) -> ToolResult:
        """同步執行 IOT 指令發送"""
        params = params or {}
        logger.info(f"Agent 調用 IOT 控制: device={device_id}, method={method}, params={params}")

        try:
            # 由於 ToolRegistry.execute 是在同步環境調用的，這裡我們需要啟動事件迴圈來跑異步任務
            # 注意：在 FastAPI 環境下，通常已經有 running loop，這裡用 run_coroutine_threadsafe 或直接 run
            # 為了簡單與安全，我們先嘗試從 registry 發送
            loop = asyncio.get_event_loop()

            if loop.is_running():
                # 如果 loop 正在跑（FastAPI 環境），建立任務
                # 這裡可能會有 block 的風險，但在簡單指令下可以接受
                # 未來可優化為讓 Tool 層原生支援 async
                coro = device_registry.execute_command(device_id, method, params)
                future = asyncio.run_coroutine_threadsafe(coro, loop)
                success = future.result(timeout=5)  # 等待 5 秒超時
            else:
                success = asyncio.run(device_registry.execute_command(device_id, method, params))

            if success:
                return ToolResult(
                    success=True,
                    data=f"Success: Instruction '{method}' sent to device '{device_id}'."
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"Failed to send command to '{device_id}'. Device might be offline."
                )
        except Exception as e:
            logger.exception("IOTControlTool 執行異常")
            return ToolResult(success=False, error=f"Internal Error: {str(e)}")
