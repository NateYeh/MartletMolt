---
name: api-docs-generator
description: 自動掃描 FastAPI 後端路由並生成 Markdown 文件。當用戶要求「更新 API 文件」或「查看接口定義」時使用。
metadata:
  emoji: 📚
  version: 1.0.0
---

# API Docs Generator Skill

本技能可以提取 MartletMolt 後端的路由資訊，自動產出標準的 API 指南。

## 使用場景
- 剛新增了 FastAPI Endpoint，需要同步更新文件。
- 向人類報告目前的接口清單。

## 參數
- `system`: (選填) 指定掃描 'a' 或 'b' 系統，預設為 'a'。
