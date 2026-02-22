"""
檔案寫入 Tool
"""

import shutil
from pathlib import Path
from typing import Literal

from martlet_molt.tools.base import BaseTool, ToolResult


class FileWriteTool(BaseTool):
    """檔案寫入 Tool"""

    name = "file_write"
    description = "寫入內容到指定檔案。支援建立新檔案、覆蓋現有檔案、追加內容等操作。"

    parameters_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "要寫入的檔案路徑（絕對路徑）",
            },
            "content": {
                "type": "string",
                "description": "要寫入的內容",
            },
            "mode": {
                "type": "string",
                "enum": ["write", "append"],
                "default": "write",
                "description": "寫入模式：write（覆蓋）或 append（追加）",
            },
            "create_dirs": {
                "type": "boolean",
                "default": True,
                "description": "是否自動建立上層目錄",
            },
            "backup": {
                "type": "boolean",
                "default": False,
                "description": "覆蓋前是否備份原檔案（.bak）",
            },
            "encoding": {
                "type": "string",
                "default": "utf-8",
                "description": "檔案編碼",
            },
        },
        "required": ["file_path", "content"],
    }

    def execute(
        self,
        file_path: str,
        content: str,
        mode: Literal["write", "append"] = "write",
        create_dirs: bool = True,
        backup: bool = False,
        encoding: str = "utf-8",
    ) -> ToolResult:
        """執行檔案寫入"""
        try:
            path = Path(file_path)

            # 建立上層目錄
            if create_dirs and not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)

            # 備份
            if backup and path.exists() and mode == "write":
                backup_path = path.with_suffix(path.suffix + ".bak")
                shutil.copy2(path, backup_path)

            # 寫入
            write_mode = "w" if mode == "write" else "a"
            with open(path, write_mode, encoding=encoding) as f:
                f.write(content)

            return ToolResult(
                success=True,
                data={
                    "file_path": str(path),
                    "mode": mode,
                    "bytes_written": len(content.encode(encoding)),
                },
                metadata={"file_path": file_path, "mode": mode},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )
