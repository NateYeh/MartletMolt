import pytest
from fastapi.testclient import TestClient
from orchestrator.proxy import app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    # 我們需要 Mock state_manager 和 settings 以便測試代理邏輯
    with patch("orchestrator.proxy.state_manager") as mock_state:
        with patch("orchestrator.proxy.settings") as mock_settings:
            mock_state.get_active_system.return_value = "a"
            mock_settings.system_a = MagicMock(url="http://localhost:9999")
            yield TestClient(app)

@pytest.mark.asyncio
async def test_proxy_http_forwarding(client):
    # 模擬 httpx.AsyncClient.request
    with patch("orchestrator.proxy.client.request") as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"status": "ok"}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response
        
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        # 驗證是否轉發到了正確的 URL
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert kwargs["url"] == "http://localhost:9999/health"

@pytest.mark.asyncio
async def test_proxy_error_handling(client):
    with patch("orchestrator.proxy.client.request") as mock_request:
        mock_request.side_effect = Exception("Connection Refused")
        
        response = client.get("/any-path")
        
        assert response.status_code == 502
        assert "Proxy Error" in response.text
