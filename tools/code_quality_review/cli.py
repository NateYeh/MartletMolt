"""程式碼品質審查命令列工具。

使用方式：
    python tools/code_quality_review/cli.py
    cd tools/code_quality_review && python cli.py
"""

import json
from datetime import datetime
from pathlib import Path

from reviewer import CodeQualityReviewer


def generate_markdown_report(result) -> str:
    """生成 Markdown 格式報告。

    Args:
        result: 審查結果。

    Returns:
        Markdown 格式報告字串。
    """
    lines = [
        '# 程式碼品質審查報告',
        '',
        f'**審查時間**: {result.timestamp}',
        f'**專案路徑**: {result.project_path}',
        '',
        '---',
        '',
        '## 📊 總覽',
        '',
        '| 指標 | 數值 |',
        '|------|------|',
        f'| 掃描檔案數 | {result.stats.get("total_files", 0)} |',
        f'| 總程式碼行數 | {result.stats.get("total_loc", 0)} |',
        f'| 問題總數 | {result.stats.get("total_issues", 0)} |',
        f'| 🔴 高風險 | {result.high_count} |',
        f'| 🟡 中風險 | {result.medium_count} |',
        f'| 🟢 低風險 | {result.low_count} |',
        '',
    ]

    # 按問題類型統計
    issues_by_type = result.stats.get('issues_by_type', {})
    if issues_by_type:
        lines.extend([
            '## 📈 問題類型分佈',
            '',
            '| 類型 | 數量 |',
            '|------|------|',
        ])
        type_names = {
            'complexity': '圈複雜度',
            'maintainability': '可維護性',
            'file_length': '檔案行數',
            'function_length': '函數行數',
        }
        for issue_type, count in sorted(issues_by_type.items(), key=lambda x: -x[1]):
            type_name = type_names.get(issue_type, issue_type)
            lines.append(f'| {type_name} | {count} |')
        lines.append('')

    # 問題詳情
    if result.issues:
        lines.extend([
            '## 🔍 問題詳情',
            '',
        ])

        # 高風險問題
        high_issues = [i for i in result.issues if i.severity == 'high']
        if high_issues:
            lines.append('### 🔴 高風險問題')
            lines.append('')
            for issue in high_issues:
                lines.append(f'#### `{issue.file_path}`')
                lines.append('')
                lines.append(f'- **問題**: {issue.name}')
                if issue.line:
                    lines.append(f'- **行號**: {issue.line}')
                lines.append(f'- **數值**: {issue.value}')
                lines.append(f'- **建議**: {issue.suggestion}')
                lines.append('')

        # 中風險問題
        medium_issues = [i for i in result.issues if i.severity == 'medium']
        if medium_issues:
            lines.append('### 🟡 中風險問題')
            lines.append('')
            for issue in medium_issues:
                lines.append(f'#### `{issue.file_path}`')
                lines.append('')
                lines.append(f'- **問題**: {issue.name}')
                if issue.line:
                    lines.append(f'- **行號**: {issue.line}')
                lines.append(f'- **數值**: {issue.value}')
                lines.append(f'- **建議**: {issue.suggestion}')
                lines.append('')

    else:
        lines.extend([
            '## ✅ 審查結果',
            '',
            '沒有發現問題，程式碼品質良好！',
            '',
        ])

    return '\n'.join(lines)


def generate_json_report(result) -> dict:
    """生成 JSON 格式報告。

    Args:
        result: 審查結果。

    Returns:
        JSON 可序列化的字典。
    """
    return {
        'timestamp': result.timestamp,
        'project_path': result.project_path,
        'stats': result.stats,
        'issues': [
            {
                'file_path': issue.file_path,
                'issue_type': issue.issue_type,
                'severity': issue.severity,
                'name': issue.name,
                'value': issue.value,
                'line': issue.line,
                'suggestion': issue.suggestion,
            }
            for issue in result.issues
        ],
    }


def print_summary(result) -> None:
    """列印審查摘要到終端機。

    Args:
        result: 審查結果。
    """
    print('\n' + '=' * 60)
    print('📊 程式碼品質審查結果')
    print('=' * 60)
    print(f'專案路徑: {result.project_path}')
    print(f'掃描檔案: {result.stats.get("total_files", 0)} 個')
    print(f'總行數: {result.stats.get("total_loc", 0)} 行')
    print('-' * 60)
    print(f'問題總數: {result.stats.get("total_issues", 0)}')
    print(f'  🔴 高風險: {result.high_count}')
    print(f'  🟡 中風險: {result.medium_count}')
    print(f'  🟢 低風險: {result.low_count}')
    print('=' * 60)

    if result.issues:
        # 顯示前 5 個高風險問題
        high_issues = [i for i in result.issues if i.severity == 'high'][:5]
        if high_issues:
            print('\n🔴 高風險問題（前 5 個）:')
            for i, issue in enumerate(high_issues, 1):
                print(f'  {i}. {issue.file_path}')
                print(f'     └─ {issue.name} (值: {issue.value})')

        # 顯示前 5 個中風險問題
        medium_issues = [i for i in result.issues if i.severity == 'medium'][:5]
        if medium_issues:
            print('\n🟡 中風險問題（前 5 個）:')
            for i, issue in enumerate(medium_issues, 1):
                print(f'  {i}. {issue.file_path}')
                print(f'     └─ {issue.name} (值: {issue.value})')

        print('\n📄 詳細報告已生成於 reports/ 目錄')
    else:
        print('\n✅ 沒有發現問題，程式碼品質良好！')

    print()


def main():
    """主程式入口。"""
    # 確定專案根目錄
    current_dir = Path(__file__).resolve()

    # 嘗試找到專案根目錄（包含 pyproject.toml 或 src 目錄的目錄）
    project_path = current_dir.parent.parent.parent

    # 如果找不到，使用當前目錄的父目錄
    if not (project_path / 'pyproject.toml').exists() and not (project_path / 'src').exists():
        project_path = current_dir.parent.parent

    print(f'🔍 正在審查專案: {project_path}')

    # 執行審查
    reviewer = CodeQualityReviewer(str(project_path))
    result = reviewer.review()

    # 建立報告目錄
    reports_dir = Path(__file__).parent / 'reports'
    reports_dir.mkdir(exist_ok=True)

    # 生成日期標記
    date_str = datetime.now().strftime('%Y%m%d')

    # 生成並保存 Markdown 報告
    md_report = generate_markdown_report(result)
    md_path = reports_dir / f'quality_review_{date_str}.md'
    md_path.write_text(md_report, encoding='utf-8')

    # 生成並保存 JSON 報告
    json_report = generate_json_report(result)
    json_path = reports_dir / f'quality_review_{date_str}.json'
    json_path.write_text(json.dumps(json_report, ensure_ascii=False, indent=2), encoding='utf-8')

    # 列印摘要
    print_summary(result)

    # 返回 exit code（有高風險問題則返回 1）
    return 1 if result.high_count > 0 else 0


if __name__ == '__main__':
    exit(main())
