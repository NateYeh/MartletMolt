"""
AI Agent 核心
"""

import asyncio
import json
from collections.abc import AsyncIterator

from loguru import logger

from martlet_molt.core.session import Session, session_manager
from martlet_molt.core.stream_buffer import StreamBuffer
from martlet_molt.providers.base import BaseProvider, ToolDefinition
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
        self._tools_registered = False

    def set_provider(self, provider: BaseProvider) -> None:
        """設定 Provider"""
        self.provider = provider
        self._tools_registered = False

    def add_system_prompt(self, prompt: str) -> None:
        """添加系統提示"""
        session_manager.add_message(self.session.id, "system", prompt)

    def _register_tools_to_provider(self) -> None:
        """註冊 Tools 到 Provider"""
        if self._tools_registered or not self.provider:
            return

        # 檢查 Provider 是否支援 tool 註冊
        if not hasattr(self.provider, "register_tool"):
            logger.debug("Provider does not support tool registration")
            return

        # 註冊所有 Tools
        tool_names = self.tools.list_tools()
        if not tool_names:
            # 嘗試註冊預設 Tools
            self.tools.register_defaults()
            tool_names = self.tools.list_tools()

        for tool_name in tool_names:
            tool = self.tools.get(tool_name)
            if tool:
                self.provider.register_tool(
                    ToolDefinition(
                        name=tool.name,
                        description=tool.description,
                        parameters=tool.parameters_schema,
                    )
                )
                logger.debug(f"Registered tool: {tool_name}")

        self._tools_registered = True
        logger.info(f"Registered {len(tool_names)} tools to provider")

    async def chat(self, user_input: str, max_iterations: int = 10) -> str:
        """
        對話（支援 Tool Calling）

        Args:
            user_input: 用戶輸入
            max_iterations: 最大 Tool Calling 迭代次數，防止無限循環

        Returns:
            AI 回應
        """
        if not self.provider:
            raise ValueError("No provider set")

        # 1. 註冊 Tools 到 Provider
        self._register_tools_to_provider()

        # 2. 添加用戶訊息
        session_manager.add_message(self.session.id, "user", user_input)

        # 3. Tool Calling Loop
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            logger.debug(f"Tool calling iteration: {iteration}")

            # 準備訊息 (從 DB 確保載入最新，或是使用緩存)
            messages = self.session.get_messages_for_api()

            # 調用 Provider (支援 tools)
            try:
                # 優先使用 chat_with_tools
                if hasattr(self.provider, "chat_with_tools"):
                    content, tool_calls = await self.provider.chat_with_tools(messages)
                else:
                    # 回退到普通 chat
                    content = await self.provider.chat(messages)
                    tool_calls = []
            except Exception as e:
                logger.exception(f"Provider chat failed: {e}")
                raise

            # 如果沒有 tool calls，返回結果
            if not tool_calls:
                session_manager.add_message(self.session.id, "assistant", content)
                return content

            # 有 tool calls，需要執行並繼續對話
            logger.info(f"AI requested {len(tool_calls)} tool calls")

            # 構建 assistant 訊息（包含 tool_calls）
            session_manager.add_message(
                self.session.id,
                "assistant",
                content,
                tool_calls=self._format_tool_calls_for_message(tool_calls),
            )

            # 執行所有 tool calls 並添加結果
            for call in tool_calls:
                call_id = call.get("id", "")
                tool_name = call.get("name", "")
                arguments = call.get("arguments", {})

                logger.info(f"Executing tool: {tool_name} with arguments: {arguments}")

                try:
                    result = self.tools.execute(tool_name, arguments)

                    # 記錄到會話的 tool_calls 列表 (這裡維持內存 update，主要由 add_message 持久化)
                    self.session.add_tool_call(tool_name, arguments)

                    # 添加 tool 結果訊息
                    tool_content = json.dumps(result.data, ensure_ascii=False) if result.data else result.error
                    session_manager.add_message(
                        self.session.id,
                        "tool",
                        tool_content,
                        name=tool_name,
                        tool_call_id=call_id,
                    )

                    logger.debug(f"Tool {tool_name} result: {tool_content[:200]}...")

                except Exception as e:
                    logger.exception(f"Tool execution failed: {e}")
                    # 添加錯誤結果
                    session_manager.add_message(
                        self.session.id,
                        "tool",
                        f"Error: {e}",
                        name=tool_name,
                        tool_call_id=call_id,
                    )

        # 達到最大迭代次數
        logger.warning(f"Reached max tool calling iterations: {max_iterations}")
        return content or "抱歉，處理您的請求時超出了最大迭代次數。"

    def _format_tool_calls_for_message(self, tool_calls: list[dict]) -> list[dict]:
        """
        格式化 tool_calls 用於 assistant 訊息

        Args:
            tool_calls: 從 Provider 返回的 tool_calls

        Returns:
            OpenAI 格式的 tool_calls
        """
        formatted = []
        for call in tool_calls:
            formatted.append(
                {
                    "id": call.get("id", ""),
                    "type": "function",
                    "function": {
                        "name": call.get("name", ""),
                        "arguments": json.dumps(call.get("arguments", {}), ensure_ascii=False),
                    },
                }
            )
        return formatted

    async def stream(self, user_input: str) -> AsyncIterator[str]:
        """
        串流對話

        注意：串流模式目前不支援 Tool Calling，
        如需 Tool 請使用 chat() 方法。

        Args:
            user_input: 用戶輸入

        Yields:
            AI 回應片段
        """
        if not self.provider:
            raise ValueError("No provider set")

        # 註冊 Tools
        self._register_tools_to_provider()

        # 添加用戶訊息
        session_manager.add_message(self.session.id, "user", user_input)

        # 準備訊息
        messages = self.session.get_messages_for_api()

        # 調用 Provider (串流)
        full_response = ""
        async for chunk in self.provider.stream(messages):  # type: ignore[misc]
            full_response += chunk
            yield chunk

        # 添加助手訊息
        session_manager.add_message(self.session.id, "assistant", full_response)

    async def stream_to_buffer(
        self,
        user_input: str,
        buffer: StreamBuffer,
    ) -> str:
        """
        串流到緩衝區（後台任務使用）

        Args:
            user_input: 用戶輸入
            buffer: 串流緩衝區

        Returns:
            完整回應內容
        """
        if not self.provider:
            raise ValueError("No provider set")

        # 註冊 Tools
        self._register_tools_to_provider()

        # 添加用戶訊息
        session_manager.add_message(self.session.id, "user", user_input)

        # 準備訊息
        messages = self.session.get_messages_for_api()

        # 標記緩衝區開始
        buffer.start()

        full_response = ""
        try:
            # 調用 Provider (串流)
            async for chunk in self.provider.stream(messages):  # type: ignore[misc]
                full_response += chunk

                # 推入緩衝區
                await buffer.put(chunk)

            # 標記完成
            buffer.complete()

            # 添加助手訊息
            session_manager.add_message(self.session.id, "assistant", full_response)

            logger.info(f"Stream completed: session={self.session.id}, response_len={len(full_response)}")

            # 自動生成標題 (如果還沒有標題)
            if not self.session.metadata.get("title"):
                asyncio.create_task(self._generate_session_title(user_input))

            return full_response

        except asyncio.CancelledError:
            logger.warning(f"Stream cancelled: session={self.session.id}")
            buffer.cancel()
            raise

        except Exception as e:
            logger.exception(f"Stream failed: {e}")
            buffer.fail(str(e))
            raise

    async def _generate_session_title(self, first_user_input: str) -> None:
        """自動生成會話標題"""
        try:
            # 簡單處理：取前 20 個字
            title = first_user_input[:20].strip() + ("..." if len(first_user_input) > 20 else "")
            session_manager.rename_session(self.session.id, title)
            logger.info(f"Auto-generated title for {self.session.id}: {title}")
        except Exception as e:
            logger.error(f"Failed to generate title: {e}")
    async def run_tools(self, tool_calls: list[dict]) -> list[dict]:
        """
        執行工具調用（獨立使用）

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
        self._tools_registered = False
