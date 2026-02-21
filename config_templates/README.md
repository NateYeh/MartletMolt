# Config Templates

配置範本目錄，提供用戶參考的配置範例。

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `settings.yaml.example` | 主配置範例 |
| `.env.example` | 環境變數範例 |
| `good_example.yaml` | 完整配置範例 |

## 使用方式

1. 複製 `settings.yaml.example` 到 `Config/settings.yaml`
2. 複製 `.env.example` 到 `Config/.env`
3. 填入實際的 API Keys 和設定

```bash
# 複製範本
cp config_templates/settings.yaml.example Config/settings.yaml
cp config_templates/.env.example Config/.env

# 編輯配置
vim Config/settings.yaml
vim Config/.env
```

## 注意事項

- `Config/` 目錄不會上傳至 Git（已在 .gitignore 中排除）
- API Keys 等敏感資訊請填入 `Config/.env`
- 請勿將敏感資訊填入 `config_templates/` 中的範例檔案