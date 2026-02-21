"""
Provider 抽象基類
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from pydantic import BaseModel


class Message(BaseModel):
    """訊息模型"""

    role: str  # "user" | "assistant" | "system" | "tool"
    content: str
    name: str | None = None  # for tool messages
    tool_call_id: str | None = None  # for tool messages
    tool_calls: list[dict] | None = None  # for assistant messages with tool calls


class ToolDefinition(BaseModel):
    """工具定義"""

    name: str
    description: str
    parameters: dict  # JSON Schema


class BaseProvider(ABC):
    """AI Provider 抽象基類"""

    name: str = "base"

    @abstractmethod
    async def chat(self, messages: list[Message]) -> str:
        """
        同步對話

        Args:
            messages: 訊息列表

        Returns:
            AI 回應
        """
        pass

    @abstractmethod
    async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
        """
        串流對話

        Args:
            messages: 訊息列表

        Yields:
            AI 回應片段
        """
        pass

    @abstractmethod
    def get_tools_definition(self) -> list[dict]:
        """
        取得工具定義（用於 API）

        Returns:
            OpenAI 格式的工具定義列表
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """
        取得可用模型列表

        Returns:
            模型 ID 列表
        """
        pass

    def register_tool(self, tool: ToolDefinition) -> None:
        """
        註冊工具（可選實作）

        Args:
            tool: 工具定義
        """
        _ = tool  # 可選實作，子類可覆寫

    async def chat_with_tools(self, messages: list[Message]) -> tuple[str, list[dict[str, Any]]]:
        """
        對話（支援工具調用，可選實作）

        Args:
            messages: 訊息列表

        Returns:
            (回應內容, 工具調用列表)
        """
        # 預設實作：調用普通 chat，返回空的 tool_calls
        response = await self.chat(messages)
        return response, []
