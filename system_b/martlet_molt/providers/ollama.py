"""
Ollama Cloud Provider

支援 Ollama Cloud API (https://ollama.com)，可使用 GLM-5 等雲端模型。
使用 requests 套件實作，方便除錯和控制。
"""

import json
import os
from collections.abc import AsyncIterator
from typing import Any

import requests
from loguru import logger

from martlet_molt.providers.base import BaseProvider, Message, ToolDefinition


class OllamaProvider(BaseProvider):
    """
    Ollama Cloud Provider

    支援 Ollama Cloud API 與本地 Ollama 服務。
    透過設定 base_url 來區分：
    - Cloud: base_url="https://ollama.com"
    - Local: base_url="http://localhost:11434" (預設)
    """

    name = "ollama"

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://ollama.com",
        model: str = "glm-5",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: int = 120,
        **kwargs: Any,
    ) -> None:
        """
        初始化 Ollama Provider

        Args:
            api_key: Ollama Cloud API Key (從環境變數 OLLAMA_API_KEY 讀取)
            base_url: API 端點，預設為 Ollama Cloud
            model: 模型名稱，預設為 glm-5
            max_tokens: 最大輸出 token 數
            temperature: 溫度參數
            timeout: 請求逾時秒數
            **kwargs: 其他參數
        """
        self.api_key = api_key or os.environ.get("OLLAMA_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        self._tools: list[ToolDefinition] = []

        # 建立 session
        self._session = requests.Session()
        if self.api_key:
            self._session.headers.update({"Authorization": f"Bearer {self.api_key}"})

        logger.info(f"OllamaProvider initialized: base_url={base_url}, model={model}")

    def register_tool(self, tool: ToolDefinition) -> None:
        """
        註冊工具

        Args:
            tool: 工具定義
        """
        self._tools.append(tool)
        logger.debug(f"Tool registered: {tool.name}")

    def get_tools_definition(self) -> list[dict]:
        """
        取得工具定義（Ollama/OpenAI 格式）

        Returns:
            工具定義列表
        """
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

    def _convert_messages(self, messages: list[Message]) -> list[dict]:
        """
        將內部 Message 格式轉換為 Ollama API 格式

        支援 OpenAI-style Tool Calling:
        - user/system: {"role": "...", "content": "..."}
        - assistant with tool_calls: {"role": "assistant", "content": "...", "tool_calls": [...]}
        - tool: {"role": "tool", "content": "...", "name": "..."}

        Args:
            messages: 內部訊息列表

        Returns:
            Ollama API 格式的訊息列表
        """
        ollama_messages: list[dict] = []

        for msg in messages:
            # 基本訊息
            if msg.role in ["user", "system"]:
                ollama_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                })

            # Assistant 訊息
            elif msg.role == "assistant":
                msg_dict: dict = {
                    "role": msg.role,
                    "content": msg.content,
                }
                # 如果有 tool_calls，加入
                if msg.tool_calls:
                    msg_dict["tool_calls"] = msg.tool_calls
                ollama_messages.append(msg_dict)

            # Tool 結果訊息
            elif msg.role == "tool":
                ollama_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                    "name": msg.name,
                })

        return ollama_messages

    def _chat_sync(
        self,
        messages: list[dict],
        stream: bool = False,
        tools: list[dict] | None = None,
    ) -> dict:
        """
        同步呼叫 Ollama API

        Args:
            messages: 訊息列表
            stream: 是否使用串流模式
            tools: 工具定義列表

        Returns:
            API 回應字典
        """
        url = f"{self.base_url}/api/chat"
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
        }

        # 添加 tools
        if tools:
            payload["tools"] = tools

        # 注意: GLM-5 模型在傳入 options 時可能觸發 thinking 模式
        # 導致 content 為空，因此這裡不傳入 options
        #
        # 如果需要控制 max_tokens 或 temperature，可以在需要時啟用：
        # payload["options"] = {
        #     "num_predict": self.max_tokens,
        #     "temperature": self.temperature,
        # }

        logger.debug(f"POST {url} with model={self.model}, stream={stream}, tools={len(tools) if tools else 0}")

        response = self._session.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()

        return response.json()

    async def chat(self, messages: list[Message]) -> str:
        """
        同步對話

        Args:
            messages: 訊息列表

        Returns:
            AI 回應字串
        """
        try:
            ollama_messages = self._convert_messages(messages)
            logger.debug(f"Sending chat request to {self.model}")

            data = self._chat_sync(
                ollama_messages,
                tools=self.get_tools_definition() or None,
            )

            # 解析回應
            message = data.get("message", {})
            content = message.get("content", "")
            logger.debug(f"Received response: {len(content)} chars")
            return content

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"Ollama API error: {e.response.status_code}") from e
        except Exception:
            logger.exception(f"Ollama chat error: {self.model}")
            raise

    async def chat_with_tools(
        self, messages: list[Message]
    ) -> tuple[str, list[dict[str, Any]]]:
        """
        對話（支援工具調用）

        Args:
            messages: 訊息列表

        Returns:
            (回應內容, 工具調用列表)
        """
        try:
            ollama_messages = self._convert_messages(messages)
            tools = self.get_tools_definition()

            logger.debug(f"Sending chat_with_tools request to {self.model}, tools={len(tools)}")

            data = self._chat_sync(
                ollama_messages,
                tools=tools or None,
            )

            # 解析回應
            message = data.get("message", {})
            content = message.get("content", "")

            # 解析 tool_calls
            tool_calls = []
            if "tool_calls" in message:
                for call in message["tool_calls"]:
                    tool_calls.append({
                        "id": call.get("id", ""),
                        "name": call.get("function", {}).get("name", ""),
                        "arguments": call.get("function", {}).get("arguments", {}),
                    })
                logger.info(f"AI requested {len(tool_calls)} tool calls")

            return content, tool_calls

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"Ollama API error: {e.response.status_code}") from e
        except Exception:
            logger.exception(f"Ollama chat_with_tools error: {self.model}")
            raise

    async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
        """
        串流對話

        Args:
            messages: 訊息列表

        Yields:
            AI 回應片段
        """
        try:
            ollama_messages = self._convert_messages(messages)
            url = f"{self.base_url}/api/chat"
            payload: dict = {
                "model": self.model,
                "messages": ollama_messages,
                "stream": True,
            }

            # 添加 tools
            tools = self.get_tools_definition()
            if tools:
                payload["tools"] = tools

            # 注意: GLM-5 模型在傳入 options 時可能觸發 thinking 模式
            # 導致 content 為空，因此這裡不傳入 options

            logger.debug(f"Starting stream to {self.model}")

            response = self._session.post(url, json=payload, timeout=self.timeout, stream=True)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        message = data.get("message", {})
                        content = message.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"Ollama API error: {e.response.status_code}") from e
        except Exception:
            logger.exception(f"Ollama stream error: {self.model}")
            raise

    def get_available_models(self) -> list[str]:
        """
        取得可用模型列表

        Returns:
            模型 ID 列表
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = self._session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            models = data.get("models", [])
            return [m.get("name", "") for m in models if m.get("name")]
        except Exception:
            logger.warning("Failed to list models, returning defaults")
            return [
                "glm-5",
                "glm-4.7",
                "llama3.1",
                "llama3.2",
                "codellama",
                "mistral",
            ]