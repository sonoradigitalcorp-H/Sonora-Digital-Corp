#!/usr/bin/env python3
"""
JARVIS MCP Bridge for Hermes Desktop v3.0.
Ahora proxy al MCP Gateway del VPS (18989) en vez de JARVIS local.
Hermes Desktop puede usar las 138 tools del gateway vía este bridge.
"""
import json
import logging
import os
import sys

# Usar httpx para llamar al MCP Gateway del VPS
import httpx

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(asctime)s [JARVIS] %(message)s")
log = logging.getLogger("jarvis.bridge")

# MCP Gateway del VPS
GATEWAY_URL = os.environ.get("MCP_GATEWAY_URL", "https://sonoradigitalcorp.com")
CLIENT_ID = os.environ.get("SONORA_CLIENT_ID", "sdc-core")
CLIENT_SECRET = os.environ.get("SONORA_CLIENT_SECRET", "sdc_secret_ent3rpr1s3_k3y_2026")

# Cache de token
_token = None

def _get_token():
    global _token
    try:
        r = httpx.post(f"{GATEWAY_URL}/api/auth/token", json={
            "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        }, timeout=5)
        if r.status_code == 200:
            _token = r.json().get("access_token", "")
    except Exception as e:
        log.warning(f"Auth failed: {e}")
    return _token

def _call(tool, params=None):
    token = _get_token()
    if not token:
        return {"error": "MCP Gateway auth failed"}
    try:
        r = httpx.post(f"{GATEWAY_URL}/api/call", json={
            "tool": tool, "params": params or {},
        }, headers={"Authorization": f"Bearer {token}"}, timeout=30)
        return r.json() if r.status_code == 200 else {"error": r.text}
    except Exception as e:
        return {"error": str(e)}

mcp = FastMCP("jarvis-bridge", log_level="INFO")

@mcp.tool()
def gateway_tools() -> str:
    """Lista todas las tools disponibles en el MCP Gateway del VPS (138 tools)."""
    token = _get_token()
    if not token:
        return json.dumps({"error": "No auth"})
    try:
        r = httpx.get(f"{GATEWAY_URL}/api/tools", headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            tools = data.get("tools", [])
            summary = {}
            for t in tools:
                prefix = t["name"].split("_")[0]
                summary[prefix] = summary.get(prefix, 0) + 1
            return json.dumps({
                "total": len(tools),
                "by_category": summary,
                "tools": [t["name"] for t in tools],
            }, indent=2)
        return json.dumps({"error": r.text})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def gateway_call(tool: str, params: str = "{}") -> str:
    """Ejecuta cualquier tool del MCP Gateway del VPS (138 disponibles).
    Args:
        tool: Nombre de la tool (ej: enterprise_score, skills_list, audit_run)
        params: Parámetros en JSON string
    """
    try:
        p = json.loads(params) if isinstance(params, str) else params
    except json.JSONDecodeError:
        p = {}
    result = _call(tool, p)
    return json.dumps(result, indent=2)

@mcp.tool()
def jarvis_research(query: str) -> str:
    """Busca y sintetiza información vía MCP Gateway."""
    result = _call("capability_resolve", {"task": query})
    return json.dumps(result, indent=2)

@mcp.tool()
def jarvis_metrics() -> str:
    """Métricas del sistema vía MCP Gateway."""
    result = _call("enterprise_score", {})
    finops = _call("finops_summary", {})
    return json.dumps({"enterprise_score": result, "finops": finops}, indent=2)

@mcp.tool()
def enterprise_score() -> str:
    """Enterprise Score desde el MCP Gateway del VPS."""
    result = _call("enterprise_score", {})
    return json.dumps(result, indent=2)

@mcp.tool()
def finops_summary() -> str:
    """Resumen FinOps desde el MCP Gateway del VPS."""
    result = _call("finops_summary", {})
    return json.dumps(result, indent=2)

@mcp.tool()
def health_status() -> str:
    """Estado de todos los servicios via MCP Gateway."""
    result = _call("health_all", {})
    return json.dumps(result, indent=2)

@mcp.tool()
def gateway_status() -> str:
    """Estado completo del MCP Gateway."""
    result = _call("health_all", {})
    caps = _call("capability_list", {})
    return json.dumps({
        "gateway": GATEWAY_URL,
        "health": result,
        "capabilities": caps.get("capabilities", []) if isinstance(caps, dict) else [],
    }, indent=2)

if __name__ == "__main__":
    log.info(f"JARVIS MCP Bridge v3.0 — Conectado a MCP Gateway: {GATEWAY_URL}")
    log.info(f"Tools disponibles: 138+")
    mcp.run(transport="stdio")
