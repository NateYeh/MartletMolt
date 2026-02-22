# SKILLS System - Future Plan

> 讓 AI 能夠動態學習、創建、執行可重用的技能模組

---

## 📋 概述

SKILLS 系統是一個讓 AI Agent 能夠**動態擴展能力**的框架。用戶可以通過自然語言描述需求，AI 自動創建或更新 Skills，並在未來的對話中重複使用。

### 核心理念

```
傳統方式：AI 每次對話都需要重新學習如何做事
SKILLS 方式：AI 學習一次，永久保存為 Skill，隨時調用
```

---

## 🎯 使用場景

### 場景 1：用戶首次請求

```
用戶：「我想要支援現在很紅的 SKILLS」

Agent 思考過程：
1. 分析需求：用戶想要一個 Skill 系統
2. 搜尋資料：了解 SKILLS 是什麼
3. 設計架構：規劃 Skill 系統結構
4. 創建檔案：實現 Skill 基礎設施
5. 測試驗證：確保系統可用
6. 自我進化：通過 A/B 架構升級系統

結果：專案獲得完整的 SKILLS 系統
```

### 場景 2：用戶再次使用

```
用戶：「用 code_review skill 幫我審查這段程式碼」

Agent 思考過程：
1. 檢查 Skills 註冊表
2. 找到 code_review skill
3. 載入並執行

結果：直接使用已有的 Skill，無需重新學習
```

### 場景 3：創建新 Skill

```
用戶：「創建一個 git_commit skill，根據變更自動生成 commit message」

Agent 思考過程：
1. 理解 Skill 需求
2. 設計 Skill 邏輯
3. 創建 Skill 檔案
4. 註冊到系統

結果：新 Skill 可立即使用
```

---

## 🏗️ 系統架構

### 目錄結構

```
MartletMolt/
├── skills/                              # Skills 存放目錄 (用戶可編輯)
│   ├── __init__.py
│   ├── code_review.py                   # 程式碼審查
│   ├── web_search.py                    # 網頁搜尋
│   ├── documentation.py                 # 文件生成
│   ├── data_analysis.py                 # 資料分析
│   └── git_commit.py                    # Git Commit 生成
│
├── system_a/martlet_molt/
│   ├── skills/                          # Skill 系統核心
│   │   ├── __init__.py
│   │   ├── base.py                      # Skill 基類
│   │   ├── manager.py                   # Skill 管理器
│   │   ├── loader.py                    # 動態載入器
│   │   ├── registry.py                  # 註冊表
│   │   ├── executor.py                  # 執行器 (沙箱)
│   │   └── validator.py                 # 驗證器
│   │
│   └── tools/
│       └── skill.py                     # Skill Tool (AI 調用入口)
```

### 核心組件

```
┌─────────────────────────────────────────────────────────────────┐
│                        Agent 核心                                │
│  - 接收用戶請求                                                  │
│  - 決定是否使用 Skill                                           │
│  - 可調用 skill_tool 創建/管理 Skills                           │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Skill Tool                                  │
│  - create: 創建新 Skill                                         │
│  - update: 更新現有 Skill                                       │
│  - delete: 刪除 Skill                                           │
│  - execute: 執行 Skill                                          │
│  - list: 列出所有 Skills                                        │
│  - search: 搜尋 Skills                                          │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Skill Manager                                │
│  - 載入和管理 Skills                                            │
│  - 驗證 Skill 安全性                                            │
│  - 執行 Skill (沙箱環境)                                        │
│  - 維護 Skill 元數據                                            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Skill Registry                               │
│  - 註冊表存儲                                                   │
│  - Skill 版本管理                                               │
│  - 依賴關係追蹤                                                 │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Skills 目錄                                │
│  skills/*.py - 用戶可編輯的 Skill 檔案                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📐 設計規格

### Skill 基類定義

```python
# system_a/martlet_molt/skills/base.py

from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class SkillMetadata(BaseModel):
    """Skill 元數據"""
    name: str
    version: str = "1.0.0"
    description: str
    author: str = "AI"
    tags: list[str] = []
    created_at: str
    updated_at: str
    requires: list[str] = []  # 依賴的其他 Skills
    dangerous: bool = False   # 是否需要用戶確認


class SkillResult(BaseModel):
    """Skill 執行結果"""
    success: bool
    output: Any = None
    error: str = ""
    metadata: dict = {}


