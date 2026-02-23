from unittest.mock import AsyncMock

import pytest

from martlet_molt.channels.base import ChannelResponse, ChannelStatus
from martlet_molt.channels.web.channel import WebChannel


@pytest.fixture
def mock_websocket():
    ws = AsyncMock()
    ws.client_state.name = "CONNECTED"
    return ws


@pytest.mark.asyncio
async def test_web_channel_start(mock_websocket):
    channel = WebChannel(mock_websocket, session_id="test_session")
    success = await channel.start()

    assert success is True
    assert channel.status == ChannelStatus.RUNNING
    mock_websocket.accept.assert_awaited_once()


@pytest.mark.asyncio
async def test_web_channel_receive(mock_websocket):
    channel = WebChannel(mock_websocket, session_id="test_session")
    await channel.start()

    # 模擬接收一則訊息後，第二次接收拋出異常來終止循環
    mock_websocket.receive_json.side_effect = [{"content": "Hello AI", "user_id": "user1"}, Exception("Stop Loop")]

    messages = []
    async for msg in channel.receive():
        messages.append(msg)

    assert len(messages) == 1
    assert messages[0].content == "Hello AI"
    assert messages[0].user_id == "user1"
    assert channel.status == ChannelStatus.ERROR


@pytest.mark.asyncio
async def test_web_channel_send(mock_websocket):
    channel = WebChannel(mock_websocket, session_id="test_session")
    response = ChannelResponse(content="AI Reply")

    success = await channel.send(response)

    assert success is True
    mock_websocket.send_json.assert_awaited_once()


@pytest.mark.asyncio
async def test_web_channel_stop(mock_websocket):
    channel = WebChannel(mock_websocket, session_id="test_session")
    await channel.start()

    success = await channel.stop()

    assert success is True
    assert channel.status == ChannelStatus.STOPPED
    mock_websocket.close.assert_awaited_once()
