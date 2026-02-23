import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import logging
import docker
import os

# --- 設定日誌 ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

app = FastAPI(title="MartletMolt Orchestrator")
client = docker.from_env()

# --- 狀態管理 (暫時以記憶體存儲，後續可改為文件/DB) ---
# 預設流量導向 system_a
STATE = {
    "active_system": "system_a",
    "systems": {
        "system_a": {"url": "http://system_a:8001", "container_name": "martlet-system-a"},
        "system_b": {"url": "http://system_b:8001", "container_name": "martlet-system-b"}
    }
}

@app.get("/status")
async def get_status():
    """查看當前活躍系統與健康狀態"""
    return STATE

@app.post("/switch/{target}")
async def switch_system(target: str):
    """切換活躍系統 (system_a 或 system_b)"""
    if target not in STATE["systems"]:
        raise HTTPException(status_code=400, detail="Invalid target system")
    
    STATE["active_system"] = target
    logger.info(f"Traffic switched to {target}")
    return {"message": f"Successfully switched to {target}", "active_system": target}

@app.post("/restart/{target}")
async def restart_container(target: str):
    """重啟指定的容器 (由 Agent 觸發)"""
    if target not in ["system_a", "system_b"]:
         raise HTTPException(status_code=400, detail="Can only restart system_a or system_b")
    
    container_name = STATE["systems"][target]["container_name"]
    try:
        container = client.containers.get(container_name)
        container.restart()
        logger.info(f"Container {container_name} restarted by request.")
        return {"message": f"Container {container_name} restarted"}
    except Exception as e:
        logger.error(f"Failed to restart {container_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# --- 萬能代理流量轉發 (Reverse Proxy) ---
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    """將所有不屬於路由的請求轉發給 Active System"""
    target_system = STATE["active_system"]
    target_url = f"{STATE['systems'][target_system]['url']}/{path}"
    
    # 獲取原始請求內容
    body = await request.body()
    headers = dict(request.headers)
    
    # 移除可能會造成干擾的 Host header
    if "host" in headers:
        del headers["host"]

    logger.debug(f"Proxying {request.method} to {target_url}")

    async def stream_request():
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 建立轉發請求
            async with client.stream(
                method=request.method,
                url=target_url,
                params=request.query_params,
                headers=headers,
                content=body
            ) as response:
                # 串流傳回響應 (支援 WebSocket 風格的大量數據)
                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        stream_request(),
        status_code=httpx.codes.OK, # 這裡其實應該動態獲取，暫時簡化
        headers={"X-Martlet-Source": target_system}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
