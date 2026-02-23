import subprocess
import tempfile
import os
from typing import Any, Dict
from martlet_molt.skills.base import BaseSkill, SkillMetadata, SkillResult


class PythonReviewerSkill(BaseSkill):
    """Python 代碼規範檢查技能，封裝 Ruff 進行靜態分析"""
    
    metadata = SkillMetadata(
        name="python_reviewer",
        version="1.0.0",
        description="使用 Ruff 檢查 Python 代碼的格式與規範建議",
        tags=["dev", "lint", "quality"]
    )
    
    def execute(self, context: Dict[str, Any], **kwargs) -> SkillResult:
        code = kwargs.get("code")
        if not code:
            return SkillResult(success=False, error="缺少 'code' 參數。")

        # 建立臨時檔案來存放代碼以進行檢查
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            # 執行 ruff check
            result = subprocess.run(
                ["ruff", "check", tmp_path, "--output-format", "json"],
                capture_output=True,
                text=True
            )
            
            # Ruff 如果沒發現問題回傳 0，發現問題回傳 1
            # 我們從 stderr 讀取輸出的 json (或 stdout，視 ruff 版本而定)
            output = result.stdout if result.stdout else result.stderr
            
            return SkillResult(
                success=True,
                output={
                    "raw_output": output,
                    "return_code": result.returncode,
                    "message": "檢查完成，請參考輸出結果。" if result.returncode != 0 else "代碼品質完美！未發現規範問題。"
                },
                metadata={"file_size": len(code)}
            )
        except Exception as e:
            return SkillResult(success=False, error=f"執行 Ruff 失敗: {str(e)}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def _describe_parameters(self) -> str:
        return "- code: 要檢查的 Python 原始碼內容。"

    def _describe_examples(self) -> str:
        return "skill_manager.execute(skill_name='python_reviewer', parameters={'code': 'import os\ndef test(): pass'})"
