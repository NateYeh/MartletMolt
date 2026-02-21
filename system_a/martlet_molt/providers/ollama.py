"""
Ollama Provider (Placeholder)
"""

from collections.abc import AsyncIterator

from martlet_molt.providers.base import BaseProvider, Message


class OllamaProvider(BaseProvider):
    """Ollama Provider"""

    name = "ollama"

    def __init__(self):
        # TODO: Implement
        pass

    async def chat(self, messages: list[Message]) -> str:
        # TODO: Implement
        raise NotImplementedError("Ollama provider not yet implemented")

    async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
        # TODO: Implement
        raise NotImplementedError("Ollama provider not yet implemented")
        yield ""  # type: ignore

    def get_tools_definition(self) -> list[dict]:
        return []

    def get_available_models(self) -> list[str]:
        return ["llama3.1", "llama3.2", "codellama", "mistral"]
