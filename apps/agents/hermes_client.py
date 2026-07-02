#!/usr/bin/env python3
"""Hermes MCP Client — wrapper estandar para que agentes llamen tools via Hermes.

Uso:
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    result = await client.call_tool("neo4j_query", {"cypher": "MATCH (n) RETURN count(n)"})
"""
import json
import logging
from typing import Any

log = logging.getLogger("hermes.client")

HERMES_SSE_URL = "http://127.0.0.1:8000/sse"
HERMES_MCP_URL = "http://127.0.0.1:8000/mcp"
TIMEOUT = 30


class HermesClient:
    """MCP client that calls tools via Hermes Gateway."""

    def __init__(self, base_url: str = HERMES_MCP_URL):
        self.base_url = base_url

    async def call_tool(self, tool_name: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Call any MCP tool via Hermes. If Hermes is down, returns error dict."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                payload = {"tool": tool_name, "params": params or {}}
                resp = await client.post(f"{self.base_url}/call", json=payload)
                if resp.status_code == 200:
                    return {"success": True, "data": resp.json()}
                return {"success": False, "error": f"HTTP {resp.status_code}", "data": resp.text[:200]}
        except httpx.TimeoutException:
            log.warning(f"Hermes timeout calling {tool_name}")
            return {"success": False, "error": "timeout"}
        except httpx.ConnectError:
            log.warning(f"Hermes not available at {self.base_url}")
            return {"success": False, "error": "hermes_unavailable"}
        except Exception as e:
            log.error(f"Hermes call failed: {e}")
            return {"success": False, "error": str(e)}

    async def query_neo4j(self, cypher: str) -> dict[str, Any]:
        """Execute Cypher query via Hermes/Neo4j MCP."""
        return await self.call_tool("neo4j_query", {"cypher": cypher})

    async def search_qdrant(self, collection: str, vector: list[float], limit: int = 5) -> dict[str, Any]:
        """Search Qdrant via Hermes/Qdrant MCP."""
        return await self.call_tool("qdrant_search", {
            "collection": collection, "vector": vector, "limit": limit,
        })

    async def health_status(self) -> dict[str, Any]:
        """Check health of all services via Hermes."""
        return await self.call_tool("health_status", {})

    async def list_tools(self) -> dict[str, Any]:
        """List all available tools via Hermes."""
        return await self.call_tool("gateway_tools", {})

    # Git MCP tools
    async def git_status(self, repo_path: str = ".") -> dict[str, Any]:
        """Check git status via Git MCP."""
        return await self.call_tool("git_status", {"repo_path": repo_path})

    async def git_commit(self, message: str, repo_path: str = ".") -> dict[str, Any]:
        """Commit changes via Git MCP."""
        return await self.call_tool("git_commit", {"repo_path": repo_path, "message": message})

    async def git_log(self, max_count: int = 10, repo_path: str = ".") -> dict[str, Any]:
        """Show git log via Git MCP."""
        return await self.call_tool("git_log", {"repo_path": repo_path, "max_count": max_count})

    # Memory MCP tools
    async def memory_search(self, query: str) -> dict[str, Any]:
        """Search Memory MCP knowledge graph."""
        return await self.call_tool("search_nodes", {"query": query})

    async def memory_create_entities(self, entities: list[dict]) -> dict[str, Any]:
        """Create entities in Memory MCP knowledge graph."""
        return await self.call_tool("create_entities", {"entities": entities})
