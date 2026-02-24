# AI_OPERATIONS.md — MartletMolt AI 操作快捷指南

> **AI 必讀**：這是我（守護者）在管理本系統時的高頻指令庫。

---

## 🚦 流量調度指令 (Orchestration)

### 1. 查詢系統狀態
```bash
curl -s http://localhost:8000/status | python3 -m json.tool
```

### 2. 切換活躍系統 (A -> B)
```bash
curl -X POST http://localhost:8000/switch/system_b
```

### 3. 切換活躍系統 (B -> A)
```bash
curl -X POST http://localhost:8000/switch/system_a
```

---

## 🛠️ 進化與維護指令 (Maintenance)

### 1. 重啟目標容器 (代碼修改後生效)
```bash
# 重啟 B 系統
curl -X POST http://localhost:8000/restart/system_b
```

### 2. 查看容器日誌
```bash
# 查看活動系統日誌
docker logs martlet-system-a --tail 50
```

### 3. 重建基礎鏡像 (新增套件時)
```bash
cd /mnt/work/py_works/external_projects/MartletMolt
docker build -t martlet-base .
```

---

## 📦 版本保存 (Git Operations)

### 1. 完成進化後推送
```bash
git add .
git commit -m "evolution: description of changes"
git push
```

---
**提示**：在進行「手術」前，請務必確認當前 `active_system` 是哪一個，並修改「另一個」系統的代碼。
