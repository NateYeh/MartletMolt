"""程式碼品質審查命令列工具。

使用方式：
    python tools/code_quality_review/cli.py
    cd tools/code_quality_review && python cli.py
"""

import json
from datetime import datetime
from pathlib import Path

from reviewer import CodeQualityReviewer


def _format_overview_section(result) -> list[str]:
    """格式化總覽區塊。

    Args:
        result: 審查結果。

    Returns:
        Markdown 行列表。
    """
    return [
        "# 程式碼品質審查報告",
        "",
        f"**審查時間**: {result.timestamp}",
        f"**專案路徑**: {result.project_path}",
        "",
        "---",
        "",
        "## 📊 總覽",
        "",
        "| 指標 | 數值 |",
        "|------|------|",
        f"| 掃描檔案數 | {result.stats.get('total_files', 0)} |",
        f"| 總程式碼行數 | {result.stats.get('total_loc', 0)} |",
        f"| 問題總數 | {result.stats.get('total_issues', 0)} |",
        f"| 🔴 高風險 | {result.high_count} |",
        f"| 🟡 中風險 | {result.medium_count} |",
        f"| 🟢 低風險 | {result.low_count} |",
        "",
    ]


def _format_issues_by_type_section(result) -> list[str]:
    """格式化問題類型分佈區塊。

    Args:
        result: 審查結果。

    Returns:
        Markdown 行列表。
    """
    issues_by_type = result.stats.get("issues_by_type", {})
    if not issues_by_type:
        return []

    type_names = {
        "complexity": "圈複雜度",
        "maintainability": "可維護性",
        "file_length": "檔案行數",
        "function_length": "函數行數",
    }

    lines = [
        "## 📈 問題類型分佈",
        "",
        "| 類型 | 數量 |",
        "|------|------|",
    ]

    for issue_type, count in sorted(issues_by_type.items(), key=lambda x: -x[1]):
        type_name = type_names.get(issue_type, issue_type)
        lines.append(f"| {type_name} | {count} |")

    lines.append("")
    return lines


def _format_single_issue(issue) -> list[str]:
    """格式化單一問題項目。

    Args:
        issue: 問題物件。

    Returns:
        Markdown 行列表。
    """
    lines = [
        f"#### `{issue.file_path}`",
        "",
        f"- **問題**: {issue.name}",
    ]
    if issue.line:
        lines.append(f"- **行號**: {issue.line}")
    lines.extend(
        [
            f"- **數值**: {issue.value}",
            f"- **建議**: {issue.suggestion}",
            "",
        ]
    )
    return lines


def _format_issues_by_severity(issues: list, severity_label: str, severity_emoji: str) -> list[str]:
    """格式化特定嚴重度的問題區塊。

    Args:
        issues: 問題列表。
        severity_label: 嚴重度標籤（如「高風險」）。
        severity_emoji: 嚴重度 emoji。

    Returns:
        Markdown 行列表。
    """
    if not issues:
        return []

    lines = [
        f"### {severity_emoji} {severity_label}問題",
        "",
    ]

    for issue in issues:
        lines.extend(_format_single_issue(issue))

    return lines


def _format_issues_section(result) -> list[str]:
    """格式化問題詳情區塊。

    Args:
        result: 審查結果。

    Returns:
        Markdown 行列表。
    """
    if not result.issues:
        return _format_no_issues_section()

    lines = [
        "## 🔍 問題詳情",
        "",
    ]

    # 高風險問題
    high_issues = [i for i in result.issues if i.severity == "high"]
    lines.extend(_format_issues_by_severity(high_issues, "高風險", "🔴"))

    # 中風險問題
    medium_issues = [i for i in result.issues if i.severity == "medium"]
    lines.extend(_format_issues_by_severity(medium_issues, "中風險", "🟡"))

    return lines


def _format_no_issues_section() -> list[str]:
    """格式化無問題區塊。

    Returns:
        Markdown 行列表。
    """
    return [
        "## ✅ 審查結果",
        "",
        "沒有發現問題，程式碼品質良好！",
        "",
    ]


