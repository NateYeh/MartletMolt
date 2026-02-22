# 程式碼品質審查工具

一個輕量級的 Python 程式碼品質審查工具，使用 `radon` 分析程式碼複雜度，並生成結構化報告。

## 功能特點

- **圈複雜度分析** - 識別過於複雜的函數
- **可維護性指標** - 評估檔案的可維護性
- **檔案行數檢查** - 找出肥大檔案
- **結構化報告** - 輸出 Markdown 和 JSON 格式

## 安裝依賴

```bash
pip install radon
```

## 使用方式

### 方式 A：直接執行

```bash
python tools/code_quality_review/cli.py
```

### 方式 B：進入目錄執行

```bash
cd tools/code_quality_review && python cli.py
```

## 閾值設定

| 指標 | 🟡 中風險 | 🔴 高風險 |
|------|----------|----------|
| 圈複雜度 (CC) | ≥ 11 (C 級) | ≥ 21 (D 級以上) |
| 可維護性 (MI) | < 20 (B 級) | < 10 (C 級) |
| 檔案行數 | > 500 行 | > 800 行 |
| 函數行數 | > 50 行 | > 100 行 |

## 輸出報告

報告會生成於 `reports/` 目錄：

```
reports/
├── quality_review_YYYYMMDD.md    # 人類可讀報告
└── quality_review_YYYYMMDD.json  # 機器可讀報告
```

## 報告範例

### 終端機輸出

```
============================================================
📊 程式碼品質審查結果
============================================================
專案路徑: /path/to/project
掃描檔案: 42 個
總行數: 3521 行
------------------------------------------------------------
問題總數: 5
  🔴 高風險: 1
  🟡 中風險: 4
  🟢 低風險: 0
============================================================

🔴 高風險問題（前 5 個）:
  1. ./src/services/data_processor.py
     └─ function process_data (值: 25)

📄 詳細報告已生成於 reports/ 目錄
```

### Markdown 報告結構

```markdown
# 程式碼品質審查報告

**審查時間**: 2024-01-15 10:30:00
**專案路徑**: /path/to/project

---

## 📊 總覽

| 指標 | 數值 |
|------|------|
| 掃描檔案數 | 42 |
| 總程式碼行數 | 3521 |
| 問題總數 | 5 |
| 🔴 高風險 | 1 |
| 🟡 中風險 | 4 |

## 🔍 問題詳情

### 🔴 高風險問題
...
```

## JSON 報告結構

```json
{
  "timestamp": "2024-01-15 10:30:00",
  "project_path": "/path/to/project",
  "stats": {
    "total_files": 42,
    "total_loc": 3521,
    "total_issues": 5,
    "high_issues": 1,
    "medium_issues": 4,
    "low_issues": 0
  },
  "issues": [
    {
      "file_path": "./src/services/data_processor.py",
      "issue_type": "complexity",
      "severity": "high",
      "name": "function process_data",
      "value": 25,
      "line": 42,
      "suggestion": "..."
    }
  ]
}
```

## Exit Code

- `0` - 沒有高風險問題
- `1` - 存在高風險問題（可用於 CI/CD）

## 擴展修改

修改 `reviewer.py` 中的 `THRESHOLDS` 和 `SUGGESTIONS` 可自定義閾值和建議內容。

```python
THRESHOLDS = {
    'complexity': {
        'high': 21,
        'medium': 11,
    },
    'file_lines': {
        'high': 800,
        'medium': 500,
    },
    # ...
}
```

## 作為 AI 交接任務

此工具適合作為 AI 交接的週期性任務，執行後生成的報告可直接提供給下一任 AI 閱讀，快速了解專案程式碼品質狀況。

---

**版本**: 1.0.0