"""Tests for Hermes MCP Client."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.mark.asyncio
async def test_call_tool_success():
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = MagicMock(status_code=200, json=lambda: {"result": "ok"})
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        result = await client.call_tool("neo4j_query", {"cypher": "RETURN 1"})
        assert result["success"] is True
        assert result["data"]["result"] == "ok"


@pytest.mark.asyncio
async def test_call_tool_hermes_down():
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post.side_effect = __import__("httpx").ConnectError("Connection refused")
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        result = await client.call_tool("neo4j_query", {"cypher": "RETURN 1"})
        assert result["success"] is False
        assert "hermes_unavailable" in result["error"]


@pytest.mark.asyncio
async def test_call_tool_timeout():
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post.side_effect = __import__("httpx").TimeoutException("Timeout")
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        result = await client.call_tool("neo4j_query", {"cypher": "RETURN 1"})
        assert result["success"] is False
        assert "timeout" in result["error"]


@pytest.mark.asyncio
async def test_query_neo4j():
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    
    with patch.object(client, "call_tool", AsyncMock()) as mock_call:
        mock_call.return_value = {"success": True, "data": {"nodes": 33}}
        result = await client.query_neo4j("MATCH (n) RETURN count(n)")
        assert result["success"] is True
        mock_call.assert_called_once_with("neo4j_query", {"cypher": "MATCH (n) RETURN count(n)"})


@pytest.mark.asyncio
async def test_search_qdrant():
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    
    with patch.object(client, "call_tool", AsyncMock()) as mock_call:
        mock_call.return_value = {"success": True, "data": {"points": []}}
        result = await client.search_qdrant("abe-artists", [0.1, 0.2, 0.3])
        assert result["success"] is True
        mock_call.assert_called_once()


@pytest.mark.asyncio
async def test_health_status():
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    
    with patch.object(client, "call_tool", AsyncMock()) as mock_call:
        mock_call.return_value = {"success": True, "data": {"healthy": True}}
        result = await client.health_status()
        assert result["success"] is True


@pytest.mark.asyncio
async def test_list_tools():
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    
    with patch.object(client, "call_tool", AsyncMock()) as mock_call:
        mock_call.return_value = {"success": True, "data": {"tools": ["neo4j_query", "qdrant_search"]}}
        result = await client.list_tools()
        assert result["success"] is True
