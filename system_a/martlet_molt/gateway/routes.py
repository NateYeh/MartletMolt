"""
REST API 路由
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from martlet_molt.core.agent import Agent
from martlet_molt.core.config import settings
from martlet_molt.core.session import session_manager
from martlet_molt.providers.base import BaseProvider
from martlet_molt.providers.ollama import OllamaProvider
from martlet_molt.providers.openai import OpenAIProvider
from martlet_molt.tools.base import ToolRegistry

router = APIRouter()


# 請求模型
class ChatRequest(BaseModel):
    """聊天請求"""

    message: str
    session_id: str = "default"
    stream: bool = False


class ChatResponse(BaseModel):
    """聊天回應"""

    message: str
    session_id: str


class HealthResponse(BaseModel):
    """健康檢查回應"""

    status: str
    system: str
    version: str


class StatusResponse(BaseModel):
    """狀態回應"""

    system: str
    active: bool
    tools: list[str]
    provider: str
    model: str


# 模板
def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates


def get_provider() -> BaseProvider:
    """
    根據配置取得 Provider 實例

    Returns:
        Provider 實例
    """
    provider_name = settings.agent.default_provider
    provider_config = getattr(settings.providers, provider_name, None)

    if not provider_config:
        raise ValueError(f"Provider '{provider_name}' not configured")

    if provider_name == "ollama":
        return OllamaProvider(
            api_key=provider_config.api_key,
            base_url=provider_config.base_url or "https://ollama.com",
            model=provider_config.model,
            max_tokens=provider_config.max_tokens,
            temperature=provider_config.temperature,
        )

    elif provider_name == "openai":
        return OpenAIProvider(
            api_key=provider_config.api_key,
            model=provider_config.model,
            max_tokens=provider_config.max_tokens,
            temperature=provider_config.temperature,
        )

    else:
        raise ValueError(f"Unsupported provider: {provider_name}")


# API 路由
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康檢查端點"""
    return HealthResponse(
        status="running",
        system=settings.system_name,
        version="0.1.0",
    )


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """取得系統狀態"""
    provider_config = getattr(settings.providers, settings.agent.default_provider, None)
    return StatusResponse(
        system=settings.system_name,
        active=True,
        tools=ToolRegistry().list_tools(),
        provider=settings.agent.default_provider,
        model=provider_config.model if provider_config else "unknown",
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天端點（同步）"""
    # 取得或建立會話
    session = session_manager.get_or_create(request.session_id)

    # 建立 Agent
    provider = get_provider()
    agent = Agent(provider=provider, session=session)

    try:
        # 調用 AI
        response = await agent.chat(request.message)

        return ChatResponse(
            message=response,
            session_id=session.id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """聊天端點（串流）"""
    # 取得或建立會話
    session = session_manager.get_or_create(request.session_id)

    # 建立 Agent
    provider = get_provider()
    agent = Agent(provider=provider, session=session)

    async def generate():
        try:
            async for chunk in agent.stream(request.message):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


# Web UI 路由
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首頁"""
    templates = get_templates(request)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "system": settings.system_name},
    )


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """聊天頁面"""
    templates = get_templates(request)
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "system": settings.system_name},
    )
