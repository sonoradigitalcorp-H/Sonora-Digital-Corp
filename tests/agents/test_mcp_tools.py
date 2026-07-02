"""Tests for Git MCP and Memory MCP tools via HermesClient."""
import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_git_status():
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    with patch.object(client, "call_tool", AsyncMock()) as mock_call:
        mock_call.return_value = {"success": True, "data": {"status": "clean"}}
        r = await client.git_status()
        assert r["success"] is True
        mock_call.assert_called_once_with("git_status", {"repo_path": "."})


@pytest.mark.asyncio
async def test_git_commit():
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    with patch.object(client, "call_tool", AsyncMock()) as mock_call:
        mock_call.return_value = {"success": True, "data": {"commit": "abc123"}}
        r = await client.git_commit("test commit")
        assert r["success"] is True
        mock_call.assert_called_once_with("git_commit", {"repo_path": ".", "message": "test commit"})


@pytest.mark.asyncio
async def test_git_log():
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    with patch.object(client, "call_tool", AsyncMock()) as mock_call:
        mock_call.return_value = {"success": True, "data": {"commits": []}}
        r = await client.git_log(max_count=5)
        assert r["success"] is True
        mock_call.assert_called_once_with("git_log", {"repo_path": ".", "max_count": 5})


@pytest.mark.asyncio
async def test_memory_search():
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    with patch.object(client, "call_tool", AsyncMock()) as mock_call:
        mock_call.return_value = {"success": True, "data": {"entities": []}}
        r = await client.memory_search("Neo4j")
        assert r["success"] is True
        mock_call.assert_called_once_with("search_nodes", {"query": "Neo4j"})


@pytest.mark.asyncio
async def test_memory_create_entities():
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    with patch.object(client, "call_tool", AsyncMock()) as mock_call:
        entities = [{"name": "Neo4j", "entityType": "service", "observations": ["Graph DB"]}]
        mock_call.return_value = {"success": True, "data": {"created": 1}}
        r = await client.memory_create_entities(entities)
        assert r["success"] is True
