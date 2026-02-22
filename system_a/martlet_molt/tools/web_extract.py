"""
網頁內容提取 Tool
"""

from typing import Literal

from martlet_molt.tools.base import BaseTool, ToolResult
from martlet_molt.tools.web_navigate import WebNavigateTool


class WebExtractTool(BaseTool):
    """網頁內容提取 Tool"""

    name = "web_extract"
    description = "提取網頁內容（文字、HTML、連結、圖片、特定元素）"

    parameters_schema = {
        "type": "object",
        "properties": {
            "extract_type": {
                "type": "string",
                "enum": ["text", "html", "elements", "links", "images"],
                "default": "text",
                "description": "提取類型",
            },
            "selector": {
                "type": "string",
                "description": "CSS Selector（當 extract_type=elements 時使用）",
            },
            "attribute": {
                "type": "string",
                "description": "要提取的屬性名稱（例如 href、src）",
            },
        },
        "required": [],
    }

    def __init__(self, navigate_tool: WebNavigateTool | None = None):
        self._navigate_tool = navigate_tool

    def _get_page(self):
        """取得頁面實例"""
        if self._navigate_tool and self._navigate_tool._page:
            return self._navigate_tool._page
        raise RuntimeError("No page available. Please navigate first.")

    def _extract_text(self, page) -> ToolResult:
        """
        提取頁面文字內容。

        Args:
            page: Playwright 頁面實例。

        Returns:
            提取結果。
        """
        content = page.inner_text("body")
        return ToolResult(
            success=True,
            data={"content": content, "length": len(content)},
        )

    def _extract_html(self, page) -> ToolResult:
        """
        提取頁面 HTML 內容。

        Args:
            page: Playwright 頁面實例。

        Returns:
            提取結果。
        """
        content = page.content()
        return ToolResult(
            success=True,
            data={"html": content, "length": len(content)},
        )

    def _extract_elements(
        self,
        page,
        selector: str | None,
        attribute: str | None,
    ) -> ToolResult:
        """
        提取特定元素。

        Args:
            page: Playwright 頁面實例。
            selector: CSS 選擇器。
            attribute: 要提取的屬性名稱。

        Returns:
            提取結果。
        """
        if not selector:
            return ToolResult(
                success=False,
                error="selector is required for extract_type=elements",
            )

        elements = page.query_selector_all(selector)
        results = []

        for el in elements:
            if attribute:
                value = el.get_attribute(attribute)
                results.append(value)
            else:
                results.append(el.inner_text())

        return ToolResult(
            success=True,
            data={"elements": results, "count": len(results)},
        )

    def _extract_links(self, page) -> ToolResult:
        """
        提取頁面所有連結。

        Args:
            page: Playwright 頁面實例。

        Returns:
            提取結果。
        """
        links = page.query_selector_all("a[href]")
        results = [
            {
                "text": link.inner_text(),
                "href": link.get_attribute("href"),
            }
            for link in links
        ]
        return ToolResult(
            success=True,
            data={"links": results, "count": len(results)},
        )

    def _extract_images(self, page) -> ToolResult:
        """
        提取頁面所有圖片。

        Args:
            page: Playwright 頁面實例。

        Returns:
            提取結果。
        """
        images = page.query_selector_all("img")
        results = [
            {
                "alt": img.get_attribute("alt"),
                "src": img.get_attribute("src"),
            }
            for img in images
        ]
        return ToolResult(
            success=True,
            data={"images": results, "count": len(results)},
        )

    def execute(
        self,
        extract_type: Literal["text", "html", "elements", "links", "images"] = "text",
        selector: str | None = None,
        attribute: str | None = None,
    ) -> ToolResult:
        """
        執行內容提取。

        Args:
            extract_type: 提取類型（text/html/elements/links/images）。
            selector: CSS 選擇器（當 extract_type=elements 時使用）。
            attribute: 要提取的屬性名稱。

        Returns:
            提取結果。
        """
        extractors = {
            "text": lambda page: self._extract_text(page),
            "html": lambda page: self._extract_html(page),
            "elements": lambda page: self._extract_elements(page, selector, attribute),
            "links": lambda page: self._extract_links(page),
            "images": lambda page: self._extract_images(page),
        }

        extractor = extractors.get(extract_type)
        if not extractor:
            return ToolResult(
                success=False,
                error=f"Unknown extract_type: {extract_type}",
            )

        try:
            page = self._get_page()
            return extractor(page)
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )
