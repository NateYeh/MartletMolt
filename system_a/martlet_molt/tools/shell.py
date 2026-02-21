"""
Shell 命令執行 Tool
"""

import subprocess
import time

from martlet_molt.core.config import settings
from martlet_molt.tools.base import BaseTool, ToolResult


class ShellTool(BaseTool):
    """Shell 命令執行 Tool"""

    name = "shell"
    description = "執行 Linux Shell 命令（使用 bash）。支援管道、重定向、環境變數等標準 shell 語法。"

    parameters_schema = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "要執行的 shell 命令",
            },
            "timeout": {
                "type": "integer",
                "default": 300,
                "description": "執行超時時間（秒），預設 300 秒，最大 300 秒",
            },
            "cwd": {
                "type": "string",
                "description": "工作目錄",
            },
        },
        "required": ["command"],
    }

    # 危險命令列表
    DANGEROUS_COMMANDS = [
        "rm -rf /",
        "mkfs",
        "dd if=",
        "> /dev/sda",
        "chmod -R 777 /",
        "chown -R",
    ]

    def execute(
        self,
        command: str,
        timeout: int = 300,
        cwd: str | None = None,
    ) -> ToolResult:
        """執行 Shell 命令"""
        # 安全檢查
        if settings.tools.shell_sandbox:
            for dangerous in self.DANGEROUS_COMMANDS:
                if dangerous in command:
                    return ToolResult(
                        success=False,
                        error=f"Dangerous command detected: {dangerous}",
                    )

        # 限制超時時間
        timeout = min(timeout, 300)

        try:
            start_time = time.time()

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )

            elapsed = time.time() - start_time

            return ToolResult(
                success=result.returncode == 0,
                data={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                    "elapsed": elapsed,
                },
                metadata={"command": command, "timeout": timeout},
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error=f"Command timed out after {timeout} seconds",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )
