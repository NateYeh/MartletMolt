"""
Channel 抽象基類
統一不同通訊通道的介面
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class ChannelStatus(StrEnum):
    """Channel 狀態"""

    IDLE = "idle"  # 待機中
    RUNNING = "running"  # 運行中
    ERROR = "error"  # 錯誤
    STOPPED = "stopped"  # 已停止


class ChannelMessage(BaseModel):
    """統一的訊息格式"""

    content: str  # 訊息內容
    user_id: str = ""  # 用戶 ID
    session_id: str = ""  # 會話 ID
    metadata: dict[str, Any] = {}  # 額外資訊（平台、時間戳等）


class ChannelResponse(BaseModel):
    """統一的回應格式"""

    content: str  # 回應內容
    success: bool = True  # 是否成功
    error: str = ""  # 錯誤訊息
    metadata: dict[str, Any] = {}  # 額外資訊


class BaseChannel(ABC):
    """
    Channel 抽象基類

    統一不同通訊通道（CLI、Web、Discord 等）的介面，
    讓 Agent 可以用一致的方式處理不同來源的訊息。

    實現範例：
        - CLIChannel: 命令行互動
        - WebChannel: WebSocket 通訊
        - DiscordChannel: Discord 機器人
        - SlackChannel: Slack 機器人
    """

    # ============ 基本屬性 ============

    id: str = ""  # Channel 唯一標識
    name: str = ""  # Channel 名稱
    description: str = ""  # Channel 描述

    _status: ChannelStatus = ChannelStatus.IDLE

    # ============ 抽象方法（必須實現）============

    @abstractmethod
    async def receive(self) -> AsyncIterator[ChannelMessage]:
        """
        接收訊息（非同步迭代器）

        Yields:
            ChannelMessage: 接收到的訊息
        """
        pass

    @abstractmethod
    async def send(self, response: ChannelResponse) -> bool:
        """
        發送回應

        Args:
            response: 回應內容

        Returns:
            bool: 是否發送成功
        """
        pass

    # ============ 可選方法（有預設實現）============

    async def start(self) -> bool:
        """
        啟動 Channel

        Returns:
            bool: 是否啟動成功
        """
        self._status = ChannelStatus.RUNNING
        return True

    async def stop(self) -> bool:
        """
        停止 Channel

        Returns:
            bool: 是否停止成功
        """
        self._status = ChannelStatus.STOPPED
        return True

    async def health_check(self) -> bool:
        """
        健康檢查

        Returns:
            bool: 是否健康
        """
        return self._status == ChannelStatus.RUNNING

    # ============ 屬性訪問 ============

    @property
    def status(self) -> ChannelStatus:
        """取得當前狀態"""
        return self._status

    @property
    def is_running(self) -> bool:
        """是否正在運行"""
        return self._status == ChannelStatus.RUNNING
