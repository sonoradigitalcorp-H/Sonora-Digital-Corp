"""Tests for Sonora SDK Python"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO))

from mcp.sdk.sonora_client import SonoraSDK


@pytest.fixture
def sdk():
    return SonoraSDK(client_id="test", client_secret="test_secret")


@pytest.mark.asyncio
async def test_health_online(sdk):
    with patch.object(sdk._http, "request", new_callable=AsyncMock) as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_response.text = '{"status": "ok"}'
        mock_request.return_value = mock_response

        result = await sdk.health("n8n")
        assert result["status"] == "online"
        assert result["service"] == "n8n"


@pytest.mark.asyncio
async def test_health_offline(sdk):
    with patch.object(sdk._http, "request", new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = Exception("Connection refused")
        result = await sdk.health("n8n")
        assert result["status"] == "offline"
        assert "Connection refused" in result.get("error", "")


@pytest.mark.asyncio
async def test_health_unknown_service(sdk):
    result = await sdk.health("nonexistent")
    assert result["status"] == "offline"


@pytest.mark.asyncio
async def test_health_all(sdk):
    with patch.object(sdk, "health", new_callable=AsyncMock) as mock_health:
        mock_health.return_value = {"status": "online", "service": "test"}
        result = await sdk.health_all()
        assert "timestamp" in result
        assert "services" in result
        assert "summary" in result


@pytest.mark.asyncio
async def test_ensure_token_new(sdk):
    with patch.object(sdk._http, "request", new_callable=AsyncMock) as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "tok_123", "expires_in": 3600}
        mock_response.text = '{"access_token": "tok_123", "expires_in": 3600}'
        mock_request.return_value = mock_response

        token = await sdk._ensure_token()
        assert token == "tok_123"
        assert sdk._token == "tok_123"


@pytest.mark.asyncio
async def test_auth_failure(sdk):
    with patch.object(sdk._http, "request", new_callable=AsyncMock) as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_request.return_value = mock_response

        with pytest.raises(RuntimeError, match="Auth failed"):
            await sdk._ensure_token()


@pytest.mark.asyncio
async def test_tool_call(sdk):
    with patch.object(sdk, "_auth_request", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = {"status": 200, "data": {"result": "ok"}}
        result = await sdk.tool("test_tool", {"param": "value"})
        assert result.get("result") == "ok"


@pytest.mark.asyncio
async def test_capability(sdk):
    with patch.object(sdk, "_auth_request", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = {"status": 200, "data": {"capability": "analytics", "agent": "research-agent"}}
        result = await sdk.capability("analyze dataset")
        assert result["capability"] == "analytics"


@pytest.mark.asyncio
async def test_status(sdk):
    with patch.object(sdk, "_auth_request", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = {
            "status": 200,
            "data": {
                "tenant": "sdc",
                "version": "2.0.0",
                "timestamp": "2026-07-19T00:00:00Z",
                "services": {"n8n": True},
                "summary": {"total": 1, "online": 1, "offline": 0},
            },
        }
        result = await sdk.status()
        assert result["tenant"] == "sdc"
        assert result["version"] == "2.0.0"
