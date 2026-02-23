import json
from unittest.mock import MagicMock, patch

import pytest
import requests
from martlet_molt.providers.base import Message, ToolDefinition
from martlet_molt.providers.ollama import OllamaProvider


@pytest.fixture
def ollama_provider():
    return OllamaProvider(
        api_key="fake-key",
        base_url="https://fake-ollama.com",
        model="test-model"
    )


def test_convert_messages_basic(ollama_provider):
    """測試基本訊息格式轉換"""
    messages = [
        Message(role="system", content="sys content"),
        Message(role="user", content="user content"),
        Message(role="assistant", content="ai content")
    ]
    
    ollama_msgs = ollama_provider._convert_messages(messages)
    
    assert len(ollama_msgs) == 3
    assert ollama_msgs[0]["role"] == "system"
    assert ollama_msgs[1]["role"] == "user"
    assert ollama_msgs[2]["role"] == "assistant"
    assert ollama_msgs[2]["content"] == "ai content"


def test_convert_messages_with_tools(ollama_provider):
    """測試包含工具調用與工具回傳結果的轉換"""
    messages = [
        Message(
            role="assistant", 
            content="Use tool", 
            tool_calls=[{"id": "c1", "type": "function", "function": {"name": "test"}}]
        ),
        Message(
            role="tool",
            content="tool result",
            name="test",
            tool_call_id="c1"
        )
    ]
    
    ollama_msgs = ollama_provider._convert_messages(messages)
    
    assert len(ollama_msgs) == 2
    # Assistant 訊息應包含 tool_calls
    assert "tool_calls" in ollama_msgs[0]
    assert ollama_msgs[0]["tool_calls"][0]["id"] == "c1"
    
    # Tool 訊息應包含 name
    assert ollama_msgs[1]["role"] == "tool"
    assert ollama_msgs[1]["name"] == "test"
    assert ollama_msgs[1]["content"] == "tool result"


def test_register_and_get_tools(ollama_provider):
    """測試工具註冊與定義輸出"""
    tool = ToolDefinition(
        name="test_tool",
        description="test description",
        parameters={"type": "object", "properties": {"cmd": {"type": "string"}}}
    )
    ollama_provider.register_tool(tool)
    
    definitions = ollama_provider.get_tools_definition()
    assert len(definitions) == 1
    assert definitions[0]["type"] == "function"
    assert definitions[0]["function"]["name"] == "test_tool"
    assert "cmd" in definitions[0]["function"]["parameters"]["properties"]


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
async def test_ollama_chat_error(ollama_provider):
    """測試 API 報錯處理"""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Invalid model"
    
    # 建立一個帶有 response 屬性的 HTTPError
    error = requests.exceptions.HTTPError("Bad Request")
    error.response = mock_response
    mock_response.raise_for_status.side_effect = error
    
    with patch.object(ollama_provider._session, "post", return_value=mock_response):
        with pytest.raises(RuntimeError, match="Ollama API error: 400"):
            await ollama_provider.chat([Message(role="user", content="Hi")])


@pytest.mark.asyncio
async def test_ollama_chat_with_tools(ollama_provider):
    """測試帶工具調用的對話解析"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {
            "role": "assistant",
            "content": "Running command...",
            "tool_calls": [
                {
                    "id": "call_99",
                    "function": {"name": "shell", "arguments": {"command": "ls -la"}}
                }
            ]
        }
    }
    
    with patch.object(ollama_provider._session, "post", return_value=mock_response):
        content, tool_calls = await ollama_provider.chat_with_tools([Message(role="user", content="list files")])
        assert content == "Running command..."
        assert len(tool_calls) == 1
        assert tool_calls[0]["id"] == "call_99"
        assert tool_calls[0]["name"] == "shell"
        assert tool_calls[0]["arguments"] == {"command": "ls -la"}


@pytest.mark.asyncio
async def test_ollama_stream(ollama_provider):
    """測試串流對話"""
    mock_response = MagicMock()
    # 模擬串流行數據
    lines = [
        json.dumps({"message": {"content": "Hel"}}).encode('utf-8'),
        json.dumps({"message": {"content": "lo"}}).encode('utf-8'),
        json.dumps({"message": {"content": "!"}}).encode('utf-8')
    ]
    mock_response.iter_lines.return_value = lines
    mock_response.raise_for_status = MagicMock()
    
    with patch.object(ollama_provider._session, "post", return_value=mock_response):
        collected = []
        async for chunk in ollama_provider.stream([Message(role="user", content="Hi")]):
            collected.append(chunk)
        
        assert "".join(collected) == "Hello!"
        assert len(collected) == 3


def test_get_available_models(ollama_provider):
    """測試模型清單取得"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "models": [
            {"name": "glm-5:latest"},
            {"name": "llama3:latest"}
        ]
    }
    
    with patch.object(ollama_provider._session, "get", return_value=mock_response):
        models = ollama_provider.get_available_models()
        assert "glm-5:latest" in models
        assert "llama3:latest" in models


def test_get_available_models_fallback(ollama_provider):
    """測試模型清單失敗時的回退機制"""
    with patch.object(ollama_provider._session, "get", side_effect=Exception("Network error")):
        models = ollama_provider.get_available_models()
        assert len(models) > 0
        assert "glm-5" in models  # 預設清單中的模型
