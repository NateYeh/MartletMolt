"""
AI Agent 核心
"""

from collections.abc import AsyncIterator

from loguru import logger

from martlet_molt.core.session import Session, session_manager
from martlet_molt.providers.base import BaseProvider
from martlet_molt.tools.base import ToolRegistry


class Agent:
    """AI Agent"""

    def __init__(
        self,
        provider: BaseProvider | None = None,
        session: Session | None = None,
        tools: ToolRegistry | None = None,
    ):
        self.provider = provider
        self.session = session or session_manager.create()
        self.tools = tools or ToolRegistry()

    def set_provider(self, provider: BaseProvider) -> None:
        """設定 Provider"""
        self.provider = provider

    def add_system_prompt(self, prompt: str) -> None:
        """添加系統提示"""
        self.session.add_message("system", prompt)

    async def chat(self, user_input: str) -> str:
        """
        同步對話

        Args:
            user_input: 用戶輸入

        Returns:
            AI 回應
        """
        if not self.provider:
            raise ValueError("No provider set")

        # 添加用戶訊息
        self.session.add_message("user", user_input)

        # 準備訊息
        messages = self.session.get_messages_for_api()

        # 調用 Provider
        response = await self.provider.chat(messages)

        # 添加助手訊息
        self.session.add_message("assistant", response)

        # 儲存會話
        session_manager.save(self.session)

        return response

    async def stream(self, user_input: str) -> AsyncIterator[str]:
        """
        串流對話

        Args:
            user_input: 用戶輸入

        Yields:
            AI 回應片段
        """
        if not self.provider:
            raise ValueError("No provider set")

        # 添加用戶訊息
        self.session.add_message("user", user_input)

        # 準備訊息
        messages = self.session.get_messages_for_api()

        # 調用 Provider (串流)
        full_response = ""
        async for chunk in self.provider.stream(messages):
            full_response += chunk
            yield chunk

        # 添加助手訊息
        self.session.add_message("assistant", full_response)

        # 儲存會話
        session_manager.save(self.session)

    async def run_tools(self, tool_calls: list[dict]) -> list[dict]:
        """
        執行工具調用

        Args:
            tool_calls: 工具調用列表

        Returns:
            工具結果列表
        """
        results = []

        for call in tool_calls:
            tool_name = call.get("name") or call.get("function", {}).get("name")
            arguments = call.get("arguments") or call.get("function", {}).get("arguments", {})

            if isinstance(arguments, str):
                import json

                arguments = json.loads(arguments)

            logger.info(f"Executing tool: {tool_name} with arguments: {arguments}")

            try:
                result = self.tools.execute(tool_name, arguments)
                results.append(
                    {
                        "tool_call_id": call.get("id"),
                        "name": tool_name,
                        "result": result.model_dump(),
                    }
                )

                # 記錄到會話
                self.session.add_tool_call(tool_name, arguments)

            except Exception as e:
                logger.exception(f"Tool execution failed: {e}")
                results.append(
                    {
                        "tool_call_id": call.get("id"),
                        "name": tool_name,
                        "error": str(e),
                    }
                )

        return results

    def reset(self) -> None:
        """重置會話"""
        self.session = session_manager.create()
