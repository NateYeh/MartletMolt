"""
MartletMolt 統一入口點

根據 settings.yaml 中的 active_system 設定，
動態切換啟動 system_a 或 system_b。
"""

import sys
from pathlib import Path

# 將專案根目錄加入 sys.path，以便導入 system_a/system_b
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import yaml


def load_active_system() -> str:
    """
    從設定檔載入目前啟用的系統

    Returns:
        系統名稱 ('a' 或 'b')
    """
    # 尋找配置檔路徑
    config_paths = [
        Path(__file__).parent / "Config" / "settings.yaml",
        Path("Config/settings.yaml"),
        Path("../Config/settings.yaml"),
    ]

    for config_path in config_paths:
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
                return config.get("active_system", "a")

    return "a"


def main() -> None:
    """主入口點"""
    # 載入設定
    active_system = load_active_system()

    # 驗證系統名稱
    if active_system not in ("a", "b"):
        print(f"錯誤: active_system 必須是 'a' 或 'b'，目前設定為 '{active_system}'")
        sys.exit(1)

    # 將對應的系統目錄加入 sys.path
    project_root = Path(__file__).parent
    system_path = project_root / "backend" / f"system_{active_system}"
    if str(system_path) not in sys.path:
        sys.path.insert(0, str(system_path))

    # 動態導入 CLI 模組
    try:
        import importlib

        cli_module = importlib.import_module("martlet_molt.cli")
        cli_main = getattr(cli_module, "main", None)

        if cli_main is None:
            print("錯誤: martlet_molt.cli 中找不到 main 函數")
            sys.exit(1)

        # 執行 CLI
        cli_main()

    except ImportError as e:
        print("錯誤: 無法導入 martlet_molt.cli")
        print(f"詳細錯誤: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"執行錯誤: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
