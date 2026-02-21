"""
系統狀態管理
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from orchestrator.config import settings


class SystemHealth(BaseModel):
    """系統健康狀態"""

    status: Literal["running", "stopped", "error", "synced"]
    uptime: int = 0  # 運行時間（秒）
    last_check: str | None = None
    error_message: str = ""


class SystemVersion(BaseModel):
    """系統版本資訊"""

    a: str = "0.1.0"
    b: str = "0.1.0"


class State(BaseModel):
    """系統狀態"""

    active: Literal["a", "b"] = "a"
    version: SystemVersion = SystemVersion()
    last_switch: str | None = None
    health_status: dict[str, SystemHealth] = {
        "a": SystemHealth(status="stopped"),
        "b": SystemHealth(status="synced"),
    }


class StateManager:
    """狀態管理器"""

    def __init__(self, state_file: Path | None = None):
        self.state_file = state_file or settings.state_file
        self._state: State | None = None

    @property
    def state(self) -> State:
        """取得當前狀態"""
        if self._state is None:
            self._state = self._load_state()
        return self._state

    def _load_state(self) -> State:
        """從檔案載入狀態"""
        if not self.state_file.exists():
            return State()

        try:
            with open(self.state_file, encoding="utf-8") as f:
                data = json.load(f)
            return State(**data)
        except Exception:
            return State()

    def _save_state(self) -> None:
        """儲存狀態到檔案"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state.model_dump(), f, indent=2, ensure_ascii=False)

    def get_active_system(self) -> str:
        """取得當前活躍的系統"""
        return self.state.active

    def get_inactive_system(self) -> str:
        """取得當前非活躍的系統"""
        return "b" if self.state.active == "a" else "a"

    def switch_active(self) -> str:
        """切換活躍系統"""
        old_active = self.state.active
        self.state.active = "b" if old_active == "a" else "a"
        self.state.last_switch = datetime.now().isoformat()
        self._save_state()
        return self.state.active

    def update_health(self, system: str, health: SystemHealth) -> None:
        """更新系統健康狀態"""
        self.state.health_status[system] = health
        self._save_state()

    def update_version(self, system: str, version: str) -> None:
        """更新系統版本"""
        setattr(self.state.version, system, version)
        self._save_state()


# 全域狀態管理器
state_manager = StateManager()