def generate_markdown_report(result) -> str:
    """生成 Markdown 格式報告。

    Args:
        result: 審查結果。

    Returns:
        Markdown 格式報告字串。
    """
    lines = _format_overview_section(result)
    lines.extend(_format_issues_by_type_section(result))
    lines.extend(_format_issues_section(result))
    return "\n".join(lines)


def generate_json_report(result) -> dict:
    """生成 JSON 格式報告。

    Args:
        result: 審查結果。

    Returns:
        JSON 可序列化的字典。
    """
    return {
        "timestamp": result.timestamp,
        "project_path": result.project_path,
        "stats": result.stats,
        "issues": [
            {
                "file_path": issue.file_path,
                "issue_type": issue.issue_type,
                "severity": issue.severity,
                "name": issue.name,
                "value": issue.value,
                "line": issue.line,
                "suggestion": issue.suggestion,
            }
            for issue in result.issues
        ],
    }


def print_summary(result) -> None:
    """列印審查摘要到終端機。

    Args:
        result: 審查結果。
    """
    print("\n" + "=" * 60)
    print("📊 程式碼品質審查結果")
    print("=" * 60)
    print(f"專案路徑: {result.project_path}")
    print(f"掃描檔案: {result.stats.get('total_files', 0)} 個")
    print(f"總行數: {result.stats.get('total_loc', 0)} 行")
    print("-" * 60)
    print(f"問題總數: {result.stats.get('total_issues', 0)}")
    print(f"  🔴 高風險: {result.high_count}")
    print(f"  🟡 中風險: {result.medium_count}")
    print(f"  🟢 低風險: {result.low_count}")
    print("=" * 60)

    if result.issues:
        # 顯示前 5 個高風險問題
        high_issues = [i for i in result.issues if i.severity == "high"][:5]
        if high_issues:
            print("\n🔴 高風險問題（前 5 個）:")
            for i, issue in enumerate(high_issues, 1):
                print(f"  {i}. {issue.file_path}")
                print(f"     └─ {issue.name} (值: {issue.value})")

        # 顯示前 5 個中風險問題
        medium_issues = [i for i in result.issues if i.severity == "medium"][:5]
        if medium_issues:
            print("\n🟡 中風險問題（前 5 個）:")
            for i, issue in enumerate(medium_issues, 1):
                print(f"  {i}. {issue.file_path}")
                print(f"     └─ {issue.name} (值: {issue.value})")

        print("\n📄 詳細報告已生成於 reports/ 目錄")
    else:
        print("\n✅ 沒有發現問題，程式碼品質良好！")

    print()


def main():
    """主程式入口。"""
    # 確定專案根目錄
    current_dir = Path(__file__).resolve()

    # 嘗試找到專案根目錄（包含 pyproject.toml 或 src 目錄的目錄）
    project_path = current_dir.parent.parent.parent

    # 如果找不到，使用當前目錄的父目錄
    if not (project_path / "pyproject.toml").exists() and not (project_path / "src").exists():
        project_path = current_dir.parent.parent

    print(f"🔍 正在審查專案: {project_path}")

    # 執行審查
    reviewer = CodeQualityReviewer(str(project_path))
    result = reviewer.review()

    # 建立報告目錄
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    # 生成日期標記
    date_str = datetime.now().strftime("%Y%m%d")

    # 生成並保存 Markdown 報告
    md_report = generate_markdown_report(result)
    md_path = reports_dir / f"quality_review_{date_str}.md"
    md_path.write_text(md_report, encoding="utf-8")

    # 生成並保存 JSON 報告
    json_report = generate_json_report(result)
    json_path = reports_dir / f"quality_review_{date_str}.json"
    json_path.write_text(json.dumps(json_report, ensure_ascii=False, indent=2), encoding="utf-8")

    # 列印摘要
    print_summary(result)

    # 返回 exit code（有高風險問題則返回 1）
    return 1 if result.high_count > 0 else 0


if __name__ == "__main__":
    exit(main())
