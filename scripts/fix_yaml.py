#!/usr/bin/env python3
"""
YAML 檔案格式修正工具
自動修正常見的 YAML 格式問題
"""

import sys
from pathlib import Path


def fix_yaml_file(file_path: Path) -> bool:
    """
    修正 YAML 檔案的常見問題。

    Args:
        file_path: YAML 檔案路徑

    Returns:
        是否成功修正
    """
    try:
        # 讀取檔案
        content = file_path.read_text(encoding="utf-8")

        # 修正問題
        fixed_content = content

        # 1. 確保檔案結尾有換行符
        if not fixed_content.endswith("\n"):
            fixed_content += "\n"
            print(f"✅ {file_path}: 已添加結尾換行符")

        # 2. 移除多餘的尾隨空行（只保留一個）
        fixed_content = fixed_content.rstrip() + "\n"

        # 3. 寫回檔案
        if fixed_content != content:
            file_path.write_text(fixed_content, encoding="utf-8")
            return True
        else:
            print(f"✓ {file_path}: 格式正確，無需修正")
            return False

    except Exception as e:
        print(f"❌ {file_path}: 修正失敗 - {e}")
        return False


def main():
    """主程式進入點"""
    if len(sys.argv) < 2:
        print("使用方式: python fix_yaml.py <file1.yaml> [file2.yaml ...]")
        print("       python fix_yaml.py --all")
        sys.exit(1)

    files: list[Path] = []

    if sys.argv[1] == "--all":
        # 找出所有 YAML 檔案
        project_root = Path(__file__).parent.parent
        files = list(project_root.rglob("*.yaml")) + list(project_root.rglob("*.yml"))
        # 排除虛擬環境和快取目錄
        files = [f for f in files if ".venv" not in str(f) and "__pycache__" not in str(f) and ".git" not in str(f)]
    else:
        files = [Path(f) for f in sys.argv[1:]]

    print(f"🔍 掃描 {len(files)} 個 YAML 檔案...\n")

    fixed_count = 0
    for file_path in files:
        if fix_yaml_file(file_path):
            fixed_count += 1

    print(f"\n{'=' * 50}")
    print(f"✅ 完成！已修正 {fixed_count} 個檔案")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
