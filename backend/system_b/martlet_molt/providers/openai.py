"""
OpenAI Provider
"""

import json
from collections.abc import AsyncIterator

from loguru import logger
from openai import AsyncOpenAI

from martlet_molt.core.config import settings
from martlet_molt.providers.base import BaseProvider, Message, ToolDefinition


class OpenAIProvider(BaseProvider):
    """OpenAI Provider"""

    name = "openai"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ):
        """
        初始化 OpenAI Provider

        注意：為了支援雙容器架構，base_url 應優先從配置讀取，
        若未提供則預設為 None (由 SDK 使用預設或環境變數)。
        """
        config = settings.providers.openai
        if config is None:
            config = type("Config", (), {})()

        self.api_key = api_key or getattr(config, "api_key", "") or ""
        # 核心改動：不提供寫死的 https://api.openai.com，這讓我們可以輕鬆切換到 Proxy
        self.base_url = base_url or getattr(config, "base_url", None)
        self.model = model or getattr(config, "model", "gpt-4o")
        self.max_tokens = max_tokens or getattr(config, "max_tokens", 4096)
        self.temperature = temperature or getattr(config, "temperature", 0.7)

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        self._tools: list[ToolDefinition] = []

    def register_tool(self, tool: ToolDefinition) -> None:
        """註冊工具"""
        self._tools.append(tool)

    def get_tools_definition(self) -> list[dict]:
        """取得工具定義"""
        if not self._tools:
            return []

        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in self._tools
        ]

    def get_available_models(self) -> list[str]:
        """取得可用模型列表"""
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ]

    def _convert_messages(self, messages: list[Message]) -> list[dict]:
        """
        轉換訊息格式

        支援 OpenAI Tool Calling 格式:
        - user/assistant/system: {"role": "...", "content": "..."}
        - assistant with tool_calls: {"role": "assistant", "content": "...", "tool_calls": [...]}
        - tool: {"role": "tool", "content": "...", "tool_call_id": "..."}

        Args:
            messages: 訊息列表

        Returns:
            OpenAI API 格式的訊息列表
        """
        api_messages: list[dict] = []

        for msg in messages:
            # 基本訊息
            if msg.role in ["user", "system"]:
                api_messages.append(
                    {
                        "role": msg.role,
                        "content": msg.content,
                    }
                )

            # Assistant 訊息
            elif msg.role == "assistant":
                msg_dict: dict = {
                    "role": msg.role,
                    "content": msg.content,
                }
                # 如果有 tool_calls，加入
                if msg.tool_calls:
                    msg_dict["tool_calls"] = msg.tool_calls
                api_messages.append(msg_dict)

            # Tool 結果訊息
            elif msg.role == "tool":
                api_messages.append(
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "tool_call_id": msg.tool_call_id,
                    }
                )

        return api_messages

    async def chat(self, messages: list[Message]) -> str:
        """同步對話"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self._convert_messages(messages),
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                tools=self.get_tools_definition() or None,
            )

            return response.choices[0].message.content or ""

        except Exception as e:
            logger.exception(f"OpenAI chat failed: {e}")
            raise

    async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
        """串流對話"""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=self._convert_messages(messages),
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                tools=self.get_tools_definition() or None,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.exception(f"OpenAI stream failed: {e}")
            raise

    async def chat_with_tools(self, messages: list[Message]) -> tuple[str, list[dict]]:
        """
        對話（支援工具調用）

        Args:
            messages: 訊息列表

        Returns:
            (回應內容, 工具調用列表)
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self._convert_messages(messages),
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                tools=self.get_tools_definition() or None,
            )

            message = response.choices[0].message
            content = message.content or ""

            tool_calls = []
            if message.tool_calls:
                for call in message.tool_calls:
                    tool_calls.append(
                        {
                            "id": call.id,
                            "name": call.function.name,
                            "arguments": json.loads(call.function.arguments),
                        }
                    )

            return content, tool_calls

        except Exception as e:
            logger.exception(f"OpenAI chat_with_tools failed: {e}")
            raise
