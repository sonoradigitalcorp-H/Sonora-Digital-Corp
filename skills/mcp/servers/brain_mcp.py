"""Unified Brain v2 — MCP Server.

Expone el cerebro unificado como herramientas MCP:
  - brain_query: búsqueda unificada (FTS + semántica + grafos)
  - brain_status: estado de conexiones
  - brain_sync: forzar sincronización
"""

import json
import logging

from apps.brain.config import BrainConfig
from apps.brain.models import BrainQuery
from apps.brain.service import BrainService

log = logging.getLogger("mcp.brain")

# Singleton
_brain: BrainService = None


def _get_brain() -> BrainService:
    global _brain
    if _brain is None:
        try:
            _brain = BrainService()
            log.info("✅ BrainService initialized")
        except Exception as e:
            log.error(f"❌ BrainService init: {e}")
            raise
    return _brain


async def brain_query(query: str, mode: str = "auto", limit: int = 10) -> str:
    """Busca en el cerebro unificado."""
    try:
        brain = _get_brain()
        q = BrainQuery(text=query, mode=mode, limit=limit)
        result = await brain.query(q)
        return json.dumps({
            "query": result.query,
            "mode": result.mode,
            "total": result.total,
            "sources": result.sources_queried,
            "elapsed_ms": result.elapsed_ms,
            "results": [
                {
                    "type": r.type,
                    "label": r.label,
                    "content": r.content[:300],
                    "source": r.source,
                    "score": r.score,
                }
                for r in result.results
            ],
        })
    except Exception as e:
        log.error(f"brain_query error: {e}")
        return json.dumps({"error": str(e)})


async def brain_status() -> str:
    """Estado del cerebro unificado."""
    try:
        brain = _get_brain()
        status = brain.ready()
        return json.dumps(status)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def brain_sync() -> str:
    """Forzar sincronización de todos los ingestores."""
    try:
        brain = _get_brain()
        result = brain.run_sync()
        return json.dumps({
            "status": "completed",
            "last_sync": result.last_sync or "just now",
            "total_nodes": result.total_nodes,
            "ingestors": {
                name: info
                for name, info in result.ingestor_results.items()
            },
            "errors": result.errors,
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


async def brain_context(topic: str, limit: int = 5) -> str:
    """Obtiene contexto relevante del brain para inyectar en LLM."""
    try:
        brain = _get_brain()
        q = BrainQuery(text=topic, mode="auto", limit=limit)
        result = await brain.query(q)
        if not result.results:
            return json.dumps({"context": ""})
        parts = []
        for r in result.results[:limit]:
            parts.append(f"[{r.type}|{r.source}] {r.label}: {r.content[:200]}")
        return json.dumps({"context": "\n".join(parts)})
    except Exception as e:
        log.warning(f"brain_context error: {e}")
        return json.dumps({"context": "", "error": str(e)})


MCP_TOOLS = {
    "brain_query": {
        "description": "Busca en el Unified Brain (Engram + Neo4j + Qdrant) — modo auto/FTS/semantic/graph",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Texto a buscar"},
                "mode": {
                    "type": "string",
                    "enum": ["auto", "fts", "semantic", "graph"],
                    "description": "Modo de búsqueda",
                },
                "limit": {"type": "integer", "description": "Máximo resultados"},
            },
            "required": ["query"],
        },
        "handler": lambda args: brain_query(
            args["query"],
            args.get("mode", "auto"),
            args.get("limit", 10),
        ),
    },
    "brain_status": {
        "description": "Estado del Unified Brain — conexiones a Neo4j, Qdrant, Engram",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
        "handler": lambda args: brain_status(),
    },
    "brain_sync": {
        "description": "Forzar sincronización completa del Unified Brain desde todas las fuentes",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
        "handler": lambda args: brain_sync(),
    },
    "brain_context": {
        "description": "Obtiene contexto relevante del Brain para inyectar en prompts LLM",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Tema a buscar contexto"},
                "limit": {"type": "integer", "description": "Máximo items"},
            },
            "required": ["topic"],
        },
        "handler": lambda args: brain_context(
            args["topic"],
            args.get("limit", 5),
        ),
    },
}
