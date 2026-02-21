"""
健康檢查模組
"""

import time

import httpx
from loguru import logger

from orchestrator.config import settings
from orchestrator.state import SystemHealth


class HealthChecker:
    """健康檢查器"""

    def __init__(self):
        self.client = httpx.Client(timeout=settings.health_check.timeout)

    def check(self, url: str) -> SystemHealth:
        """
        執行健康檢查

        Args:
            url: 系統 URL

        Returns:
            健康狀態
        """
        try:
            response = self.client.get(f"{url}{settings.health_check.endpoint}")

            if response.status_code == 200:
                return SystemHealth(
                    status="running",
                    last_check=time.strftime("%Y-%m-%d %H:%M:%S"),
                )
            else:
                return SystemHealth(
                    status="error",
                    error_message=f"HTTP {response.status_code}",
                    last_check=time.strftime("%Y-%m-%d %H:%M:%S"),
                )

        except httpx.TimeoutException:
            return SystemHealth(
                status="error",
                error_message="Timeout",
                last_check=time.strftime("%Y-%m-%d %H:%M:%S"),
            )
        except Exception as e:
            return SystemHealth(
                status="error",
                error_message=str(e),
                last_check=time.strftime("%Y-%m-%d %H:%M:%S"),
            )

    def check_with_retry(self, url: str, retries: int | None = None) -> bool:
        """
        帶重試的健康檢查

        Args:
            url: 系統 URL
            retries: 重試次數，預設使用配置值

        Returns:
            是否健康
        """
        retries = retries or settings.health_check.retries

        for attempt in range(retries):
            health = self.check(url)

            if health.status == "running":
                return True

            if attempt < retries - 1:
                logger.warning(f"Health check failed (attempt {attempt + 1}/{retries}): {health.error_message}")
                time.sleep(settings.health_check.interval)

        return False

    def close(self) -> None:
        """關閉 HTTP 客戶端"""
        self.client.close()


# 全域健康檢查器
health_checker = HealthChecker()
