"""
CLI Channel 實現
命令行互動通道
"""

import asyncio
from collections.abc import AsyncIterator

from loguru import logger

from martlet_molt.channels.base import (
    BaseChannel,
    ChannelMessage,
    ChannelResponse,
    ChannelStatus,
)


class CLIChannel(BaseChannel):
    """命令行通訊通道"""

    id = "cli"
    name = "CLI Channel"
    description = "命令行互動通道"

    def __init__(self, session_id: str = ""):
        """
        初始化 CLI Channel

        Args:
            session_id: 會話 ID
        """
        self._session_id = session_id
        self._prompt = "你: "

    def set_prompt(self, prompt: str) -> None:
        """
        設定輸入提示符

        Args:
            prompt: 提示符文字
        """
        self._prompt = prompt

    async def receive(self) -> AsyncIterator[ChannelMessage]:
        """
        從標準輸入接收訊息

        Yields:
            ChannelMessage: 接收到的訊息
        """
        self._status = ChannelStatus.RUNNING
        logger.debug("CLI Channel 開始接收訊息")

        while self.is_running:
            try:
                # 非阻塞讀取標準輸入
                loop = asyncio.get_event_loop()
                user_input = await loop.run_in_executor(
                    None,
                    input,
                    self._prompt,
                )

                # 跳過空輸入
                if not user_input.strip():
                    continue

                # 處理退出命令
                if user_input.lower() in ["/exit", "/quit", "exit", "quit"]:
                    logger.info("用戶請求退出")
                    self._status = ChannelStatus.STOPPED
                    break

                yield ChannelMessage(
                    content=user_input,
                    user_id="cli_user",
                    session_id=self._session_id,
                    metadata={"source": "cli"},
                )

            except EOFError:
                # 使用者輸入 Ctrl+D
                logger.debug("收到 EOF 訊號")
                break
            except KeyboardInterrupt:
                # 使用者輸入 Ctrl+C
                logger.debug("收到中斷訊號")
                break
            except Exception as e:
                logger.exception(f"接收訊息時發生錯誤: {e}")
                self._status = ChannelStatus.ERROR
                break

        logger.debug("CLI Channel 停止接收訊息")

    async def send(self, response: ChannelResponse) -> bool:
        """
        輸出到標準輸出

        Args:
            response: 回應內容

        Returns:
            bool: 是否發送成功
        """
        try:
            if response.success:
                print(f"\nAI: {response.content}\n")
            else:
                print(f"\n[錯誤] {response.error}\n")
            return True
        except Exception as e:
            logger.exception(f"發送回應時發生錯誤: {e}")
            return False

    async def stop(self) -> bool:
        """
        停止 Channel

        Returns:
            bool: 是否停止成功
        """
        self._status = ChannelStatus.STOPPED
        logger.debug("CLI Channel 已停止")
        return True
