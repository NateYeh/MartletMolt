"""
A/B 系統切換模組
"""

from loguru import logger

from orchestrator.config import settings
from orchestrator.health_check import health_checker
from orchestrator.manager import process_manager
from orchestrator.state import state_manager


class Switcher:
    """A/B 系統切換器"""

    def __init__(self):
        self.syncer = Syncer()

    def switch(self, target: str | None = None) -> bool:
        """
        切換系統

        Args:
            target: 目標系統 ('a' 或 'b')，None 表示切換到另一個

        Returns:
            是否切換成功
        """
        current = state_manager.get_active_system()
        target = target or state_manager.get_inactive_system()

        if current == target:
            logger.warning(f"System {target} is already active")
            return True

        logger.info(f"Switching from system {current} to system {target}")

        # 取得目標系統配置
        target_config = getattr(settings, f"system_{target}")

        # 檢查目標系統是否正在運行
        if process_manager.is_running(target):
            logger.warning(f"System {target} is already running, performing health check")
            if not health_checker.check_with_retry(target_config.url):
                logger.error(f"System {target} health check failed")
                return False
        else:
            # 啟動目標系統
            if not process_manager.start(target):
                logger.error(f"Failed to start system {target}")
                return False

        # 停止當前系統
        if not process_manager.stop(current):
            logger.warning(f"Failed to stop system {current}, continuing anyway")

        # 更新狀態
        state_manager.switch_active()

        # 同步程式碼到備份系統
        self.syncer.sync(target, current)

        logger.info(f"Successfully switched to system {target}")
        return True

    def evolve(self, modified_system: str) -> bool:
        """
        執行進化流程

        這是自我修改後的切換流程：
        1. 確認修改的是非活躍系統
        2. 啟動被修改的系統
        3. 健康檢查
        4. 切換服務

        Args:
            modified_system: 被修改的系統 ('a' 或 'b')

        Returns:
            是否進化成功
        """
        current = state_manager.get_active_system()

        # 安全檢查：不能修改正在運行的系統
        if modified_system == current:
            logger.error(f"Cannot evolve: system {modified_system} is currently active")
            return False

        logger.info(f"Starting evolution: system {modified_system}")

        # 啟動被修改的系統
        modified_config = getattr(settings, f"system_{modified_system}")

        if not process_manager.start(modified_system):
            logger.error(f"Evolution failed: could not start system {modified_system}")
            return False

        # 健康檢查（帶重試）
        if not health_checker.check_with_retry(modified_config.url):
            logger.error(f"Evolution failed: system {modified_system} health check failed")
            # 回滾：停止失敗的系統
            process_manager.stop(modified_system)
            return False

        # 切換服務
        if not self.switch(modified_system):
            logger.error("Evolution failed: could not switch systems")
            return False

        logger.info(f"Evolution successful: now running system {modified_system}")
        return True


class Syncer:
    """程式碼同步器"""

    def sync(self, source: str, target: str) -> bool:
        """
        同步程式碼從 source 到 target

        Args:
            source: 源系統 ('a' 或 'b')
            target: 目標系統 ('a' 或 'b')

        Returns:
            是否同步成功
        """
        import shutil
        from pathlib import Path

        source_path = getattr(settings, f"system_{source}").path
        target_path = getattr(settings, f"system_{target}").path

        logger.info(f"Syncing system {source} to system {target}")

        try:
            for pattern in settings.sync.exclude_patterns:
                # 清理目標系統的排除檔案
                for file in Path(target_path).rglob(pattern):
                    if file.is_dir():
                        shutil.rmtree(file)
                    else:
                        file.unlink()

            # 複製檔案
            for item in Path(source_path).iterdir():
                if item.name in settings.sync.exclude_patterns:
                    continue

                target_item = Path(target_path) / item.name

                if item.is_dir():
                    if target_item.exists():
                        shutil.rmtree(target_item)
                    shutil.copytree(item, target_item)
                else:
                    shutil.copy2(item, target_item)

            logger.info(f"Sync completed: {source} -> {target}")
            return True

        except Exception as e:
            logger.exception(f"Sync failed: {e}")
            return False


# 全域切換器
switcher = Switcher()
