"""
Web Lite - 前端路由
"""

from config import settings
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

router = APIRouter()


# 請求模型
class ChatRequest(BaseModel):
    """聊天請求"""

    message: str
    session_id: str = "default"


def get_templates(request: Request):
    """取得模板實例"""
    return request.app.state.templates


def get_http_client(request: Request):
    """取得 HTTP 客戶端"""
    return request.app.state.http_client


# 頁面路由
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首頁"""
    templates = get_templates(request)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "frontend_url": settings.frontend.url, "backend_url": settings.backend.url},
    )


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """聊天頁面"""
    templates = get_templates(request)
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "frontend_url": settings.frontend.url, "backend_url": settings.backend.url},
    )


# API 代理路由（可選：直接代理到後端）
@router.post("/api/chat")
async def chat_proxy(request: Request, chat_request: ChatRequest):
    """
    代理聊天請求到後端 API

    注意：前端也可以直接呼叫後端 API，此代理為可選功能
    """
    client = get_http_client(request)

    try:
        response = await client.post(
            f"{settings.backend.url}/chat",
            json=chat_request.model_dump(),
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@router.get("/api/status")
async def status_proxy(request: Request):
    """代理狀態請求到後端 API"""
    client = get_http_client(request)

    try:
        response = await client.get(f"{settings.backend.url}/status")
        return response.json()
    except Exception as e:
        return {"error": str(e)}
