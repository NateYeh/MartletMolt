"""
Web Lite - FastAPI 前端服務入口
"""

import sys
from contextlib import asynccontextmanager

import httpx
from config import settings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

# 設定 loguru
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期"""
    # 啟動
    logger.info("Starting Web Lite Frontend Server")
    logger.info(f"Frontend: {settings.frontend.url}")
    logger.info(f"Backend API: {settings.backend.url}")

    # 建立 HTTP 客戶端
    app.state.http_client = httpx.AsyncClient(timeout=60.0)

    yield

    # 關閉
    logger.info("Shutting down Web Lite Frontend Server")
    await app.state.http_client.aclose()


def create_app() -> FastAPI:
    """建立 FastAPI 應用"""
    app = FastAPI(
        title="Web Lite - MartletMolt Frontend",
        description="Lightweight Frontend for MartletMolt",
        version="0.1.0",
        lifespan=lifespan,
    )

    # 掛載靜態資源
    if settings.static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

    # 設定模板
    app.state.templates = Jinja2Templates(directory=str(settings.templates_dir))

    # 註冊路由
    from routes import router

    app.include_router(router)

    return app


def run_server() -> None:
    """運行伺服器"""
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.frontend.host,
        port=settings.frontend.port,
        reload=settings.frontend.reload,
        log_level=settings.log_level.lower(),
    )


# FastAPI 實例
app = create_app()


if __name__ == "__main__":
    run_server()
