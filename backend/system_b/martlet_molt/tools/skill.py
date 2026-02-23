from typing import Any, Literal

from loguru import logger

from martlet_molt.skills.manager import SkillManager
from martlet_molt.tools.base import BaseTool, ToolResult


class SkillTool(BaseTool):
    """
    Skill 管理與執行工具。
    允許 Agent 偵測、學習(建立)、更新與執行持久化的技能模組。
    """

    name = "skill_manager"
    description = "管理 AI 技能。可用於建立(create)、列出(list)、獲取資訊(info)或執行(execute)特定技能。"

    parameters_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create", "list", "execute", "info"],
                "description": "要執行的操作：'create' (建立新技能), 'list' (列出所有技能), 'execute' (執行技能), 'info' (查看詳情)"
            },
            "skill_name": {
                "type": "string",
                "description": "技能名稱 (全小寫蛇形命名，如 'code_reviewer')"
            },
            "skill_code": {
                "type": "string",
                "description": "建立技能時的 Python 程式碼 (僅在 action='create' 時使用)"
            },
            "parameters": {
                "type": "object",
                "description": "執行技能時傳入的參數字典 (僅在 action='execute' 時使用)"
            }
        },
        "required": ["action"]
    }

    def __init__(self, manager: SkillManager | None = None):
        super().__init__()
        self.manager = manager or SkillManager()

    def execute(
        self,
        action: Literal["create", "list", "execute", "info"],
        skill_name: str | None = None,
        skill_code: str | None = None,
        parameters: dict[str, Any] | None = None,
        **kwargs
    ) -> ToolResult:
        try:
            if action == "list":
                skills = self.manager.list_skills()
                return ToolResult(success=True, data={"skills": skills})

            if action == "info":
                if not skill_name:
                    return ToolResult(success=False, error="skill_name is required for 'info' action")
                skill = self.manager.get_skill(skill_name)
                if not skill:
                    return ToolResult(success=False, error=f"Skill '{skill_name}' not found")
                return ToolResult(success=True, data={
                    "name": skill.metadata.name,
                    "description": skill.metadata.description,
                    "prompt_help": skill.to_prompt()
                })

            if action == "create":
                if not skill_name or not skill_code:
                    return ToolResult(success=False, error="skill_name and skill_code are required for 'create' action")
                skill = self.manager.create_skill(skill_name, "", skill_code)
                return ToolResult(success=True, data={
                    "message": f"Skill '{skill_name}' created and loaded.",
                    "name": skill.metadata.name
                })

            if action == "execute":
                if not skill_name:
                    return ToolResult(success=False, error="skill_name is required for 'execute' action")

                # 這裡的 context 可以在之後擴充，目前給予基本的資訊
                context = {
                    "tool_instance": self,
                    "timestamp": str(self.manager.skills_dir)
                }

                result = self.manager.execute_skill(skill_name, context, **(parameters or {}))
                return ToolResult(
                    success=result.success,
                    data=result.output,
                    error=result.error,
                    metadata=result.metadata
                )

            return ToolResult(success=False, error=f"Unsupported action: {action}")

        except Exception as e:
            logger.exception(f"SkillTool error during {action}")
            return ToolResult(success=False, error=str(e))
