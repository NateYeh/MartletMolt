"""
Gateway Server - FastAPI 主程式
"""

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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
    logger.info(f"Starting MartletMolt System {settings.system_name}")
    logger.info(f"Gateway: {settings.gateway.url}")

    yield

    # 關閉
    logger.info(f"Shutting down MartletMolt System {settings.system_name}")


def create_app() -> FastAPI:
    """建立 FastAPI 應用"""
    app = FastAPI(
        title="MartletMolt",
        description="A Self-Evolving AI Agent System",
        version="0.1.0",
        lifespan=lifespan,
    )

    # 註冊路由
    app.include_router(router)

    # 靜態檔案（使用共享目錄）
    static_dir = settings.static_dir
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # 模板（使用共享目錄）
    templates_dir = settings.templates_dir
    if templates_dir.exists():
        app.state.templates = Jinja2Templates(directory=str(templates_dir))

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