class SkillStatus(str, Enum):
    """Skill 狀態"""
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"
    PENDING = "pending"  # 需要審核


class BaseSkill(ABC):
    """Skill 抽象基類"""
    
    # 元數據 (子類必須定義)
    metadata: SkillMetadata
    
    # 狀態
    status: SkillStatus = SkillStatus.ACTIVE
    
    @abstractmethod
    def execute(self, context: dict, **kwargs) -> SkillResult:
        """
        執行 Skill
        
        Args:
            context: 執行上下文 (包含 session, agent, tools 等)
            **kwargs: Skill 參數
        
        Returns:
            SkillResult: 執行結果
        """
        pass
    
    def validate_parameters(self, **kwargs) -> bool:
        """驗證參數"""
        return True
    
    def pre_execute(self, context: dict, **kwargs) -> bool:
        """執行前檢查 (可選)"""
        return True
    
    def post_execute(self, context: dict, result: SkillResult) -> None:
        """執行後處理 (可選)"""
        pass
    
    def to_prompt(self) -> str:
        """轉換為 Prompt 格式 (讓 AI 知道如何使用此 Skill)"""
        return f"""
## Skill: {self.metadata.name}

{self.metadata.description}

### 使用方式
- 名稱: {self.metadata.name}
- 版本: {self.metadata.version}
- 標籤: {', '.join(self.metadata.tags)}

### 參數
{self._describe_parameters()}

### 範例
{self._describe_examples()}
"""
    
    @abstractmethod
    def _describe_parameters(self) -> str:
        """描述參數"""
        pass
    
    @abstractmethod
    def _describe_examples(self) -> str:
        """描述範例"""
        pass
```

### Skill Tool 定義

```python
# system_a/martlet_molt/tools/skill.py

from typing import Literal, Optional
from martlet_molt.tools.base import BaseTool, ToolResult
from martlet_molt.skills.manager import SkillManager


