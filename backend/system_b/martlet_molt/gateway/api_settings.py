"""
系統設定與工具管理 API
"""

from fastapi import APIRouter
from pydantic import BaseModel

from martlet_molt.core.config import settings
from martlet_molt.tools.base import ToolRegistry

router = APIRouter(prefix="/settings", tags=["settings"])


class AgentSettingsUpdate(BaseModel):
    """Agent 設定更新請求"""

    provider: str | None = None
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None


class ToolConfigUpdate(BaseModel):
    """工具配置更新請求"""

    name: str
    enabled: bool


@router.get("/")
async def get_settings():
    """
    取得目前的系統與 Agent 設定
    """
    # 取得當前 Provider 的詳細配置
    current_provider = settings.agent.default_provider
    provider_config = getattr(settings.providers, current_provider, None)

    return {
        "agent": {
            "provider": current_provider,
            "model": provider_config.model if provider_config else "unknown",
            "temperature": provider_config.temperature if provider_config else settings.agent.temperature,
            "max_tokens": provider_config.max_tokens if provider_config else settings.agent.max_tokens,
        },
        "tools": {
            "web_enabled": settings.tools.web_enabled,
            "shell_enabled": settings.tools.shell_enabled,
            "file_enabled": settings.tools.file_enabled,
        },
        "system": {
            "name": settings.system_name,
            "debug": settings.debug,
        }
    }


@router.patch("/agent")
async def update_agent_settings(request: AgentSettingsUpdate):
    """
    更新 Agent 設定 (動態生效，但目前不持久化到 YAML)
    """
    if request.provider:
        settings.agent.default_provider = request.provider

    # 取得對應的 provider config
    provider_name = request.provider or settings.agent.default_provider
    provider_config = getattr(settings.providers, provider_name, None)

    if provider_config:
        if request.model:
            provider_config.model = request.model
        if request.temperature is not None:
            provider_config.temperature = request.temperature
        if request.max_tokens:
            provider_config.max_tokens = request.max_tokens

    return {"status": "success", "message": "Agent settings updated"}


@router.get("/tools")
async def list_tools():
    """
    列出所有可用工具及其狀態
    """
    registry = ToolRegistry()
    tools = []

    for name, tool in registry.tools.items():
        tools.append({
            "name": name,
            "description": tool.description,
            "enabled": True  # 暫時硬編碼，未來可擴充為動態開關
        })

    return {"tools": tools}
