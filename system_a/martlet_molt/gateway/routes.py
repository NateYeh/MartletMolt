"""
REST API 路由（純 API，不提供前端頁面）
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
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


# ============================================
# 會話管理 API
# ============================================


class SessionInfo(BaseModel):
    """會話基本資訊"""

    id: str
    created_at: str
    updated_at: str
    message_count: int
    tool_call_count: int
    metadata: dict


class SessionListResponse(BaseModel):
    """會話列表回應"""

    sessions: list[SessionInfo]
    total: int


class SessionDetailResponse(BaseModel):
    """會話詳情回應"""

    id: str
    created_at: str
    updated_at: str
    messages: list[dict]
    tool_calls: list[dict]
    metadata: dict


class DeleteSessionResponse(BaseModel):
    """刪除會話回應"""

    success: bool
    message: str


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions():
    """
    列出所有會話

    Returns:
        所有會話的基本資訊列表
    """
    session_ids = session_manager.list_sessions()
    sessions = []

    for session_id in session_ids:
        info = session_manager.get_session_info(session_id)
        if info:
            sessions.append(SessionInfo(**info))

    return SessionListResponse(
        sessions=sessions,
        total=len(sessions),
    )


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str):
    """
    取得會話詳情（包含完整訊息歷史）

    Args:
        session_id: 會話 ID

    Returns:
        會話完整資訊，包含所有訊息歷史

    Raises:
        HTTPException: 會話不存在時返回 404
    """
    session = session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    return SessionDetailResponse(
        id=session.id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[msg.model_dump() for msg in session.messages],
        tool_calls=[tc.model_dump() for tc in session.tool_calls],
        metadata=session.metadata,
    )


@router.delete("/sessions/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(session_id: str):
    """
    刪除會話

    Args:
        session_id: 會話 ID

    Returns:
        刪除結果

    Raises:
        HTTPException: 會話不存在時返回 404
    """
    # 先檢查會話是否存在
    session = session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    # 刪除會話
    success = session_manager.delete(session_id)

    return DeleteSessionResponse(
        success=success,
        message=f"Session '{session_id}' deleted successfully" if success else "Failed to delete session",
    )
