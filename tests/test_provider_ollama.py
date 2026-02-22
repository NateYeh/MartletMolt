import json
from unittest.mock import MagicMock, patch

import pytest
from martlet_molt.providers.base import Message, ToolDefinition
from martlet_molt.providers.ollama import OllamaProvider


@pytest.fixture
def ollama_provider():
    return OllamaProvider(
        api_key="fake-key",
        base_url="https://fake-ollama.com",
        model="test-model"
    )


def test_convert_messages(ollama_provider):
    """測試訊息格式轉換"""
    messages = [
        Message(role="system", content="sys content"),
        Message(role="user", content="user content"),
        Message(role="assistant", content="ai content", tool_calls=[{"id": "c1", "type": "function"}])
    ]
    
    ollama_msgs = ollama_provider._convert_messages(messages)
    
    assert len(ollama_msgs) == 3
    assert ollama_msgs[0]["role"] == "system"
    assert ollama_msgs[2]["tool_calls"] == [{"id": "c1", "type": "function"}]


def test_register_and_get_tools(ollama_provider):
    """測試工具註冊與定義輸出"""
    tool = ToolDefinition(
        name="test_tool",
        description="test description",
        parameters={"type": "object", "properties": {}}
    )
    ollama_provider.register_tool(tool)
    
    definitions = ollama_provider.get_tools_definition()
    assert len(definitions) == 1
    assert definitions[0]["function"]["name"] == "test_tool"


@pytest.mark.asyncio
async def test_ollama_chat_success(ollama_provider):
    """測試對話成功的 API 封裝"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {"role": "assistant", "content": "Hello human"}
    }
    mock_response.raise_for_status = MagicMock()
    
    with patch.object(ollama_provider._session, "post", return_value=mock_response):
        content = await ollama_provider.chat([Message(role="user", content="Hi")])
        assert content == "Hello human"


@pytest.mark.asyncio
async def test_ollama_chat_with_tools(ollama_provider):
    """測試帶工具調用的對話"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {
            "role": "assistant",
            "content": "Thinking...",
            "tool_calls": [
                {
                    "id": "call_1",
                    "function": {"name": "shell", "arguments": {"command": "ls"}}
                }
            ]
        }
    }
    
    with patch.object(ollama_provider._session, "post", return_value=mock_response):
        content, tool_calls = await ollama_provider.chat_with_tools([Message(role="user", content="run ls")])
        assert content == "Thinking..."
        assert len(tool_calls) == 1
        assert tool_calls[0]["name"] == "shell"
        assert tool_calls[0]["arguments"] == {"command": "ls"}
