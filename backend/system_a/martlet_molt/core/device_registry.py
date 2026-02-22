import json
from collections.abc import Awaitable, Callable
from typing import Any

from loguru import logger


class DeviceRegistry:
    """
    裝置註冊中心：負責管理遠端 IoT 裝置的連線狀態與能力清單。
    """
    def __init__(self):
        # 存儲格式: { device_id: { "capabilities": [...], "send_func": async_callable } }
        self._devices: dict[str, dict[str, Any]] = {}
        logger.info("DeviceRegistry 初始完成，準備接收裝置投誠。")

    async def register(self, device_id: str, capabilities: list[dict[str, Any]], send_func: Callable[[str], Awaitable[None]]):
        """
        註冊一個新裝置及其能力。
        capabilities 格式範例: 
        [{"name": "toggle_light", "description": "開關燈", "parameters": {"type": "object", "properties": {"state": {"type": "boolean"}}}}]
        """
        self._devices[device_id] = {
            "capabilities": capabilities,
            "send_func": send_func
        }
        logger.info(f"裝置註冊成功: {device_id}，擁有 {len(capabilities)} 個超能力！")

    def unregister(self, device_id: str):
        """註冊裝置移除。"""
        if device_id in self._devices:
            del self._devices[device_id]
            logger.info(f"裝置已移除: {device_id}")

    def get_active_devices(self) -> list[str]:
        """獲取目前在線的裝置 ID 列表。"""
        return list(self._devices.keys())

    def get_all_capabilities(self) -> list[dict[str, Any]]:
        """獲取所有在線裝置的能力，並按裝置 ID 標註。"""
        all_caps = []
        for did, info in self._devices.items():
            for cap in info["capabilities"]:
                # 複製並注入 device_id 資訊，方便後端識別
                enriched_cap = cap.copy()
                enriched_cap["device_id"] = did
                all_caps.append(enriched_cap)
        return all_caps

    async def execute_command(self, device_id: str, method: str, params: dict[str, Any]) -> bool:
        """
        向指定裝置發送執行指令。
        """
        if device_id not in self._devices:
            logger.warning(f"嘗試控制不存在的裝置: {device_id}")
            return False

        payload = {
            "type": "execute",
            "method": method,
            "params": params
        }

        try:
            await self._devices[device_id]["send_func"](json.dumps(payload))
            logger.info(f"指令已發送至 {device_id}: {method}({params})")
            return True
        except Exception:
            logger.exception(f"發送指令至裝置 {device_id} 時發生意外故障")
            return False

# 全域單例
device_registry = DeviceRegistry()
