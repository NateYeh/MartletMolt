"""
程序管理模組
"""

import subprocess
import time
from pathlib import Path

from loguru import logger

from orchestrator.config import settings
from orchestrator.health_check import health_checker
from orchestrator.state import SystemHealth, state_manager


class ProcessManager:
    """程序管理器"""

    def __init__(self):
        self.processes: dict[str, subprocess.Popen] = {}

    def start(self, system: str) -> bool:
        """
        啟動系統

        Args:
            system: 系統名稱 ('a' 或 'b')

        Returns:
            是否啟動成功
        """
        system_config = getattr(settings, f"system_{system}")
        path = system_config.path
        port = system_config.port

        # 檢查是否已經在運行
        if system in self.processes and self.processes[system].poll() is None:
            logger.warning(f"System {system} is already running")
            return True

        # 啟動程序
        try:
            # 使用 uvicorn 啟動 FastAPI 服務
            cmd = [
                "uvicorn",
                f"{path.name}.main:app",
                "--host",
                system_config.host,
                "--port",
                str(port),
            ]

            logger.info(f"Starting system {system}: {' '.join(cmd)}")

            process = subprocess.Popen(
                cmd,
                cwd=Path.cwd() / path.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.processes[system] = process

            # 等待服務啟動
            time.sleep(2)

            # 健康檢查
            if health_checker.check_with_retry(system_config.url):
                state_manager.update_health(
                    system,
                    SystemHealth(
                        status="running",
                        last_check=time.strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
                logger.info(f"System {system} started successfully on port {port}")
                return True
            else:
                logger.error(f"System {system} health check failed after startup")
                self.stop(system)
                return False

        except Exception as e:
            logger.exception(f"Failed to start system {system}: {e}")
            return False

    def stop(self, system: str) -> bool:
        """
        停止系統

        Args:
            system: 系統名稱 ('a' 或 'b')

        Returns:
            是否停止成功
        """
        if system not in self.processes:
            logger.warning(f"System {system} is not running")
            return True

        process = self.processes[system]

        try:
            # 嘗試優雅關閉
            process.terminate()

            # 等待程序結束
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # 強制關閉
                process.kill()
                process.wait()

            del self.processes[system]

            state_manager.update_health(
                system,
                SystemHealth(
                    status="stopped",
                    last_check=time.strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )

            logger.info(f"System {system} stopped successfully")
            return True

        except Exception as e:
            logger.exception(f"Failed to stop system {system}: {e}")
            return False

    def restart(self, system: str) -> bool:
        """
        重啟系統

        Args:
            system: 系統名稱 ('a' 或 'b')

        Returns:
            是否重啟成功
        """
        self.stop(system)
        time.sleep(2)
        return self.start(system)

    def is_running(self, system: str) -> bool:
        """
        檢查系統是否正在運行

        Args:
            system: 系統名稱 ('a' 或 'b')

        Returns:
            是否正在運行
        """
        if system not in self.processes:
            return False

        return self.processes[system].poll() is None

    def get_status(self) -> dict:
        """取得所有系統狀態"""
        return {
            system: {
                "process": self.processes.get(system),
                "running": self.is_running(system),
            }
            for system in ["a", "b"]
        }


# 全域程序管理器
process_manager = ProcessManager()