class SkillTool(BaseTool):
    """Skill 管理 Tool"""
    
    name = "skill"
    description = "管理 AI Skills：創建、更新、刪除、執行、列出技能"
    
    parameters_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create", "update", "delete", "execute", "list", "search", "info"],
                "description": "要執行的操作"
            },
            "skill_name": {
                "type": "string",
                "description": "Skill 名稱"
            },
            "skill_description": {
                "type": "string",
                "description": "Skill 描述"
            },
            "skill_code": {
                "type": "string",
                "description": "Skill Python 程式碼"
            },
            "skill_parameters": {
                "type": "object",
                "description": "Skill 執行參數"
            },
            "search_query": {
                "type": "string",
                "description": "搜尋關鍵字"
            }
        },
        "required": ["action"]
    }
    
    def __init__(self, manager: Optional[SkillManager] = None):
        self.manager = manager or SkillManager()
    
    def execute(
        self,
        action: Literal["create", "update", "delete", "execute", "list", "search", "info"],
        skill_name: str = "",
        skill_description: str = "",
        skill_code: str = "",
        skill_parameters: dict = None,
        search_query: str = "",
    ) -> ToolResult:
        """執行 Skill 操作"""
        
        if action == "create":
            return self._create_skill(skill_name, skill_description, skill_code)
        
        elif action == "update":
            return self._update_skill(skill_name, skill_description, skill_code)
        
        elif action == "delete":
            return self._delete_skill(skill_name)
        
        elif action == "execute":
            return self._execute_skill(skill_name, skill_parameters or {})
        
        elif action == "list":
            return self._list_skills()
        
        elif action == "search":
            return self._search_skills(search_query)
        
        elif action == "info":
            return self._get_skill_info(skill_name)
        
        else:
            return ToolResult(success=False, error=f"Unknown action: {action}")
    
    def _create_skill(self, name: str, description: str, code: str) -> ToolResult:
        """創建新 Skill"""
        try:
            skill = self.manager.create_skill(name, description, code)
            return ToolResult(
                success=True,
                data={
                    "name": skill.metadata.name,
                    "description": skill.metadata.description,
                    "message": f"Skill '{name}' created successfully"
                }
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _execute_skill(self, name: str, parameters: dict) -> ToolResult:
        """執行 Skill"""
        try:
            result = self.manager.execute_skill(name, parameters)
            return ToolResult(
                success=result.success,
                data=result.output,
                error=result.error,
                metadata=result.metadata
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    # ... 其他方法
```

---

## 🛡️ 安全設計

### 沙箱執行

```python
# system_a/martlet_molt/skills/executor.py

import ast
import RestrictedPython
from typing import Any
from loguru import logger


class SkillExecutor:
    """Skill 執行器 - 沙箱環境"""
    
    # 允許的模組白名單
    ALLOWED_MODULES = {
        # 標準庫
        "json", "re", "datetime", "math", "random", "string",
        "collections", "itertools", "functools", "typing",
        # 專案模組
        "martlet_molt.tools",
        "martlet_molt.skills",
    }
    
    # 禁止的操作
    FORBIDDEN_OPERATIONS = {
        "exec", "eval", "compile", "open",  # 執行任意代碼
        "import", "__import__",  # 動態導入
        "os.system", "subprocess",  # 系統命令
    }
    
    def __init__(self, max_execution_time: int = 30):
        self.max_execution_time = max_execution_time
    
    def validate_code(self, code: str) -> tuple[bool, str]:
        """
        驗證 Skill 代碼安全性
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # 解析 AST
            tree = ast.parse(code)
            
            # 檢查禁止的操作
            for node in ast.walk(tree):
                # 檢查函數調用
                if isinstance(node, ast.Call):
                    func_name = self._get_func_name(node)
                    if func_name in self.FORBIDDEN_OPERATIONS:
                        return False, f"Forbidden operation: {func_name}"
                
                # 檢查導入
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module = node.module or ""
                    if not any(module.startswith(allowed) for allowed in self.ALLOWED_MODULES):
                        return False, f"Module not allowed: {module}"
            
            return True, ""
            
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
    
    def execute(self, skill: "BaseSkill", context: dict, **kwargs) -> "SkillResult":
        """
        在沙箱環境中執行 Skill
        """
        # 1. 驗證代碼
        is_valid, error = self.validate_code(inspect.getsource(skill.__class__))
        if not is_valid:
            return SkillResult(success=False, error=f"Security validation failed: {error}")
        
        # 2. 檢查是否需要用戶確認
        if skill.metadata.dangerous:
            # TODO: 請求用戶確認
            logger.warning(f"Dangerous skill execution: {skill.metadata.name}")
        
        # 3. 執行 (帶超時)
        try:
            with timeout(self.max_execution_time):
                result = skill.execute(context, **kwargs)
                return result
        except TimeoutError:
            return SkillResult(success=False, error="Skill execution timed out")
        except Exception as e:
            logger.exception(f"Skill execution failed: {e}")
            return SkillResult(success=False, error=str(e))
```

### Skill 審核機制

```python
# 危險操作需要用戶確認
DANGEROUS_PATTERNS = [
    r"file_write",      # 寫入檔案
    r"shell",           # 執行命令
    r"delete",          # 刪除操作
    r"drop_table",      # 資料庫操作
    r"format",          # 格式化
]

# 自動審核規則
AUTO_APPROVE_RULES = [
    "skill.created_by == 'user'",           # 用戶創建的
    "skill.execution_count < 100",          # 執行次數少
    "not skill.metadata.dangerous",         # 非危險操作
]
```

---

## 📝 範例 Skills

### 範例 1：Code Review Skill

```python
# skills/code_review.py

from datetime import datetime
from martlet_molt.skills.base import BaseSkill, SkillMetadata, SkillResult
from martlet_molt.tools import ToolRegistry


class CodeReviewSkill(BaseSkill):
    """程式碼審查 Skill"""
    
    metadata = SkillMetadata(
        name="code_review",
        version="1.0.0",
        description="審查程式碼品質，檢查潛在問題、程式碼風格、安全性漏洞",
        author="AI",
        tags=["code", "review", "quality"],
        created_at="2025-01-15T00:00:00Z",
        updated_at="2025-01-15T00:00:00Z",
    )
    
    def execute(self, context: dict, **kwargs) -> SkillResult:
        """執行程式碼審查"""
        code = kwargs.get("code", "")
        language = kwargs.get("language", "python")
        
        if not code:
            return SkillResult(success=False, error="No code provided")
        
        # 取得 Tools
        tools: ToolRegistry = context.get("tools")
        
        review_result = {
            "issues": [],
            "suggestions": [],
            "score": 0,
        }
        
        # 1. 檢查程式碼風格
        if language == "python":
            result = tools.execute("shell", {
                "command": f"echo '{code}' | ruff check -",
            })
            if result.data:
                review_result["issues"].extend(self._parse_ruff_output(result.data))
        
        # 2. 檢查安全性
        security_issues = self._check_security(code, language)
        review_result["issues"].extend(security_issues)
        
        # 3. 檢查複雜度
        complexity = self._calculate_complexity(code)
        review_result["suggestions"].append(f"Complexity score: {complexity}")
        
        # 4. 計算分數
        review_result["score"] = self._calculate_score(review_result)
        
        return SkillResult(
            success=True,
            output=review_result,
            metadata={"language": language, "lines": len(code.split("\n"))}
        )
    
    def _describe_parameters(self) -> str:
        return """
- code: 要審查的程式碼 (必填)
- language: 程式語言，預設 python (可選)
"""
    
    def _describe_examples(self) -> str:
        return """
```python
# 執行方式
skill.execute(
    action="execute",
    skill_name="code_review",
    skill_parameters={
        "code": "def hello(): print('world')",
        "language": "python"
    }
)
```
"""
    
    def _check_security(self, code: str, language: str) -> list:
        """檢查安全性問題"""
        issues = []
        dangerous_patterns = ["eval(", "exec(", "__import__", "os.system"]
        for pattern in dangerous_patterns:
            if pattern in code:
                issues.append({
                    "type": "security",
                    "severity": "high",
                    "message": f"Dangerous pattern found: {pattern}"
                })
        return issues
    
    def _calculate_complexity(self, code: str) -> int:
        """計算複雜度"""
        return len(code.split("\n"))  # 簡化版
    
    def _calculate_score(self, result: dict) -> int:
        """計算評分"""
        base_score = 100
        for issue in result["issues"]:
            if issue.get("severity") == "high":
                base_score -= 20
            elif issue.get("severity") == "medium":
                base_score -= 10
            else:
                base_score -= 5
        return max(0, base_score)
    
    def _parse_ruff_output(self, output: str) -> list:
        """解析 ruff 輸出"""
        issues = []
        for line in output.split("\n"):
            if line.strip():
                issues.append({
                    "type": "style",
                    "severity": "low",
                    "message": line
                })
        return issues
```

### 範例 2：Web Search Skill

```python
# skills/web_search.py

from datetime import datetime
from martlet_molt.skills.base import BaseSkill, SkillMetadata, SkillResult


class WebSearchSkill(BaseSkill):
    """網頁搜尋 Skill"""
    
    metadata = SkillMetadata(
        name="web_search",
        version="1.0.0",
        description="搜尋網頁內容，返回相關結果",
        author="AI",
        tags=["web", "search", "information"],
        created_at="2025-01-15T00:00:00Z",
        updated_at="2025-01-15T00:00:00Z",
    )
    
    def execute(self, context: dict, **kwargs) -> SkillResult:
        """執行網頁搜尋"""
        query = kwargs.get("query", "")
        max_results = kwargs.get("max_results", 5)
        
        if not query:
            return SkillResult(success=False, error="No query provided")
        
        # 取得 Tools
        tools = context.get("tools")
        
        # 執行搜尋
        result = tools.execute("web_search", {
            "query": query,
            "max_results": max_results,
        })
        
        if not result.success:
            return SkillResult(success=False, error=result.error)
        
        return SkillResult(
            success=True,
            output=result.data,
            metadata={"query": query, "results_count": len(result.data.get("results", []))}
        )
    
    def _describe_parameters(self) -> str:
        return """
- query: 搜尋關鍵字 (必填)
- max_results: 最大結果數，預設 5 (可選)
"""
    
    def _describe_examples(self) -> str:
        return """
```python
skill.execute(
    action="execute",
    skill_name="web_search",
    skill_parameters={"query": "Python async best practices"}
)
```
"""
```

---

## 🔄 與 A/B 架構整合

### Skill 在 A/B 系統中的位置

```
                    ┌─────────────────────────────────────────┐
                    │            Orchestrator                 │
                    │        (管理 A/B 系統切換)               │
                    └─────────────────────────────────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
        ┌───────────────────────┐           ┌───────────────────────┐
        │      System A         │           │      System B         │
        │  ┌─────────────────┐  │           │  ┌─────────────────┐  │
        │  │   Agent Core    │  │           │  │   Agent Core    │  │
        │  └────────┬────────┘  │           │  └────────┬────────┘  │
        │           │           │           │           │           │
        │  ┌────────┴────────┐  │           │  ┌────────┴────────┐  │
        │  │  Skill Manager  │  │           │  │  Skill Manager  │  │
        │  └────────┬────────┘  │           │  └────────┬────────┘  │
        │           │           │           │           │           │
        │  ┌────────┴────────┐  │           │  ┌────────┴────────┐  │
        │  │ Skills Registry │  │           │  │ Skills Registry │  │
        │  └────────┬────────┘  │           │  └────────┬────────┘  │
        │           │           │           │           │           │
        └───────────┼───────────┘           └───────────┼───────────┘
                    │                                   │
                    └───────────────┬───────────────────┘
                                    ▼
                    ┌───────────────────────────────┐
                    │       Shared Skills Dir       │
                    │         skills/*.py           │
                    │    (A/B 共用同一個 Skills 目錄) │
                    └───────────────────────────────┘
```

### Skill 同步策略

```python
# Skills 目錄在 shared/ 下，A/B 系統共用
# 這樣創建的新 Skill 兩個系統都能使用

shared/
├── config/
├── data/
├── logs/
└── skills/                    # 共用 Skills 目錄
    ├── code_review.py
    ├── web_search.py
    └── custom/
        └── my_skill.py
```

---

## 🚀 實現計畫

### Phase 1：基礎架構 (預計 1-2 天)

- [ ] 實現 `BaseSkill` 基類
- [ ] 實現 `SkillManager` 管理器
- [ ] 實現 `SkillTool` Tool 入口
- [ ] 實現 `SkillRegistry` 註冊表
- [ ] 基本的 Skill 創建和執行功能

### Phase 2：安全與沙箱 (預計 1 天)

- [ ] 實現 `SkillExecutor` 沙箱執行器
- [ ] 代碼安全驗證
- [ ] 執行超時控制
- [ ] 危險操作審核機制

### Phase 3：動態載入 (預計 1 天)

- [ ] 實現 `SkillLoader` 動態載入器
- [ ] 熱重載 Skills (無需重啟服務)
- [ ] Skill 版本管理
- [ ] 依賴關係處理

### Phase 4：內建 Skills (預計 2 天)

- [ ] `code_review` - 程式碼審查
- [ ] `web_search` - 網頁搜尋
- [ ] `documentation` - 文件生成
- [ ] `data_analysis` - 資料分析
- [ ] `git_commit` - Git Commit 生成

### Phase 5：整合與測試 (預計 1 天)

- [ ] 整合到 Agent 核心
- [ ] 整合到 A/B 架構
- [ ] 完整測試
- [ ] 文檔撰寫

---

## 📊 預期效果

### 用戶體驗

```
# 第一次對話
用戶：「幫我審查這段程式碼」
AI：「好的，我來創建一個 code_review skill...」
    [創建 skill，執行]
AI：「審查完成，發現 3 個問題...」

# 之後的對話
用戶：「用 code_review skill 審查這段程式碼」
AI：[直接執行 skill]
AI：「審查完成...」

# 創建新 Skill
用戶：「創建一個翻譯 skill，可以把文字翻譯成不同語言」
AI：[理解需求，創建 skill]
AI：「已創建 translate skill，支援中、英、日文翻譯」
```

### AI 能力擴展

```
初始狀態：AI 只有基礎 Tools (web, shell, file...)

用戶互動後：AI 獲得新 Skills
├── code_review.py      (用戶請求後創建)
├── web_search.py       (用戶請求後創建)
├── translate.py        (用戶請求後創建)
└── my_custom.py        (用戶手動添加)

結果：AI 的能力隨著使用不斷擴展
```

---

## 🔗 相關文檔

- [README.md](../README.md) - 專案說明
- [AI_CONTEXT.md](./AI_CONTEXT.md) - AI 友善說明
- [architecture.md](./architecture.md) - 架構說明 (待建立)

---

## 📝 備註

1. Skills 與 Tools 的區別：
   - **Tools**: 系統內建，開發者預先定義
   - **Skills**: 動態創建，AI 可自行擴展

2. 安全考量：
   - 所有 Skill 代碼都需要驗證
   - 危險操作需要用戶確認
   - 執行時間有限制

3. 效能考量：
   - Skills 會被緩存，不重複載入
   - 支援異步執行
   - 大型 Skill 可拆分為小模組

---

> 最後更新：2025-01-15
> 狀態：計畫中
> 預計實現版本：v0.2.0