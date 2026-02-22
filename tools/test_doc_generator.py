#!/usr/bin/env python3
"""
API 文檔生成器測試腳本

驗證生成器能正確運作
"""

import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.generate_api_docs import ApiDocGenerator


def test_generator():
    """測試文檔生成器"""
    print("🧪 測試 API 文檔生成器...\n")

    # 初始化生成器
    docs_dir = project_root / 'docs'
    generator = ApiDocGenerator(docs_dir)

    # 測試 1: 載入配置
    print("✅ 測試 1: 載入配置")
    config = generator.load_config()
    assert config['metadata']['version'] == '0.1.0'
    assert config['metadata']['base_url'] == 'http://localhost:8001'
    print(f"  版本: {config['metadata']['version']}")
    print(f"  Base URL: {config['metadata']['base_url']}\n")

    # 測試 2: 載入端點
    print("✅ 測試 2: 載入端點")
    endpoints = generator.load_endpoints()
    assert len(endpoints) == 7, f"預期 7 個端點，實際 {len(endpoints)} 個"
    print(f"  端點數量: {len(endpoints)}")
    for ep in endpoints:
        print(f"  - {ep['endpoint']['method']} {ep['endpoint']['path']}: {ep['title']}")
    print()

    # 測試 3: 載入 SDK
    print("✅ 測試 3: 載入 SDK")
    sdk = generator.load_sdk()
    assert sdk['language'] == 'TypeScript'
    assert 'MartletMoltClient' in sdk['sections'][1]['code']
    print(f"  語言: {sdk['language']}")
    print(f"  檔案名: {sdk['filename']}\n")

    # 測試 4: 生成 Markdown
    print("✅ 測試 4: 生成 Markdown")
    markdown = generator.generate_markdown()
    assert len(markdown) > 10000, "生成的文檔過短"
    assert '# MartletMolt 後端 API SDK 文件' in markdown
    assert '## 詳細 API 文件' in markdown
    print(f"  文檔長度: {len(markdown)} 字元")
    print("  包含標題: ✅")
    print("  包含詳細文檔: ✅\n")

    # 測試 5: 檢查端點表格
    print("✅ 測試 5: 檢查端點表格")
    table = generator.generate_api_endpoints_table(endpoints)
    assert '系統端點' in table
    assert '對話端點' in table
    assert '會話管理端點' in table
    print("  系統端點: ✅")
    print("  對話端點: ✅")
    print("  會話管理端點: ✅\n")

    print("🎉 所有測試通過！\n")


if __name__ == '__main__':
    test_generator()
