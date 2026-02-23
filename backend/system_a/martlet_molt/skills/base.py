from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class SkillMetadata(BaseModel):
    """Skill 元數據"""
    name: str
    version: str = "1.0.0"
    description: str
    author: str = "AI"
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    requires: list[str] = Field(default_factory=list)  # 依賴的其他 Skills
    dangerous: bool = False   # 是否需要用戶確認


class SkillResult(BaseModel):
    """Skill 執行結果"""
    success: bool
    output: Any = None
    error: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class SkillStatus(StrEnum):
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
    def execute(self, context: dict[str, Any], **kwargs) -> SkillResult:
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

    def pre_execute(self, context: dict[str, Any], **kwargs) -> bool:
        """執行前檢查 (可選)"""
        return True

    def post_execute(self, context: dict[str, Any], result: SkillResult) -> None:  # noqa: B027
        """執行後處理 (可選)"""
        # Hook for subclasses

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
