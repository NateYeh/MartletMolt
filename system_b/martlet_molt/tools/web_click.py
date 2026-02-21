"""
網頁點擊 Tool
"""

from martlet_molt.tools.base import BaseTool, ToolResult
from martlet_molt.tools.web_navigate import WebNavigateTool


class WebClickTool(BaseTool):
    """網頁點擊 Tool"""

    name = "web_click"
    description = "使用 CSS Selector 點擊網頁元素"

    parameters_schema = {
        "type": "object",
        "properties": {
            "selector": {
                "type": "string",
                "description": "CSS Selector，例如 '#submit-btn', '.login-button'",
            },
            "click_count": {
                "type": "integer",
                "default": 1,
                "description": "點擊次數（1=單擊, 2=雙擊）",
            },
            "timeout": {
                "type": "integer",
                "default": 10000,
                "description": "等待元素超時時間（毫秒）",
            },
            "wait_after": {
                "type": "integer",
                "default": 500,
                "description": "點擊後等待時間（毫秒）",
            },
        },
        "required": ["selector"],
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
        click_count: int = 1,
        timeout: int = 10000,
        wait_after: int = 500,
    ) -> ToolResult:
        """執行點擊操作"""
        try:
            page = self._get_page()

            # 等待元素出現
            element = page.wait_for_selector(selector, timeout=timeout)

            if not element:
                return ToolResult(
                    success=False,
                    error=f"Element not found: {selector}",
                )

            # 點擊
            element.click(click_count=click_count)

            # 等待
            if wait_after > 0:
                page.wait_for_timeout(wait_after)

            return ToolResult(
                success=True,
                data={"selector": selector, "click_count": click_count},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )
