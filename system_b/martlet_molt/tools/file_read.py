"""
檔案讀取 Tool
"""

from pathlib import Path

from martlet_molt.tools.base import BaseTool, ToolResult


class FileReadTool(BaseTool):
    """檔案讀取 Tool"""

    name = "file_read"
    description = "讀取指定檔案的內容。支援行範圍選擇、行號顯示等功能。"

    parameters_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "要讀取的檔案路徑（絕對路徑）",
            },
            "start_line": {
                "type": "integer",
                "default": 1,
                "description": "起始行號（1-based），預設 1",
            },
            "end_line": {
                "type": "integer",
                "default": -1,
                "description": "結束行號（1-based），-1 表示到檔案末尾",
            },
            "show_line_numbers": {
                "type": "boolean",
                "default": True,
                "description": "是否顯示行號",
            },
            "max_lines": {
                "type": "integer",
                "default": 2000,
                "description": "最大讀取行數限制",
            },
        },
        "required": ["file_path"],
    }

    def execute(
        self,
        file_path: str,
        start_line: int = 1,
        end_line: int = -1,
        show_line_numbers: bool = True,
        max_lines: int = 2000,
    ) -> ToolResult:
        """執行檔案讀取"""
        try:
            path = Path(file_path)

            if not path.exists():
                return ToolResult(
                    success=False,
                    error=f"File not found: {file_path}",
                )

            if not path.is_file():
                return ToolResult(
                    success=False,
                    error=f"Not a file: {file_path}",
                )

            # 讀取檔案
            with open(path, encoding="utf-8") as f:
                all_lines = f.readlines()

            total_lines = len(all_lines)

            # 處理行範圍
            if end_line == -1:
                end_line = total_lines

            start_idx = max(0, start_line - 1)
            end_idx = min(total_lines, end_line)

            # 檢查最大行數
            if end_idx - start_idx > max_lines:
                end_idx = start_idx + max_lines

            lines = all_lines[start_idx:end_idx]

            # 格式化輸出
            output_lines = []
            for i, line in enumerate(lines):
                if show_line_numbers:
                    output_lines.append(f"{start_idx + i + 1:6d}: {line.rstrip()}")
                else:
                    output_lines.append(line.rstrip())

            content = "\n".join(output_lines)

            return ToolResult(
                success=True,
                data={
                    "content": content,
                    "total_lines": total_lines,
                    "read_lines": len(lines),
                    "start_line": start_line,
                    "end_line": end_line,
                },
                metadata={"file_path": file_path},
            )

        except UnicodeDecodeError:
            return ToolResult(
                success=False,
                error="File is not text or has unsupported encoding",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )
