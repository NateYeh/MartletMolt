"""
WebSocket 處理模組
實現聊天主通道的 WebSocket 路由
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from martlet_molt.channels.web.channel import WebChannel
from martlet_molt.core.agent import Agent
from martlet_molt.core.config import settings
from martlet_molt.core.session import session_manager
from martlet_molt.providers.base import BaseProvider
from martlet_molt.providers.ollama import OllamaProvider
from martlet_molt.providers.openai import OpenAIProvider

router = APIRouter()


def get_provider() -> BaseProvider:
    """取得 Provider 實例 (同步自 routes.py)"""
    provider_name = settings.agent.default_provider
    provider_config = getattr(settings.providers, provider_name, None)

    if not provider_config:
        raise ValueError(f"Provider '{provider_name}' not configured")

    if provider_name == "ollama":
        return OllamaProvider(
            api_key=provider_config.api_key,
            base_url=provider_config.base_url,
            model=provider_config.model,
            max_tokens=provider_config.max_tokens,
            temperature=provider_config.temperature,
        )
    elif provider_name == "openai":
        return OpenAIProvider(
            api_key=provider_config.api_key,
            base_url=provider_config.base_url,
            model=provider_config.model,
            max_tokens=provider_config.max_tokens,
            temperature=provider_config.temperature,
        )
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")


@router.websocket("/ws/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    """聊天 WebSocket 入口"""
    channel = WebChannel(websocket, session_id)

    if not await channel.start():
        return

    try:
        # 取得或建立會話
        session = session_manager.get_or_create(session_id)

        # 建立 Provider 和 Agent
        provider = get_provider()
        agent = Agent(provider=provider, session=session)

        # 如果是新會話且沒有消息，添加預設系統提示詞
        if not session.messages:
            agent.add_system_prompt(
                f"你是一個名為 MartletMolt 的自我進化 AI 助手。你的核心目標是協助用戶開發、調優並保護這個系統。你可以使用工具來讀取檔案、執行 Shell 命令、甚至修改自己的代碼。目前運行的系統版本是：{settings.system_name}。"
            )
            session_manager.save(session)

        # 進入接收循環
        async for message in channel.receive():
            logger.info(f"Received message via WS: {message.content}")

            # 使用 Agent 處理訊息並取得串流回應
            # 這裡我們直接調用 agent.stream 並將結果送回 channel
            try:
                async for chunk in agent.stream(message.content):
                    await channel.send_stream(chunk)

                # 發送完成訊號
                await channel.send_done()

            except Exception as e:
                logger.exception(f"Error during agent processing: {e}")
                await channel.send_error(str(e))

    except WebSocketDisconnect:
        logger.info(f"WebSocket session {session_id} disconnected")
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
    finally:
        await channel.stop()
