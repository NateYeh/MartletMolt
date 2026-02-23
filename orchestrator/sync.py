"""
智能同步模組 (Smart Syncer)
負責 A/B 系統間的程式碼增量同步，具備排除模式與安全檢查。
"""

import filecmp
import shutil
from fnmatch import fnmatch
from pathlib import Path

from loguru import logger

from orchestrator.config import settings


class Syncer:
    """智能同步器"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.exclude_patterns = settings.sync.exclude_patterns

    def _is_excluded(self, name: str) -> bool:
        """檢查是否符合排除模式"""
        return any(fnmatch(name, pattern) for pattern in self.exclude_patterns)

    def sync(self, source: str, target: str) -> bool:
        """
        同步程式碼從 source 到 target (增量同步)

        Args:
            source: 源系統名稱 ('a' 或 'b')
            target: 目標系統名稱 ('a' 或 'b')

        Returns:
            是否同步成功
        """
        source_path = getattr(settings, f"system_{source}").path
        target_path = getattr(settings, f"system_{target}").path

        # 絕對路徑化，防止路徑穿越
        src_root = Path(source_path).resolve()
        dst_root = Path(target_path).resolve()

        if self.dry_run:
            logger.info(f"[DRY RUN] Syncing {src_root} -> {dst_root}")
        else:
            logger.info(f"Syncing {src_root} -> {dst_root}")

        try:
            self._sync_dir(src_root, dst_root)
            logger.info(f"Sync completed: {source} -> {target}")
            return True
        except Exception as e:
            logger.exception(f"Sync failed: {e}")
            return False

    def _sync_dir(self, src: Path, dst: Path):
        """遞迴同步目錄"""
        if not dst.exists() and not self.dry_run:
            dst.mkdir(parents=True, exist_ok=True)

        for item in src.iterdir():
            if self._is_excluded(item.name):
                continue

            target_item = dst / item.name

            if item.is_dir():
                self._sync_dir(item, target_item)
            else:
                self._sync_file(item, target_item)

    def _sync_file(self, src_file: Path, dst_file: Path):
        """同步單一檔案（僅在變動時）"""
        should_copy = False

        if not dst_file.exists():
            should_copy = True
        else:
            # 檢查檔案是否不同
            # shallow=False 會檢查內容，但這裡為了效能先檢查 metadata
            # 如果 mtime 或 size 不同則視為有變動
            if not filecmp.cmp(src_file, dst_file, shallow=True):
                should_copy = True

        if should_copy:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would copy: {src_file.name}")
            else:
                shutil.copy2(src_file, dst_file)
                logger.debug(f"Copied: {src_file.name}")
