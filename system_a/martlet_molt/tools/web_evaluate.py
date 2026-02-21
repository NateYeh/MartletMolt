"""
網頁 JavaScript 執行 Tool
"""

from martlet_molt.tools.base import BaseTool, ToolResult
from martlet_molt.tools.web_navigate import WebNavigateTool


class WebEvaluateTool(BaseTool):
    """網頁 JavaScript 執行 Tool"""

    name = "web_evaluate"
    description = "在頁面中執行 JavaScript 代碼並返回結果"

    parameters_schema = {
        "type": "object",
        "properties": {
            "script": {
                "type": "string",
                "description": "要執行的 JavaScript 代碼，可以使用 return 返回結果",
            },
            "arg": {
                "type": "string",
                "description": "傳遞給腳本的參數（可選）",
            },
        },
        "required": ["script"],
    }

    def __init__(self, navigate_tool: WebNavigateTool | None = None):
        self._navigate_tool = navigate_tool

    def _get_page(self):
        """取得頁面實例"""
        if self._navigate_tool and self._navigate_tool._page:
            return self._navigate_tool._page
        raise RuntimeError("No page available. Please navigate first.")

    def execute(
        self,
        script: str,
        arg: str | None = None,
    ) -> ToolResult:
        """執行 JavaScript"""
        try:
            page = self._get_page()

            if arg:
                result = page.evaluate(script, arg)
            else:
                result = page.evaluate(script)

            return ToolResult(
                success=True,
                data={"result": result},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )
