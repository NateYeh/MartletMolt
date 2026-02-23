# 🦅 MartletMolt 任務導航中心

> **最後更新**：2025-02-23  
> **系統狀態**：🟢 核心後端已恢復，Web UI 體驗優化完成。

---

## 📊 進度總覽

| 類別 | 進行中 | 待啟動 | 已完成 | 總計 |
| :--- | :---: | :---: | :---: | :---: |
| 核心/架構 | 0 | 5 | 6 | 11 |
| Web UI | 0 | 1 | 3 | 4 |
| 基礎設施 | 0 | 2 | 6 | 8 |
| **總計** | **0** | **8** | **15** | **23** |

---

## 🔥 當前衝刺 (Active Sprints)
*優先處理影響系統可用性的關鍵 Bug。*

- (目前無進行中任務，切換至 Backlog 或 ARCH-001)

---

## 🗺️ 戰略里程碑 (Strategic Roadmap)

### 🏰 ARCH-001: 雙容器安全沙盒架構 (Evolvable Sandbox) 🔍
- **目標**: 實作「主容器-代理容器」分離，達成 API Key 物理隔離與 AI 進化沙盒化。
- **子任務**:
    - [ ] **TASK-ARCH-001**: 建立主從通訊橋樑 (The Bridge) 📄
    - [ ] **TASK-ARCH-002**: 沙盒容器化與物理隔離 (The Fortress) 📄
    - [ ] **TASK-ARCH-003**: 整合 A/B 進化循環 (The Evolution Loop) 📄
    - [ ] **TASK-ARCH-004**: 安全策略與動態權限 (The Validator) 📄
- **計畫書**: [`docs/plan/dual_container_architecture.md`](../plan/dual_container_architecture.md)
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
| TASK-CORE-009 | 後端緊急恢復與 UI 體驗補完 | 2025-02-23 |
| TASK-WEB-ADV | Web Lite V2 進階功能 (多會話/設定/上傳) | 2025-02-23 |
| TASK-008 | Skills 學習系統 (OpenClaw 風格) | 2025-02-23 |
| TASK-WEB-ADV-01 | 前端訊息可視化增強 (系統提示/思考過程/工具調用) | 2025-02-23 |
| TASK-WEB-FIX-001 | 遠端 WS 連線修復 (雙系統補完) | 2025-02-23 |
| TASK-ORC-03 | 流量代理層實作 (Zero-Downtime) | 2025-02-23 |
| TASK-ORC-02 | 強化同步機制 (Smart Syncer) | 2025-02-23 |
| TASK-ORC-01 | Orchestrator 深度審計 | 2025-02-23 |
| TASK-CORE-007 | 穩定性建設 (Unit Tests) | 2025-02-23 |

---

*"MartletMolt: 像毛球換羽一樣不斷進化的 AI 系統。"
