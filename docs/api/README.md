# API 文檔生成系統

## 📝 概述

本系統使用 **YAML + Jinja2 模板** 來管理和生成 API 文檔，解決了直接編輯大型 Markdown 文件的困難。

## 🏗️ 架構

```
docs/
├── api/                      # API 定義 (YAML)
│   ├── config.yaml          # 文檔配置（版本、Base URL 等）
│   ├── endpoints/           # 端點定義
│   │   ├── health.yaml
│   │   ├── status.yaml
│   │   ├── chat.yaml
│   │   ├── chat_stream.yaml
│   │   ├── sessions_list.yaml
│   │   ├── sessions_detail.yaml
│   │   └── sessions_delete.yaml
│   ├── schemas/             # 共用 Schema
│   │   └── common.yaml      # 錯誤碼、資料結構
│   └── sdk/                 # SDK 定義
│       └── typescript.yaml  # TypeScript SDK
├── templates/               # Jinja2 模板
│   └── api_sdk.md.j2        # Markdown 模板
└── API_SDK.md              # 生成的輸出文件
```

## 🚀 使用方式

### 生成文檔

```bash
# 使用 Makefile（推薦）
make docs

# 或直接執行
python tools/generate_api_docs.py
```

### 完整檢查 + 文檔生成

```bash
make check-all
```

## 📝 如何新增 API 端點

### 1. 創建端點定義檔案

在 `docs/api/endpoints/` 目錄下創建新的 YAML 檔案：

```yaml
# docs/api/endpoints/new_endpoint.yaml

order: 8  # 排序順序
title: 新端點名稱

endpoint:
  method: GET|POST|PUT|DELETE
  path: /path/to/endpoint
  description: 端點描述

request:
  headers:
    - name: Content-Type
      value: application/json
      required: true
  parameters:
    - name: param_name
      type: string
      required: true|false
      default: "default_value"  # 可選
      description: 參數描述

response:
  status_code: 200
  description: 成功回應
  body:
    field: value
  fields:
    - name: field
      type: string
      description: 欄位描述

status_codes:
  - code: 200
    description: 成功
  - code: 400
    description: 錯誤

examples:
  curl: |
    curl http://localhost:8001/endpoint
  python: |
    import requests
    # ...
  javascript: |
    const response = await fetch('http://localhost:8001/endpoint');
    # ...
```

### 2. 重新生成文檔

```bash
make docs
```

## 🔧 如何修改現有端點

1. 找到對應的 YAML 檔案（例如 `documents/api/endpoints/chat.yaml`）
2. 修改內容
3. 執行 `make docs` 重新生成

## 📚 YAML Schema 說明

### config.yaml

配置文檔基本資訊：

```yaml
metadata:
  title: 文檔標題
  version: "0.1.0"
  base_url: http://localhost:8001
  last_updated: 2025-01-15

overview: |
  文檔概述

features:
  - icon: "✅"
    title: 功能名稱
    description: 功能描述

tech_specs:
  framework: FastAPI
  data_format: JSON
```

### endpoints/*.yaml

每個端點的完整定義，包含：
- `order`: 排序用
- `title`: 端點標題
- `endpoint`: 方法、路徑、描述
- `request`: 請求參數、headers
- `response`: 回應格式、欄位
- `status_codes`: 狀態碼說明
- `examples`: 範例代碼

### schemas/common.yaml

共用定義：
- 錯誤回應格式
- 共用資料結構（SessionInfo, Message 等）

## 🎨 模板系統

模板位於 `docs/templates/api_sdk.md.j2`，使用 Jinja2 語法。

### 可用變量

- `config`: 配置資訊
- `endpoints`: 端點列表（已排序）
- `common_schemas`: 共用 Schema
- `sdk`: SDK 定義
- `api_endpoints_table`: 自動生成的端點表格

### 自定義模板

如需修改文檔結構或格式，直接編輯 `api_sdk.md.j2` 即可。

## ✅ 優勢

1. **易於維護**: 修改 YAML 即可，不用管 Markdown 格式
2. **結構化資料**: YAML 可被程式解析，未來可擴充生成 OpenAPI
3. **降低錯誤**: AI 可輕鬆讀寫 YAML，降低格式錯誤
4. **Git 友善**: YAML 是純文字，容易追蹤變更
5. **模組化設計**: 每個端點一個檔案，職責分離

## 🔮 未來擴充

- [ ] 生成 OpenAPI 3.0 規格
- [ ] 生成 Postman Collection
- [ ] 多語言 SDK 生成
- [ ] 自動同步前後端文檔

## 📖 相關資源

- [Jinja2 模板文檔](https://jinja.palletsprojects.com/)
- [YAML 規格](https://yaml.org/)
- [OpenAPI 規格](https://swagger.io/specification/)