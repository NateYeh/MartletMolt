"""
System A/B 同步腳本
使用 Python 原生實現，不依賴 rsync
"""

import argparse
import shutil
from pathlib import Path

# 要同步的模組
SYNC_MODULES = [
    "channels",
    "tools",
    "providers",
    "core",
    "gateway",
    "skills",
]


def sync_modules(source: str, target: str, modules: list[str] | None = None) -> None:
    """
    同步模組

    Args:
        source: 來源系統 (a 或 b)
        target: 目標系統 (a 或 b)
        modules: 要同步的模組列表
    """
    base = Path(__file__).parent.parent
    modules = modules or SYNC_MODULES

    print(f"🔄 同步 system_{source} → system_{target}...")

    for module in modules:
        src = base / "backend" / f"system_{source}/martlet_molt/{module}"
        dst = base / "backend" / f"system_{target}/martlet_molt/{module}"

        if not src.exists():
            print(f"  ⚠️  {module} 來源不存在，跳過")
            continue

        print(f"  📁 {module}")

        # 刪除目標目錄
        if dst.exists():
            shutil.rmtree(dst)

        # 複製目錄
        shutil.copytree(src, dst)

    print(f"✅ 同步完成！backend/system_{source} → backend/system_{target}")


def main() -> None:
    """主程式"""
    parser = argparse.ArgumentParser(
        description="同步 System A/B",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "direction",
        choices=["a-to-b", "b-to-a"],
        help="同步方向",
    )
    parser.add_argument(
        "--modules",
        nargs="*",
        help="指定要同步的模組（預設同步全部）",
    )

    args = parser.parse_args()
    source, target = args.direction.split("-to-")
    sync_modules(source, target, args.modules)


if __name__ == "__main__":
    main()
