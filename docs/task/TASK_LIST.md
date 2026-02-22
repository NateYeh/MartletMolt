# 🦅 MartletMolt 任務導航中心

> **最後更新**：2025-02-22  
> **系統狀態**：WebSocket 協議升級完成！

---

## 📊 進度總覽

| 類別 | 進行中 | 待啟動 | 已完成 | 總計 |
| :--- | :---: | :---: | :---: | :---: |
| 核心後端 | 0 | 2 | 2 | 4 |
| Web UI | 0 | 1 | 3 | 4 |
| 基礎設施 | 1 | 0 | 3 | 4 |
| **總計** | **1** | **3** | **8** | **12** |

---

## 🔥 當前衝刺 (Active Sprints)
*優先處理影響系統可用性的核心升級。*

### TASK-007: 穩定性建設 (Unit Tests) ⏳
- **說明**: 補全系統核心模組的單元測試。
- **目標**: 確保 Provider, Agent, Channel 邏輯正確。
- **當前進度**: 20% (僅完成 Streaming Buffer 測試)。

---

## 📋 任務儲備 (Backlog)
*已規劃完成，待當前衝刺結束後啟動。*

### 🛠️ 核心功能增強
- **TASK-001: Anthropic Provider 實作** ❌
    - 任務：實作 Claude 模型的對話與串流介接。
- **TASK-002: Tool 參數嚴格驗證** ❌
    - 任務：引入 JSON Schema 驗證工具調用參數。
- **TASK-008: Skills 學習系統** 📄
    - 任務：動態技能學習與儲存機制。
    - 文件：[`../skills_plan.md`](../skills_plan.md)

### 🎨 Web 介面演進
- **TASK-WEB-ADV: Web Lite V2 進階功能** 📄
    - 任務：會話管理、歷史記錄持久化、文件上傳。
    - 文件：[`TASK_web_lite_v2_advanced_features.md`](./TASK_web_lite_v2_advanced_features.md)

---

## 📁 已完成任務 (Completed)
*查看 `docs/task/Completed/` 目錄。*

| ID | 任務名稱 | 完成日期 |
| :--- | :--- | :--- |
| TASK-011 | WebSocket 協議遷移 | 2025-02-22 |
| TASK-010 | Web UI 連通性修復 | 2025-02-22 |
| TASK-000 | 串流緩衝架構 | 2025-02-22 |
| CH-001 | BaseChannel 抽象架構 | 2025-02-22 |
| CH-002 | WebSocket 通道 (WebChannel) | 2025-02-22 |
| CH-003 | CLI 交互通道 | 2025-02-22 |
| UI-001 | Web Lite V2 核心 UI | 2025-02-22 |
| SYS-001 | 系統 A/B 同步工具 | 2025-02-22 |

---

*"MartletMolt: 像毛球換羽一樣不斷進化的 AI 系統。"