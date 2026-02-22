"""
網頁導航 Tool
"""

import time
from typing import Literal

from playwright.sync_api import sync_playwright

from martlet_molt.tools.base import BaseTool, ToolResult


class WebNavigateTool(BaseTool):
    """網頁導航 Tool"""

    name = "web_navigate"
    description = "導航到指定的 URL，等待頁面載入完成"

    parameters_schema = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "要導航的 URL",
            },
            "wait_until": {
                "type": "string",
                "enum": ["load", "domcontentloaded", "networkidle", "commit"],
                "default": "load",
                "description": "等待條件",
            },
            "timeout": {
                "type": "integer",
                "default": 30000,
                "description": "超時時間（毫秒）",
            },
        },
        "required": ["url"],
    }

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser = None
        self._page = None

    def _ensure_browser(self):
        """確保瀏覽器已啟動"""
        if self._browser is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=self.headless)
            self._page = self._browser.new_page()

    def execute(
        self,
        url: str,
        wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = "load",
        timeout: int = 30000,
    ) -> ToolResult:
        """執行網頁導航"""
        try:
            self._ensure_browser()

            start_time = time.time()
            self._page.goto(url, wait_until=wait_until, timeout=timeout)
            elapsed = time.time() - start_time

            return ToolResult(
                success=True,
                data={
                    "url": self._page.url,
                    "title": self._page.title(),
                    "elapsed": elapsed,
                },
                metadata={"url": url, "wait_until": wait_until},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )

    def close(self):
        """關閉瀏覽器"""
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
