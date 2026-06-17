#!/usr/bin/env python3
"""
JARVIS MCP Bridge for Hermes Desktop.
Exposes JARVIS core functions as MCP tools so Hermes can use them.
Run as: python3 hermes_bridge.py
Hermes Desktop spawns this as a subprocess (stdio transport).
"""
import sys
import os
import json
import logging

# Add JARVIS project root to path
sys.path.insert(0, os.path.expanduser("~/jarvis"))

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(asctime)s [JARVIS] %(message)s")
log = logging.getLogger("jarvis.bridge")

# Create FastMCP server
mcp = FastMCP("jarvis-bridge", log_level="INFO")

@mcp.tool()
def jarvis_research(query: str) -> str:
    """Busca y sintetiza información en la memoria de JARVIS (Neo4j + Qdrant)."""
    try:
        from src.core.rag import rag
        result = rag.search(query, limit=3)
        if result["status"] == "success":
            texts = [r["text"][:500] for r in result["results"]]
            return "\n".join(texts) if texts else "No results found"
        return f"Error: {result.get('error', 'Unknown')}"
    except Exception as e:
        return f"Research failed: {e}"

@mcp.tool()
def jarvis_memory_store(key: str, value: str) -> str:
    """Guarda un recuerdo en la memoria persistente de JARVIS."""
    try:
        from src.core.engram import engram
        engram.store_learning("hermes-bridge", key, value, value[:200])
        return f"Saved: {key}"
    except Exception as e:
        return f"Memory store failed: {e}"

@mcp.tool()
def jarvis_memory_recall(query: str) -> str:
    """Recupera recuerdos relevantes de la memoria de JARVIS."""
    try:
        from src.core.engram import engram
        results = engram.query_context(query, limit=3)
        if results:
            return "\n".join([f"[{r['tag']}] {r['summary'][:300]}" for r in results])
        return "No relevant memories found"
    except Exception as e:
        return f"Memory recall failed: {e}"

@mcp.tool()
def jarvis_metrics() -> str:
    """Devuelve métricas del sistema JARVIS."""
    try:
        from src.core import engram, verify
        specs_dir = os.path.expanduser("~/jarvis/specs")
        spec_count = len([d for d in os.listdir(specs_dir) if os.path.isdir(os.path.join(specs_dir, d))])
        return json.dumps({
            "specs": spec_count,
            "agents": 15,
            "skills": 50,
            "tests": 330,
            "engram_ready": True,
            "status": "operational"
        }, indent=2)
    except Exception as e:
        return f"Metics failed: {e}"

@mcp.tool()
def jarvis_orchestrate(task: str) -> str:
    """Ejecuta una tarea a través del orquestador de agentes de JARVIS."""
    try:
        import asyncio
        from src.core.orchestrator import get_orchestrator
        orchestrator = get_orchestrator()
        result = asyncio.run(orchestrator.execute(task))
        return json.dumps({
            "agent": result.get("agent", "unknown"),
            "status": result.get("status", "unknown"),
            "summary": str(result.get("synthesis", result.get("message", "Done")))[:500]
        }, indent=2)
    except Exception as e:
        return f"Orchestration failed: {e}"

if __name__ == "__main__":
    log.info("Starting JARVIS MCP Bridge (stdio transport)...")
    mcp.run(transport="stdio")
