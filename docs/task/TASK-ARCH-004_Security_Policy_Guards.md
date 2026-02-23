# TASK-ARCH-004: 安全策略與動態權限 (The Validator)

## 1. 目標
層層加固沙盒，實作資源限制與動態工具權限，確保系統在 AI 自我重寫時具備抵抗力。

## 2. 詳細規格
- **資源配額 (Resource Quotas)**:
  - 限制 Sandbox 的 CPU 使用率 (如 max 2 cores)。
  - 限制 Memory 使用上限 (如 max 1GB)，防止遞歸死循環導致 OOM。
- **動態工具注入**:
  - Host 實作工具執行過濾器。當 Agent 調用如 `write_file` 於敏感路徑時，由 Host 進行策略阻斷。
  - 工具調用必須帶有單次任務的 Session ID，確保審計。
- **異常行為偵測**:
  - 監控 Sandbox 的網路流量異常。

## 3. 修改路徑清單 (預計)
- `backend/system_{a|b}/martlet_molt/core/security.py` (新增)
- `docker-compose.yml` (資源限制配置)
- `Config/security_policies.yaml` (新增)

## 4. 驗證方式
- 執行一段高負載 Python 程式碼，觀察 Docker Container 資源限制是否生效。
- 測試修改受保護目錄，確認 Host 能正確攔截並回報權限錯誤。

---
**狀態**: 📋 待啟動 (Planned)
**建立日期**: 2025-02-23
