# YAML 檢查工具使用指南

本文檔說明如何在 MartletMolt 專案中使用 YAML 檢查工具。

## 🛠️ 已安裝的工具

### 1. yamllint - YAML 檢查工具

功能類似 Python 的 Ruff，用於檢查 YAML 檔案格式。

**使用方式：**
```bash
# 檢查所有 YAML 檔案
yamllint -c .yamllint .

# 檢查特定檔案
yamllint -c .yamllint config.yaml

# 使用 Makefile
make yaml-check
```

### 2. yamlfix - YAML 自動修正工具

功能類似 `ruff --fix`，自動修正 YAML 格式問題。

**使用方式：**
```bash
# 自動修正所有 YAML 檔案
yamlfix **/*.yaml **/*.yml

# 只檢查不修正
yamlfix --check **/*.yaml

# 使用 Makefile
make yaml-fix
```

## 📋 配置檔案

### .yamllint

YAML 檢查規則配置，位於專案根目錄。

**主要規則：**
- 行長度上限：180 字元
- 縮排：2 空格
- 結尾必須換行
- 禁止尾隨空格
- 禁止重複 key

### pyproject.toml

包含 `yamlfix` 的配置設定。

## 🚀 快速開始

### 完整驗證流程
```bash
# 1. 檢查 Python 程式碼
ruff check .
ruff format .

# 2. 檢查 YAML 檔案
yamllint -c .yamllint .

# 3. 或使用 Makefile 一次搞定
make lint
```

### 自動修正
```bash
# 修正 Python 程式碼
ruff check . --fix
ruff format .

# 修正 YAML 檔案
yamlfix **/*.yaml **/*.yml

# 或使用 Makefile
make format
```

## 📁 專案檔案結構

```
MartletMolt/
├── .yamllint                      # Yamllint 配置
├── .pre-commit-config.yaml        # Pre-commit hooks
├── pyproject.toml                 # 專案配置（含 yamlfix）
├── Makefile                       # 常用指令
├── scripts/
│   ├── fix_yaml.py               # YAML 修正腳本
│   └── validate_yaml.py          # YAML 驗證驗證腳本
└── examples/config/
    └── good_example.yaml         # 正確的 YAML 範例
```

## 🎯 最佳實踐

### YAML 檔案撰寫建議

✅ **推薦寫法：**
```yaml
# 資料庫設定
database:
  host: localhost
  port: 5432
  name: myapp_db

# 明確用引號包裹特殊值
country: "no"        # 避免"挪威"被解析成 false
version: "1.10"      # 避免被解析成 float 1.1

# 多行字串使用 |
description: |
  這是一段
  多行描述
```

❌ **避免的寫法：**
```yaml
# ❌ 縮排不一致
database:
  host: localhost
   port: 5432      # 錯誤！多了一個空格

# ❌ 未用引號的特殊值
country: no         # 會被解析成 false！
version: 1.10       # 會被解析成 1.1！
```

## 🔧 Pre-commit Hooks

專案已配置 pre-commit hooks，會在每次 commit 前自動執行：

```bash
# 安裝 pre-commit
pip install pre-commit
pre-commit install

# 手動執行所有 hooks
pre-commit run --all-files
```

**自動執行的檢查：**
1. ✅ Ruff (Python 格式化與檢查)
2. ✅ Pyright (型別檢查)
3. ✅ Yamllint (YAML 檢查)
4. ✅ 檔案格式檢查（換行符、尾隨空格等）
5. ✅ 敏感資訊檢測

## 📊 工具對照表

| Python 工具 | YAML 工具 | 功能 |
|------------|----------|------|
| `ruff check` | `yamllint` | 檢查語法與風格 |
| `ruff format` | `yamlfix` | 自動格式化 |
| `ruff --fix` | `yamlfix` | 自動修正問題 |
| `pyright` | - | 型別檢查 |

## 🚨 常見問題

### Q1: yamllint 報錯 "no new line character"
**A:** 檔案結尾必須有換行符。執行 `yamlfix` 自動修正。

### Q2: yamllint 報錯 "trailing spaces"
**A:** 行尾有空格。執行 `yamlfix` 或手動刪除。

### Q3: yamlfix 把我的註解刪掉了
**A:** 這是 yamlfix 的已知限制。建議使用 yamllint 檢查，並手動修正關鍵區域。

### Q4: 如何在 CI/CD 中整合？
**A:** 使用 Makefile 指令：
```yaml
# GitHub Actions 範例
- name: Check YAML
  run: make yaml-check
```

## 📚 參考資源

- [yamllint 官方文檔](https://yamllint.readthedocs.io/)
- [yamlfix GitHub](https://github.com/lyz-code/yamlfix)
- [YAML 規範](https://yaml.org/spec/1.2/spec.html)
- [Pre-commit 官方文檔](https://pre-commit.com/)