#!/usr/bin/env python3
"""
API 文件生成器

從 YAML 檔案生成 API_SDK.md 文件

使用方式:
    python tools/generate_api_docs.py
"""

from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader


class ApiDocGenerator:
    """API 文件生成器"""

    def __init__(self, docs_dir: Path):
        """
        初始化生成器

        Args:
            docs_dir: docs 目錄路徑
        """
        self.docs_dir = docs_dir
        self.api_dir = docs_dir / 'api'
        self.endpoints_dir = self.api_dir / 'endpoints'
        self.schemas_dir = self.api_dir / 'schemas'
        self.sdk_dir = self.api_dir / 'sdk'
        self.templates_dir = docs_dir / 'templates'

        # 設定 Jinja2 環境
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def load_yaml(self, path: Path) -> dict[str, Any]:
        """
        載入 YAML 檔案

        Args:
            path: YAML 檔案路徑

        Returns:
            解析後的資料
        """
        with open(path, encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def load_config(self) -> dict[str, Any]:
        """載入配置檔案"""
        return self.load_yaml(self.api_dir / 'config.yaml')

    def load_common_schemas(self) -> dict[str, Any]:
        """載入共用 Schema"""
        return self.load_yaml(self.schemas_dir / 'common.yaml')

    def load_endpoints(self) -> list[dict[str, Any]]:
        """
        載入所有端點定義

        Returns:
            排序後的端點列表
        """
        endpoints = []
        for yaml_file in self.endpoints_dir.glob('*.yaml'):
            endpoint_data = self.load_yaml(yaml_file)
            endpoints.append(endpoint_data)

        # 按照 order 排序
        endpoints.sort(key=lambda x: x.get('order', 999))
        return endpoints

    def load_sdk(self) -> dict[str, Any]:
        """載入 SDK 定義"""
        sdk_file = self.sdk_dir / 'typescript.yaml'
        return self.load_yaml(sdk_file) if sdk_file.exists() else {}

    def generate_api_endpoints_table(self, endpoints: list[dict[str, Any]]) -> str:
        """
        生成 API 端點總覽表格

        Args:
            endpoints: 端點列表

        Returns:
            Markdown 表格
        """
        # 分類端點
        system_endpoints = []
        chat_endpoints = []
        session_endpoints = []

        for endpoint in endpoints:
            path = endpoint['endpoint']['path']

            if '/sessions' in path:
                session_endpoints.append(endpoint)
            elif '/chat' in path:
                chat_endpoints.append(endpoint)
            else:
                system_endpoints.append(endpoint)

        # 生成表格
        lines = []

        # 系統端點
        if system_endpoints:
            lines.append('### 系統端點\n')
            lines.append('| 方法 | 路徑 | 描述 |')
            lines.append('|------|------|------|')
            for ep in system_endpoints:
                lines.append(
                    f"| `{ep['endpoint']['method']}` | `{ep['endpoint']['path']}` | {ep['title']} |"
                )
            lines.append('')

        # 對話端點
        if chat_endpoints:
            lines.append('### 對話端點\n')
            lines.append('| 方法 | 路徑 | 描述 | 是否串流 |')
            lines.append('|------|------|------|----------|')
            for ep in chat_endpoints:
                is_stream = '✅' if 'stream' in ep['endpoint']['path'] else '❌'
                lines.append(
                    f"| `{ep['endpoint']['method']}` | `{ep['endpoint']['path']}` | {ep['title']} | {is_stream} |"
                )
            lines.append('')

        # 會話管理端點
        if session_endpoints:
            lines.append('### 會話管理端點\n')
            lines.append('| 方法 | 路徑 | 描述 |')
            lines.append('|------|------|------|')
            for ep in session_endpoints:
                lines.append(
                    f"| `{ep['endpoint']['method']}` | `{ep['endpoint']['path']}` | {ep['title']} |"
                )
            lines.append('')

        return '\n'.join(lines)

    def generate_markdown(self) -> str:
        """
        生成 API_SDK.md 文件

        Returns:
            Markdown 內容
        """
        # 載入資料
        config = self.load_config()
        common_schemas = self.load_common_schemas()
        endpoints = self.load_endpoints()
        sdk = self.load_sdk()

        # 準備模板資料
        template_data = {
            'config': config,
            'endpoints': endpoints,
            'common_schemas': common_schemas,
            'sdk': sdk,
            'api_endpoints_table': self.generate_api_endpoints_table(endpoints),
        }

        # 載入模板
        template = self.env.get_template('api_sdk.md.j2')

        # 生成 Markdown
        return template.render(**template_data)

    def save_markdown(self, output_path: Path) -> None:
        """
        儲存生成的 Markdown 文件

        Args:
            output_path: 輸出檔案路徑
        """
        markdown_content = self.generate_markdown()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f'✅ API 文件已生成: {output_path}')
        print(f'📊 檔案大小: {output_path.stat().st_size / 1024:.1f} KB')


def main():
    """主程式"""
    # 專案根目錄
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / 'docs'

    # 輸出路徑
    output_path = docs_dir / 'API_SDK.md'

    # 生成文件
    generator = ApiDocGenerator(docs_dir)
    generator.save_markdown(output_path)

    print('\n🎉 完成！已生成 API_SDK.md')


if __name__ == '__main__':
    main()
