"""
網頁表單填寫 Tool
"""

from martlet_molt.tools.base import BaseTool, ToolResult
from martlet_molt.tools.web_navigate import WebNavigateTool


class WebFillTool(BaseTool):
    """網頁表單填寫 Tool"""

    name = "web_fill"
    description = "填寫表單輸入框，支援自動清空和 Enter 鍵"

    parameters_schema = {
        "type": "object",
        "properties": {
            "selector": {
                "type": "string",
                "description": "CSS Selector，例如 '#username', 'input[name=email]'",
            },
            "value": {
                "type": "string",
                "description": "要填寫的值",
            },
            "clear_first": {
                "type": "boolean",
                "default": True,
                "description": "是否先清空輸入框",
            },
            "press_enter": {
                "type": "boolean",
                "default": False,
                "description": "填寫後是否按 Enter 鍵",
            },
            "timeout": {
                "type": "integer",
                "default": 10000,
                "description": "等待元素超時時間（毫秒）",
            },
            "wait_after": {
                "type": "integer",
                "default": 500,
                "description": "填寫後等待時間（毫秒）",
            },
        },
        "required": ["selector", "value"],
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
        selector: str,
        value: str,
        clear_first: bool = True,
        press_enter: bool = False,
        timeout: int = 10000,
        wait_after: int = 500,
    ) -> ToolResult:
        """執行表單填寫"""
        try:
            page = self._get_page()

            # 等待元素出現
            element = page.wait_for_selector(selector, timeout=timeout)

            if not element:
                return ToolResult(
                    success=False,
                    error=f"Element not found: {selector}",
                )

            # 清空
            if clear_first:
                element.fill("")

            # 填寫
            element.fill(value)

            # Enter
            if press_enter:
                element.press("Enter")

            # 等待
            if wait_after > 0:
                page.wait_for_timeout(wait_after)

            return ToolResult(
                success=True,
                data={"selector": selector, "value": value},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )
