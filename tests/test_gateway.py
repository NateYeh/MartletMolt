from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from martlet_molt.gateway.server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    """測試健康檢查"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "system" in data


def test_status_endpoint(client):
    """測試系統狀態"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert isinstance(data["tools"], list)


@patch("martlet_molt.gateway.routes.get_provider")
@patch("martlet_molt.gateway.routes.Agent")
def test_chat_endpoint(mock_agent_class, mock_get_provider, client):
    """測試聊天端點"""
    # 設定 Mock Agent
    mock_agent = MagicMock()
    # 因為 chat 是 async 函式，需要用 AsyncMock
    # 但在 Python 中 MagicMock 的 return_value 設定為協程也可以，或者直接 mock_agent.chat = AsyncMock(...)
    # 這裡簡單處理：
    async def fake_chat(msg): return "AI Response"
    mock_agent.chat = fake_chat
    mock_agent_class.return_value = mock_agent
    
    response = client.post(
        "/chat",
        json={"message": "Hello", "session_id": "test_api_session"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "AI Response"
    assert data["session_id"] == "test_api_session"


def test_sessions_list(client):
    """測試會話列表"""
    # 確保至少有一個會話
    client.post("/chat", json={"message": "ping", "session_id": "s1"})
    
    response = client.get("/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert data["total"] >= 1


def test_session_detail_and_delete(client):
    """測試會話詳情與刪除"""
    sid = "test_to_del"
    client.post("/chat", json={"message": "init", "session_id": sid})
    
    # 詳情
    resp = client.get(f"/sessions/{sid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == sid
    
    # 刪除
    resp = client.delete(f"/sessions/{sid}")
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    
    # 再次獲取應為 404
    resp = client.get(f"/sessions/{sid}")
    assert resp.status_code == 404
