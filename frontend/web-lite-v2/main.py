"""
Web Lite V2 - FastAPI 前端服務
輕量化版 LobeHub UI 架構
"""

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from loguru import logger

# 配置
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# 後端 API 配置
BACKEND_HOST = "0.0.0.0"
BACKEND_PORT = 8001
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

# FastAPI 應用
app = FastAPI(
    title="MartletMolt Web Lite V2",
    description="輕量化版 LobeHub UI",
    version="0.2.0"
)

# 掛載靜態文件
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Jinja2 模板
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首頁"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "backend_url": BACKEND_URL
        }
    )


@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    """聊天頁面"""
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "backend_url": BACKEND_URL
        }
    )


@app.get("/health")
async def health():
    """健康檢查"""
    return {
        "status": "ok",
        "service": "web-lite-v2",
        "backend_url": BACKEND_URL
    }


def main():
    """啟動服務"""
    logger.info("[Web Lite V2] 啟動前端服務...")
    logger.info(f"[Web Lite V2] 後端 API: {BACKEND_URL}")
    logger.info("[Web Lite V2] 前端地址: http://0.0.0.0:8002")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )


if __name__ == "__main__":
    main()
