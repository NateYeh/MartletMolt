"""
pytest 配置
"""

import sys
from pathlib import Path

# 添加 system_a 目錄到 Python 路徑
project_root = Path(__file__).parent.parent
system_a_path = project_root / "backend" / "system_a"

if system_a_path.exists():
    sys.path.insert(0, str(system_a_path))
else:
    print(f"Warning: system_a path not found at {system_a_path}")
