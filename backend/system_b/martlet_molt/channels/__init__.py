"""
Channel 模組
統一不同通訊通道的介面
"""

from martlet_molt.channels.base import (
    BaseChannel,
    ChannelMessage,
    ChannelResponse,
    ChannelStatus,
)
from martlet_molt.channels.cli import CLIChannel
from martlet_molt.channels.web import WebChannel

__all__ = [
    # 基類
    "BaseChannel",
    "ChannelMessage",
    "ChannelResponse",
    "ChannelStatus",
    # 實現
    "CLIChannel",
    "WebChannel",
]
