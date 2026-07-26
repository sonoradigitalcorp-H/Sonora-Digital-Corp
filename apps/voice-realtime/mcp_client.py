"""
MCP Client — Conexión al ecosistema MCP de Sonora Digital Corp.
Permite que Mystic Voice use: Engram, Neo4j, Qdrant, OpenClaw, n8n, ADK, Shield.

Gateway: http://127.0.0.1:18989
"""
import asyncio
import json
import logging
import os
from typing import Any, Optional

import httpx

logger = logging.getLogger("mcp-client")

MCP_GATEWAY = os.environ.get("MCP_GATEWAY_URL", "http://127.0.0.1:18989")


class MCPError(Exception):
    """Error en comunicación con MCP Gateway."""
    pass


class MCPClient:
    """
    Cliente MCP unificado.
    Conecta con el MCP Gateway y expone tools como métodos.
    """

    def __init__(self, gateway_url: str = MCP_GATEWAY):
        self.gateway = gateway_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=30.0)
        self._tools_cache = None
        logger.info(f"MCP Client -> {self.gateway}")

    async def close(self):
        await self._client.aclose()

    # ─── Tools Discovery ───

    async def list_tools(self, force: bool = False) -> list[dict]:
        """Lista todas las tools disponibles en el gateway."""
        if self._tools_cache and not force:
            return self._tools_cache
        try:
            r = await self._client.get(f"{self.gateway}/mcp/tools")
            r.raise_for_status()
            data = r.json()
            self._tools_cache = data.get("tools", [])
            return self._tools_cache
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []

    async def get_servers(self) -> list[str]:
        """Lista los servidores MCP disponibles."""
        try:
            r = await self._client.get(f"{self.gateway}/mcp/health")
            r.raise_for_status()
            data = r.json()
            return data.get("servers", [])
        except Exception as e:
            logger.error(f"Failed to get servers: {e}")
            return []

    # ─── Tool Execution ───

    async def execute(self, tool: str, args: dict = None, server: str = None) -> Any:
        """
        Ejecuta una tool MCP.
        - tool: nombre de la tool (ej: "engram_save")
        - args: argumentos de la tool
        - server: servidor específico (opcional)
        """
        payload = {"tool": tool, "args": args or {}}
        if server:
            payload["server"] = server

        try:
            r = await self._client.post(f"{self.gateway}/mcp/execute", json=payload)
            r.raise_for_status()
            result = r.json()
            return result.get("result")
        except httpx.HTTPStatusError as e:
            logger.warning(f"MCP execute {tool}: HTTP {e.response.status_code}")
            if e.response.status_code == 404:
                # Intentar con ruta completa
                if server:
                    r2 = await self._client.post(
                        f"{self.gateway}/mcp/execute/{server}/{tool}",
                        json=args or {},
                    )
                    if r2.status_code == 200:
                        return r2.json().get("result")
            return None
        except Exception as e:
            logger.error(f"MCP execute {tool}: {e}")
            return None

    # ─── Engram Tools ───

    async def engram_save(self, tenant_id: str, key: str, value: str,
                          user_id: str = "mystic", layer: int = 2,
                          importance: int = 1, tags: str = "") -> Optional[dict]:
        """Guarda en memoria Engram."""
        return await self.execute("engram_save", {
            "tenant_id": tenant_id,
            "key": key,
            "value": value,
            "user_id": user_id,
            "layer": layer,
            "importance": importance,
            "tags": tags,
        })

    async def engram_get(self, tenant_id: str, key: str, user_id: str = "mystic") -> Optional[dict]:
        """Obtiene un valor de Engram."""
        return await self.execute("engram_get", {
            "tenant_id": tenant_id,
            "key": key,
            "user_id": user_id,
        })

    async def engram_search(self, tenant_id: str, query: str,
                            user_id: str = "mystic", layer: int = None,
                            limit: int = 10) -> list:
        """Busca en Engram con FTS5."""
        args = {
            "tenant_id": tenant_id,
            "query": query,
            "user_id": user_id,
            "limit": limit,
        }
        if layer is not None:
            args["layer"] = layer
        return await self.execute("engram_search", args)

    async def engram_context(self, tenant_id: str, user_query: str) -> str:
        """
        Obtiene contexto relevante de Engram para una consulta.
        Útil para dar memoria a Mystic en conversaciones.
        """
        results = await self.engram_search(tenant_id, user_query, limit=5)
        if not results:
            return ""
        context_parts = []
        for r in results:
            if isinstance(r, dict):
                key = r.get("key", "")
                value = r.get("value", "")
                context_parts.append(f"  • {key}: {value[:200]}")
        return "\n".join(context_parts)

    # ─── Neo4j Tools ───

    async def neo4j_query(self, cypher: str, params: dict = None) -> list:
        """Ejecuta Cypher contra Neo4j vía MCP."""
        return await self.execute("neo4j_query", {
            "cypher": cypher,
            "params": json.dumps(params or {}),
        })

    async def neo4j_find(self, label: str, property_name: str,
                         property_value: str) -> Optional[dict]:
        """Busca un nodo en Neo4j."""
        results = await self.neo4j_query(
            f"MATCH (n:{label} {{{property_name}: $val}}) RETURN n LIMIT 1",
            {"val": property_value},
        )
        if results and len(results) > 0:
            return results[0]
        return None

    # ─── Qdrant Tools ───

    async def qdrant_search(self, collection: str, vector: list[float],
                            limit: int = 5) -> list:
        """Busca vectores en Qdrant vía MCP."""
        return await self.execute("qdrant_search", {
            "collection": collection,
            "vector": vector,
            "limit": limit,
        })

    # ─── OpenClaw Tools ───

    async def openclaw_skill(self, skill: str, args: dict = None) -> Any:
        """Ejecuta un skill de OpenClaw vía MCP."""
        return await self.execute("openclaw_run", {
            "skill": skill,
            "args": json.dumps(args or {}),
        })

    # ─── n8n Webhook ───

    async def n8n_trigger(self, webhook: str, payload: dict = None) -> Optional[dict]:
        """Dispara un webhook de n8n vía MCP."""
        return await self.execute("n8n_trigger", {
            "webhook": webhook,
            "payload": json.dumps(payload or {}),
        })

    # ─── Unified Brain Tools ───

    async def brain_query(self, query: str, mode: str = "auto", limit: int = 5) -> dict:
        """Busca en el Unified Brain (Engram + Neo4j + Qdrant)."""
        return await self.execute("brain_query", {
            "query": query,
            "mode": mode,
            "limit": limit,
        })

    async def brain_context(self, topic: str, limit: int = 3) -> str:
        """Obtiene contexto relevante del Brain para inyectar en prompts."""
        result = await self.execute("brain_context", {
            "topic": topic,
            "limit": limit,
        })
        if isinstance(result, dict):
            return result.get("context", "")
        return ""

    async def brain_status(self) -> dict:
        """Estado del Unified Brain."""
        return await self.execute("brain_status", {})

    # ─── Unified LLM ───

    async def llm_chat(self, messages: list, **kwargs) -> Optional[dict]:
        """Chat con LLM unificado via MCP (opencode-go deepseek-v4-flash)."""
        args = {
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "temperature": kwargs.get("temperature", 0.7),
            **({"brain_context": kwargs["brain_context"]} if "brain_context" in kwargs else {}),
            **({"provider": kwargs["provider"]} if "provider" in kwargs else {}),
        }
        return await self.execute("llm_chat", args)

    # ─── Health ───

    async def health(self) -> dict:
        """Health check del gateway."""
        try:
            r = await self._client.get(f"{self.gateway}/mcp/health")
            if r.status_code == 200:
                return r.json()
            return {"status": "error", "code": r.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ─── Singleton ───
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Obtiene el singleton del cliente MCP."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client
