#!/usr/bin/env python3
"""
YAML 驗證工具
整合 yamllint 和 yamlfix，提供完整的 YAML 檢查與修正功能
"""

import subprocess
import sys
from pathlib import Path


def run_yamllint(files: list[Path], config_path: Path | None = None) -> bool:
    """
    執行 yamllint 檢查。

    Args:
        files: 要檢查的檔案列表
        config_path: yamllint 配置檔路徑

    Returns:
        是否全部通過檢查
    """
    cmd = ["yamllint"]

    if config_path and config_path.exists():
        cmd.extend(["-c", str(config_path)])

    cmd.extend([str(f) for f in files])

    print("📋 執行 yamllint 檢查...")
    result = subprocess.run(cmd, capture_output=False)

    return result.returncode == 0


def run_yamlfix(files: list[Path], check_only: bool = False) -> bool:
    """
    執行 yamlfix 格式化。

    Args:
        files: 要處理的檔案列表
        check_only: 只檢查不自動修正

    Returns:
        是否全部格式正確
    """
    cmd = ["yamlfix"]

    if check_only:
        cmd.append("--check")

    cmd.extend([str(f) for f in files])

    print("🔧 執行 yamlfix 格式化...")
    result = subprocess.run(cmd, capture_output=False)

    return result.returncode == 0


def find_yaml_files(root_path: Path) -> list[Path]:
    """
    找出所有 YAML 檔案。

    Args:
        root_path: 根目錄路徑

    Returns:
        YAML 檔案列表
    """
    patterns = ["*.yaml", "*.yml"]
    files: list[Path] = []

    for pattern in patterns:
        files.extend(root_path.rglob(pattern))

    # 排除虛擬環境和快取目錄
    exclude_dirs = {".venv", "venv", "__pycache__", ".git", "node_modules", ".tox", "build", "dist"}

    return [f for f in files if not any(exclude in f.parts for exclude in exclude_dirs)]


def main():
    """主程式進入點"""
    import argparse

    parser = argparse.ArgumentParser(
        description="YAML 檔案驗證與修正工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 檢查所有 YAML 檔案
  python validate_yaml.py --check

  # 自動修正格式問題
  python validate_yaml.py --fix

  # 檢查指定檔案
  python validate_yaml.py --check file1.yaml file2.yaml
        """,
    )

    parser.add_argument("--check", action="store_true", help="只檢查不自動修正")

    parser.add_argument("--fix", action="store_true", help="自動修正格式問題")

    parser.add_argument("files", nargs="*", help="要檢查的檔案（留空則掃描整個專案）")

    args = parser.parse_args()

    # 確定要處理的檔案
    if args.files:
        files = [Path(f) for f in args.files]
    else:
        project_root = Path(__file__).parent.parent
        files = find_yaml_files(project_root)

    if not files:
        print("⚠️  未找到任何 YAML 檔案")
        sys.exit(0)

    print(f"🔍 掃描到 {len(files)} 個 YAML 檔案\n")
    print("=" * 60)

    # 確定配置檔路徑
    project_root = Path(__file__).parent.parent
    config_path = project_root / ".yamllint"

    success = True

    if args.fix:
        # 先執行 yamllint 檢查
        print("\n📋 階段 1: yamllint 檢查")
        yamllint_ok = run_yamllint(files, config_path)

        # 執行 yamlfix 修正
        print("\n🔧 階段 2: yamlfix 自動修正")
        yamlfix_ok = run_yamlfix(files, check_only=False)

        # 再次執行 yamllint 檢查
        print("\n✅ 階段 3: 最終驗證")
        final_ok = run_yamllint(files, config_path)

        success = final_ok

    elif args.check:
        # 只檢查
        print("\n📋 執行 yamllint 檢查")
        yamllint_ok = run_yamllint(files, config_path)

        print("\n🔧 執行 yamlfix 檢查（不自動修正）")
        yamlfix_ok = run_yamlfix(files, check_only=True)

        success = yamllint_ok and yamlfix_ok

    else:
        parser.print_help()
        sys.exit(1)

    print("\n" + "=" * 60)

    if success:
        print("✅ 所有 YAML 檔案檢查通過！")
        sys.exit(0)
    else:
        print("❌ 發現格式問題，請修正")
        sys.exit(1)


if __name__ == "__main__":
    main()
