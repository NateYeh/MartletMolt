import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from martlet_molt.skills.base import BaseSkill, SkillMetadata, SkillResult


class SkillManager:
    """
    Skill 管理器 V2 (OpenClaw 風格)：
    支援目錄封裝、SKILL.md 說明書優先架構。
    """

    def __init__(self, skills_dir: str | None = None):
        if skills_dir is None:
            current_file = Path(__file__).resolve()
            # 專案根目錄下的 skills/
            self.skills_dir = current_file.parents[4] / "skills"
        else:
            self.skills_dir = Path(skills_dir)

        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self._registry: dict[str, BaseSkill] = {}
        self._raw_metadata: dict[str, dict[str, Any]] = {}  # 儲存 SKILL.md 的 YAML 部分
        self._instructions: dict[str, str] = {}           # 儲存 SKILL.md 的 Markdown 部分

        self.load_all_skills()

    def _parse_skill_md(self, md_path: Path) -> tuple[dict[str, Any], str]:
        """解析 SKILL.md，拆分 YAML Frontmatter 與 Markdown"""
        content = md_path.read_text(encoding="utf-8")
        # 匹配 --- yaml --- body
        pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n(.*)$', re.DOTALL)
        match = pattern.match(content)

        if match:
            yaml_content = match.group(1)
            body_content = match.group(2)
            metadata = yaml.safe_load(yaml_content)
            return metadata, body_content
        else:
            # 如果沒有 frontmatter，嘗試全量讀取或報錯
            return {"name": md_path.parent.name, "description": "No description found."}, content

    def load_all_skills(self):
        """掃描技能目錄"""
        logger.info(f"Scanning V2 skills from {self.skills_dir}")
        self._registry.clear()

        # 遍歷子目錄
        if not self.skills_dir.exists():
            return

        for entry in self.skills_dir.iterdir():
            if entry.is_dir():
                skill_md = entry / "SKILL.md"
                if skill_md.exists():
                    try:
                        self.load_skill_from_dir(entry)
                    except Exception as e:
                        logger.error(f"Failed to load skill from {entry}: {e}")
            elif entry.suffix == ".py" and entry.name != "__init__.py":
                # 相容舊格式 (V1 單檔案)
                try:
                    self.load_skill_v1(entry)
                except Exception as e:
                    logger.error(f"Failed to load V1 skill {entry}: {e}")

    def load_skill_from_dir(self, skill_dir: Path):
        """載入 OpenClaw 風格的技能目錄"""
        skill_md_path = skill_dir / "SKILL.md"
        meta, instructions = self._parse_skill_md(skill_md_path)
        skill_name = meta.get("name", skill_dir.name)

        # 儲存元數據供快速索引
        self._raw_metadata[skill_name] = meta
        self._instructions[skill_name] = instructions

        # 如果有 python 實作 (scripts/main.py 或 scripts/skill_name.py)
        scripts_dir = skill_dir / "scripts"
        py_impl = list(scripts_dir.glob("*.py")) if scripts_dir.exists() else []

        if py_impl:
            # 動態載入第一個找到的 Python 檔案作為實作
            self._load_python_impl(py_impl[0], skill_name, meta)
        else:
            # 純 Markdown 指南型技能 (Prompt-based)
            # 未來可以在這裡包裝一個 GenericSkill
            logger.info(f"Loaded Prompt-based skill: {skill_name}")

    def _load_python_impl(self, file_path: Path, skill_name: str, meta: dict[str, Any]):
        """從 Python 檔案加載實作"""
        module_name = f"martlet_molt.skills.impl.{skill_name}"
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and issubclass(attr, BaseSkill) and attr is not BaseSkill):
                    skill_instance = attr()
                    # 用 SKILL.md 的 meta 覆寫代碼裡的 meta (單一事實來源)
                    skill_instance.metadata = SkillMetadata(**meta)
                    self._registry[skill_name] = skill_instance
                    logger.info(f"Skill '{skill_name}' (Python) loaded.")
                    return

    def load_skill_v1(self, file_path: Path):
        """相容 V1 單檔案 Python 格式"""
        module_name = f"martlet_molt.skills.v1.{file_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseSkill) and attr is not BaseSkill:
                    inst = attr()
                    self._registry[inst.metadata.name] = inst
                    logger.info(f"V1 Skill '{inst.metadata.name}' loaded.")

    def list_skills(self) -> list[dict[str, Any]]:
        # 同時包含實作了的與純說明的技能
        results = []
        # 以 metadata 作為主要來源
        for name, meta in self._raw_metadata.items():
            results.append({
                "name": name,
                "description": meta.get("description"),
                "type": "hybrid" if name in self._registry else "prompt-only"
            })

        # 補上 V1 但沒出現在目錄下的
        for name, inst in self._registry.items():
            if name not in self._raw_metadata:
                results.append({
                    "name": name,
                    "description": inst.metadata.description,
                    "type": "v1-legacy"
                })
        return results

    def execute_skill(self, skill_name: str, context: dict[str, Any], **kwargs) -> SkillResult:
        skill = self._registry.get(skill_name)
        if not skill:
            return SkillResult(success=False, error=f"Skill '{skill_name}' 尚未實作 Python 邏輯或找不到。")

        # ...執行邏輯保持不變...
        return skill.execute(context, **kwargs)

    def get_skill_guide(self, skill_name: str) -> str:
        """獲取技能的完整 Markdown 指南"""
        return self._instructions.get(skill_name, "無相關說明資料。")
