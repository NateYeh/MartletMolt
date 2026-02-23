"""
Orchestrator 流量代理模組
負責將流量轉發至當前活躍的 A/B 系統。
"""

import asyncio

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from loguru import logger
from starlette.requests import Request
from starlette.responses import Response

from orchestrator.config import settings
from orchestrator.state import state_manager

app = FastAPI(title="MartletMolt Proxy")

# 用於 HTTP 轉發的非同步客戶端
client = httpx.AsyncClient()


def get_target_url() -> str:
    """獲取當前活躍系統的基礎 URL"""
    active = state_manager.get_active_system()
    config = getattr(settings, f"system_{active}")
    return config.url


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_http(request: Request, path: str) -> Response:
    """通用的 HTTP 反向代理"""
    target_url = f"{get_target_url()}/{path}"
    query_params = request.query_params

    # 獲取請求內容
    content = await request.body()
    headers = dict(request.headers)

    # 移除可能導致衝突的 Header
    headers.pop("host", None)
    headers.pop("content-length", None)

    try:
        # 發送請求到活躍系統
        response = await client.request(
            method=request.method,
            url=target_url,
            params=query_params,
            content=content,
            headers=headers,
            timeout=60.0,
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )
    except Exception as e:
        logger.error(f"Proxy HTTP request failed: {e}")
        return Response(content=f"Proxy Error: {e}", status_code=502)


@app.websocket("/{path:path}")
async def proxy_websocket(websocket: WebSocket, path: str):
    """通用的 WebSocket 反向代理"""
    target_base = get_target_url().replace("http://", "ws://").replace("https://", "wss://")
    # 確保路徑處理正確，避免雙斜槓，並保留 query string
    query_string = websocket.query_params
    full_path = path
    if query_string:
        full_path = f"{path}?{query_string}"

    target_url = f"{target_base.rstrip('/')}/{full_path.lstrip('/')}"

    logger.info(f"Proxying WS connection: {websocket.url.path} -> {target_url}")
    logger.debug(f"WS Headers: {dict(websocket.headers)}")

    await websocket.accept()

    try:
        import websockets

        async with websockets.connect(target_url) as backend_ws:
            # 建立雙向轉發任務
            async def forward_to_backend():
                try:
                    while True:
                        data = await websocket.receive_text()
                        await backend_ws.send(data)
                except Exception:
                    pass

            async def forward_to_client():
                try:
                    while True:
                        data = await backend_ws.recv()
                        await websocket.send_text(str(data))
                except Exception:
                    pass

            # 同時運行兩個轉發方向
            await asyncio.gather(
                forward_to_backend(),
                forward_to_client(),
            )
    except WebSocketDisconnect:
        logger.info("Proxy WS client disconnected")
    except Exception as e:
        logger.error(f"Proxy WS error: {e}")
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
