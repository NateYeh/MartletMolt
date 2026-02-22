"""
Tool 抽象基類與註冊表
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ToolResult(BaseModel):
    """Tool 執行結果"""

    success: bool = True
    data: Any = None
    error: str = ""
    metadata: dict = {}  # 額外資訊（執行時間、資源使用等）


class BaseTool(ABC):
    """Tool 抽象基類"""

    name: str = ""
    description: str = ""
    parameters_schema: dict = {}  # JSON Schema

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        執行 Tool

        Args:
            **kwargs: 工具參數

        Returns:
            執行結果
        """
        pass

    def get_definition(self) -> dict:
        """
        取得工具定義（OpenAI 格式）

        Returns:
            OpenAI 格式的工具定義
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema,
            },
        }

    def validate_parameters(self, **kwargs) -> bool:
        """
        驗證參數

        Args:
            **kwargs: 工具參數

        Returns:
            是否有效
        """
        # TODO: 使用 JSON Schema 驗證
        return True


class ToolRegistry:
    """工具註冊表"""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """註冊工具"""
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        """取消註冊工具"""
        if name in self._tools:
            del self._tools[name]

    def get(self, name: str) -> BaseTool | None:
        """取得工具"""
        return self._tools.get(name)

    def execute(self, name: str, arguments: dict) -> ToolResult:
        """
        執行工具

        Args:
            name: 工具名稱
            arguments: 工具參數

        Returns:
            執行結果
        """
        tool = self.get(name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool not found: {name}",
            )

        try:
            return tool.execute(**arguments)
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )

    def list_tools(self) -> list[str]:
        """列出所有工具"""
        return list(self._tools.keys())

    def get_definitions(self) -> list[dict]:
        """取得所有工具定義（OpenAI 格式）"""
        return [tool.get_definition() for tool in self._tools.values()]

    def register_defaults(self) -> None:
        """註冊預設工具"""
        from martlet_molt.tools.file_read import FileReadTool
        from martlet_molt.tools.file_write import FileWriteTool
        from martlet_molt.tools.iot_control import IOTControlTool
        from martlet_molt.tools.shell import ShellTool
        from martlet_molt.tools.web_click import WebClickTool
        from martlet_molt.tools.web_evaluate import WebEvaluateTool
        from martlet_molt.tools.web_extract import WebExtractTool
        from martlet_molt.tools.web_fill import WebFillTool
        from martlet_molt.tools.web_navigate import WebNavigateTool

        self.register(WebNavigateTool())
        self.register(WebExtractTool())
        self.register(WebClickTool())
        self.register(WebFillTool())
        self.register(WebEvaluateTool())
        self.register(ShellTool())
        self.register(FileReadTool())
        self.register(FileWriteTool())
        self.register(IOTControlTool())
