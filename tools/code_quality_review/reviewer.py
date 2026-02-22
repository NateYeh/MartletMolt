"""程式碼品質審查核心模組。

使用 radon 分析程式碼複雜度，並生成結構化報告。
"""

import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Issue:
    """問題項目。"""

    file_path: str
    issue_type: str  # 'complexity', 'maintainability', 'file_length', 'function_length'
    severity: str  # 'high', 'medium', 'low'
    name: str
    value: Any
    line: int = 0
    suggestion: str = ''


@dataclass
class ReviewResult:
    """審查結果。"""

    timestamp: str
    project_path: str
    issues: list[Issue] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    @property
    def high_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == 'high')

    @property
    def medium_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == 'medium')

    @property
    def low_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == 'low')


class CodeQualityReviewer:
    """程式碼品質審查器。"""

    # 閾值設定
    THRESHOLDS = {
        'complexity': {  # 圈複雜度閾值
            'high': 21,  # D 級以上
            'medium': 11,  # C 級以上
        },
        'maintainability': {  # 可維護性指標閾值
            'high': 10,  # C 級
            'medium': 20,  # B 級
        },
        'file_lines': {  # 檔案行數閾值
            'high': 800,
            'medium': 500,
        },
        'function_lines': {  # 函數行數閾值
            'high': 100,
            'medium': 50,
        },
    }

    # 重構建議
    SUGGESTIONS = {
        'complexity_high': '🔴 嚴重：此函數複雜度過高，建議拆分為多個小函數，每個函數只做一件事。',
        'complexity_medium': '🟡 警告：此函數複雜度偏高，考慮使用策略模式或提取方法降低複雜度。',
        'maintainability_high': '🔴 嚴重：此檔案可維護性極差，建議模組化拆分。',
        'maintainability_medium': '🟡 警告：此檔案可維護性較低，建議增加註解或簡化邏輯。',
        'file_length_high': '🔴 嚴重：此檔案過於肥大，違反單一職責原則，建議拆分為多個模組。',
        'file_length_medium': '🟡 警告：此檔案行數較多，考慮按功能拆分。',
        'function_length_high': '🔴 嚴重：此函數過長，建議拆分為多個子函數，每個不超過 50 行。',
        'function_length_medium': '🟡 警告：此函數略長，考慮提取部分邏輯為獨立函數。',
    }

    def __init__(self, project_path: str):
        """初始化審查器。

        Args:
            project_path: 專案根目錄路徑。
        """
        self.project_path = Path(project_path).resolve()
        self.result = ReviewResult(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            project_path=str(self.project_path),
        )

    def review(self) -> ReviewResult:
        """執行完整審查。

        Returns:
            審查結果。
        """
        self._analyze_complexity()
        self._analyze_maintainability()
        self._analyze_file_lengths()
        self._calculate_stats()
        return self.result

    def _run_radon(self, command: str, target: str = '.') -> str:
        """執行 radon 命令。

        Args:
            command: radon 子命令（cc, mi, raw）。
            target: 目標路徑。

        Returns:
            命令輸出。
        """
        try:
            result = subprocess.run(
                ['radon', command, target, '-j', '-s'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.stdout
        except Exception:
            return '{}'

    def _analyze_complexity(self) -> None:
        """分析圈複雜度。"""
        output = self._run_radon('cc')
        if not output:
            return

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return

        for file_path, items in data.items():
            for item in items:
                complexity = item.get('complexity', 0)
                name = item.get('name', 'unknown')
                item_type = item.get('type', 'function')
                line = item.get('lineno', 0)

                if complexity >= self.THRESHOLDS['complexity']['high']:
                    self.result.issues.append(Issue(
                        file_path=file_path,
                        issue_type='complexity',
                        severity='high',
                        name=f'{item_type} {name}',
                        value=complexity,
                        line=line,
                        suggestion=self.SUGGESTIONS['complexity_high'],
                    ))
                elif complexity >= self.THRESHOLDS['complexity']['medium']:
                    self.result.issues.append(Issue(
                        file_path=file_path,
                        issue_type='complexity',
                        severity='medium',
                        name=f'{item_type} {name}',
                        value=complexity,
                        line=line,
                        suggestion=self.SUGGESTIONS['complexity_medium'],
                    ))

    def _analyze_maintainability(self) -> None:
        """分析可維護性指標。"""
        output = self._run_radon('mi')
        if not output:
            return

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return

        for file_path, info in data.items():
            mi_value = info.get('mi', 100)
            rank = info.get('rank', 'A')

            if rank == 'C':  # MI < 10
                self.result.issues.append(Issue(
                    file_path=file_path,
                    issue_type='maintainability',
                    severity='high',
                    name=f'檔案可維護性 (MI={mi_value:.1f}, Rank={rank})',
                    value=mi_value,
                    suggestion=self.SUGGESTIONS['maintainability_high'],
                ))
            elif rank == 'B':  # 10 <= MI < 20
                self.result.issues.append(Issue(
                    file_path=file_path,
                    issue_type='maintainability',
                    severity='medium',
                    name=f'檔案可維護性 (MI={mi_value:.1f}, Rank={rank})',
                    value=mi_value,
                    suggestion=self.SUGGESTIONS['maintainability_medium'],
                ))

    def _analyze_file_lengths(self) -> None:
        """分析檔案行數和函數行數。"""
        output = self._run_radon('raw')
        if not output:
            return

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return

        for file_path, info in data.items():
            loc = info.get('loc', 0)  # radon 使用小寫 'loc'

            # 檔案行數檢查
            if loc >= self.THRESHOLDS['file_lines']['high']:
                self.result.issues.append(Issue(
                    file_path=file_path,
                    issue_type='file_length',
                    severity='high',
                    name=f'檔案行數 ({loc} 行)',
                    value=loc,
                    suggestion=self.SUGGESTIONS['file_length_high'],
                ))
            elif loc >= self.THRESHOLDS['file_lines']['medium']:
                self.result.issues.append(Issue(
                    file_path=file_path,
                    issue_type='file_length',
                    severity='medium',
                    name=f'檔案行數 ({loc} 行)',
                    value=loc,
                    suggestion=self.SUGGESTIONS['file_length_medium'],
                ))

    def _calculate_stats(self) -> None:
        """計算統計資訊。"""
        output = self._run_radon('raw')
        total_loc = 0
        total_files = 0

        try:
            data = json.loads(output)
            total_files = len(data)
            total_loc = sum(info.get('loc', 0) for info in data.values())  # radon 使用小寫 'loc'
        except json.JSONDecodeError:
            pass

        # 按問題類型統計
        issue_by_type: dict[str, int] = {}
        for issue in self.result.issues:
            issue_by_type[issue.issue_type] = issue_by_type.get(issue.issue_type, 0) + 1

        self.result.stats = {
            'total_files': total_files,
            'total_loc': total_loc,
            'total_issues': len(self.result.issues),
            'high_issues': self.result.high_count,
            'medium_issues': self.result.medium_count,
            'low_issues': self.result.low_count,
            'issues_by_type': issue_by_type,
        }
