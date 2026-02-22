"""
Gateway Server - FastAPI 主程式（純 API 服務）
"""

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from martlet_molt.core.config import settings
from martlet_molt.gateway.routes import router

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
    logger.info(f"Starting MartletMolt API Server {settings.system_name}")
    logger.info(f"Gateway: {settings.gateway.url}")
    logger.info("Running in pure API mode (no frontend)")

    yield

    # 關閉
    logger.info(f"Shutting down MartletMolt API Server {settings.system_name}")


def create_app() -> FastAPI:
    """建立 FastAPI 應用（純 API）"""
    app = FastAPI(
        title="MartletMolt API",
        description="A Self-Evolving AI Agent System - Pure API Backend",
        version="0.1.0",
        lifespan=lifespan,
    )

    # 註冊 API 路由
    app.include_router(router)

    return app


def run_server() -> None:
    """運行伺服器"""
    import uvicorn

    uvicorn.run(
        "martlet_molt.main:app",
        host=settings.gateway.host,
        port=settings.gateway.port,
        reload=settings.gateway.reload,
        log_level=settings.log_level.lower(),
    )


# FastAPI 實例
app = create_app()
