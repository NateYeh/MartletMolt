# 🛠️ MartletMolt - 開發輔助工具 (Development Tools)

本目錄存放用於提升開發效率、確保代碼品質及自動化文檔生成的輔助工具。這些工具通常在 **非運行時 (Non-runtime)** 使用，旨在輔助開發流程。

## 📋 核心目錄與工具

- **`code_quality_review/`**: 包含代碼品質檢查的相關配置與腳本（如 Ruff, Mypy 規範設定）。
- **`generate_api_docs.py`**: 自動化 API 文檔生成工具，負責從源代碼註釋中提取資訊。
- **`test_doc_generator.py`**: 針對文檔生成器的測試腳本，確保文件提取邏輯正確無誤。

## 🚀 使用指南
這些工具通常直接從命令列調用：
```bash
python tools/generate_api_docs.py
```
