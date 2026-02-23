import json
import os
import uuid
from typing import Any
from pathlib import Path
from loguru import logger

class DevicePersistence:
    """處理裝置資訊的持久化存儲 (JSON 檔案)"""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        # 結構: { "devices": { "device_id": { "first_seen": "...", "caps": [] } } }
        self.data = {"devices": {}}
        self._load()

    def _load(self):
        if self.data_path.exists():
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                logger.error(f"無法讀取裝置存儲檔案: {e}")

    def save(self):
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def is_registered(self, device_id: str) -> bool:
        return device_id in self.data.get("devices", {})

    def register_new_device(self) -> str:
        new_id = f"device-{uuid.uuid4().hex[:8]}"
        self.data["devices"][new_id] = {
            "version": "1.0",
            "assigned_at": str(uuid.uuid4()) # 這裡僅作記錄
        }
        self.save()
        return new_id

from .config import settings

# 實例化存儲 (從 settings 獲取路徑)
persistence = DevicePersistence(settings.base_dir / settings.data_dir / "registered_devices.json")
