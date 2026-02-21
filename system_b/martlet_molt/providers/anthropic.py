"""
Anthropic Provider (Placeholder)
"""

from collections.abc import AsyncIterator

from martlet_molt.providers.base import BaseProvider, Message


class AnthropicProvider(BaseProvider):
    """Anthropic Provider"""

    name = "anthropic"

    def __init__(self):
        # TODO: Implement
        pass

    async def chat(self, messages: list[Message]) -> str:
        # TODO: Implement
        raise NotImplementedError("Anthropic provider not yet implemented")

    async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
        # TODO: Implement
        raise NotImplementedError("Anthropic provider not yet implemented")
        yield ""  # type: ignore

    def get_tools_definition(self) -> list[dict]:
        return []

    def get_available_models(self) -> list[str]:
        return ["claude-sonnet-4-20250514", "claude-opus-4-20250514"]
