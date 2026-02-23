# 🦅 MartletMolt 任務導航中心

> **最後更新**：2025-02-23  
> **系統狀態**：緊急除錯中 - 遠端連線問題。

---

## 📊 進度總覽

| 類別 | 進行中 | 待啟動 | 已完成 | 總計 |
| :--- | :---: | :---: | :---: | :---: |
| 核心後端 | 0 | 1 | 5 | 6 |
| Web UI | 1 | 1 | 3 | 5 |
| 基礎設施 | 0 | 2 | 6 | 8 |
| **總計** | **1** | **4** | **14** | **19** |

---

## 🔥 當前衝刺 (Active Sprints)
*優先處理影響系統可用性的關鍵 Bug。*

*(目前沒有進行中的衝刺)*

---

## 🗺️ 戰略里程碑 (Strategic Roadmap)
*長遠架構目標，需達成特定條件後啟動。*

### 🏰 ARCH-001: 雙容器安全沙盒架構 (Evolvable Sandbox) 🔍
- **目標**: 實作「主容器-代理容器」分離，達成 API Key 物理隔離與 AI 進化沙盒化。
- **計畫書**: [`docs/plan/dual_container_architecture.md`](../plan/dual_container_architecture.md)
- **啟動條件**: 
    1. TASK-CORE-007 (核心測試) 覆蓋率 > 80%。 (✅ 已達成)
    2. 基礎設施支持 A/B 同步穩定。 (✅ 已達成)
- **狀態**: 🚀 準備中 (Ready to Start)

---

## 📋 任務儲備 (Backlog)
*已規劃完成，待當前衝刺結束後啟動。*

### 🛠️ 核心功能增強
- **TASK-001: Anthropic Provider 實作** (⏸️ 缺 Key 暫存) 📄
- **TASK-015: Gemini (Google) Provider 實作** 📄
- **TASK-002: Tool 參數嚴格驗證** 📄

---

## 📁 已完成任務 (Completed)
*查看 `docs/task/Completed/` 目錄。*

| ID | 任務名稱 | 完成日期 |
| :--- | :--- | :--- |
| TASK-008 | Skills 學習系統 (OpenClaw 風格) | 2025-02-23 |
| TASK-WEB-ADV-01 | 前端訊息可視化增強 (系統提示/思考過程/工具調用) | 2025-02-23 |
| TASK-WEB-FIX-001 | 遠端 WS 連線修復 (雙系統補完) | 2025-02-23 |
| TASK-ORC-03 | 流量代理層實作 (Zero-Downtime) | 2025-02-23 |
| TASK-ORC-02 | 強化同步機制 (Smart Syncer) | 2025-02-23 |
| TASK-ORC-01 | Orchestrator 深度審計 | 2025-02-23 |
| TASK-CORE-007 | 穩定性建設 (Unit Tests) | 2025-02-23 |

---

*"MartletMolt: 像毛球換羽一樣不斷進化的 AI 系統。"
