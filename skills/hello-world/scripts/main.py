from typing import Any, Dict
from martlet_molt.skills.base import BaseSkill, SkillMetadata, SkillResult


class HelloWorldSkill(BaseSkill):
    """這是一個測試用的 Hello World 技能"""
    
    metadata = SkillMetadata(
        name="hello_world",
        version="1.0.0",
        description="向指定對象打招呼的基礎技能",
        tags=["test", "tutorial"]
    )
    
    def execute(self, context: Dict[str, Any], **kwargs) -> SkillResult:
        name = kwargs.get("name", "Stranger")
        message = f"Hello, {name}! This is a skill running from MartletMolt."
        return SkillResult(
            success=True,
            output={"message": message},
            metadata={"processed_name": name}
        )

    def _describe_parameters(self) -> str:
        return "- name: 要打招呼的對象名稱 (預設: Stranger)"

    def _describe_examples(self) -> str:
        return "skill_manager.execute(skill_name='hello_world', parameters={'name': 'Ray'})"
