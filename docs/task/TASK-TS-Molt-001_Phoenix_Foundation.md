# TASK-TS-Molt-001: Phoenix Foundation - TypeScript 重構與自癒架構藍圖

**狀態**：`Draft / Awaiting Approval`
**負責人**：MartletMolt Engine
**核心目標**：從 Python A/B 系統轉換為 TypeScript 守護者模式 (TS-Guardian)，實現 Git 回滾自癒與多端統一通訊。

---

## 1. 系統架構 (System Architecture)

### 1.1 分層架構
- **Layer 0: Guardian (The Root)**
    - 用途：守護與自癒。
    - 權限：`root`。
    - 核心功能：監控 Backend 健康、執行 `git rollback`、執行 `pnpm install/build`、提供受控的 Root Shell。
- **Layer 1: Backend (The Brain)**
    - 用途：業務邏輯與 API 互動。
    - 核心功能：LLM 溝通、Session 狀態管理 (SQLite)、Tools 執行中心。
    - 持久化：使用 `SQLite` 存儲所有對話記錄，確保「斷線續傳」。
- **Layer 2: Frontends (The Shells)**
    - **CLI (Primary)**: 本次開發重點，純終端介面。
    - **Web (Planned)**: 後續開發。
    - **Messaging Apps (Planned)**: LINE/Telegram。
    - 通訊：所有介面統一透過 WebSocket 或本地 Unix Socket 連接 Backend。

### 1.2 通訊協議 (Unified Protocol)
所有前端統一發送 / 接收以下格式：
```typescript
interface MartletMessage {
  id: string;        // 消息唯一 ID (UUID)
  sessionId: string; // 對話 Session ID
  type: 'cmd' | 'text' | 'stream' | 'status' | 'error';
  payload: any;
  timestamp: number;
}
```

---

## 2. 自癒機制演算法 (Self-Healing Flow)

1. **守護者 (Guardian)** 啟動 **Backend**。
2. **Backend** 運行中...
3. **情境 A：編譯失敗**
   - Guardian 執行 `pnpm build`。
   - 若回傳 code !== 0，分析錯誤並尝试 `git reset --hard HEAD~1`，直到編譯成功。
4. **情境 B：運行時 Crash**
   - Guardian 偵測到 PID 消失。
   - 讀取日誌，判斷是否為程式碼錯誤。
   - 執行修復 (Recover) 流程：`Git Rollback` -> `Rebuild` -> `Restart`。
5. **情境 C：AI 自我修復**
   - Backend 執行報錯，但 AI 尚能運作。
   - AI 呼叫 `RootShellTool` (由 Guardian 提供授權) 執行 `pnpm add xxx` 或修改文件。

---

## 3. 開發階段 (Roadmap)

### Phase 1: 環境搭建與 Guardian 原型
- [ ] 初始化 `pnpm monorepo` 結構。
- [ ] 撰寫 `guardian/main.ts`：實現基本的進程守護與健康檢查。
- [ ] 撰寫 `scripts/repair.sh`：封裝 Git 回滾操作。

### Phase 2: 後端核心與 Session 持久化
- [ ] 建立 `apps/backend`：使用 Fastify 或 Hono。
- [ ] 實作 `SessionStore` (SQLite / Drizzle)：確保故事能「寫完並留存」。
- [ ] 整合 LLM SDK (OpenAI/Anthropic)。

### Phase 3: CLI 前端與統一通訊
- [ ] 建立 `apps/cli`：基於 `ink` 或 `commander`。
- [ ] 實現斷線重連邏輯：啟動 CLI 時自動 sync 最後一個 Session。

---

## 4. 事實與風險核實 (Verification)

- **Root 權限**: 需確認 Docker 容器內 nate 用戶執行 `sudo` 是否免密（根據宿主機配置應已具備）。
- **Git 狀態**: 修復流程嚴格依賴 Git Commit。開發過程中必須養成頻繁 Commit 的習慣，或由系統自動建立 `auto-save` commit。

---

## 5. 核准

**請確認是否「開始實作」Phase 1？**
一旦開始，我將首先在 `/mnt/public/Develop/Projects/external_projects/MartletMolt_TS` (新目錄) 建立基礎結構，以保留舊版 Python 作為參考。
