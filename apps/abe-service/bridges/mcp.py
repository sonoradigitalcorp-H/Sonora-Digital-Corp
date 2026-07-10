import logging
from typing import Any

import httpx

from ..config import config

log = logging.getLogger("abe.bridge.mcp")

_gateway_token: str | None = None


async def _ensure_token():
    global _gateway_token
    if _gateway_token:
        return
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.post(
                f"{config.mcp_gateway_url}/api/auth/token",
                json={
                    "client_id": config.mcp_client_id,
                    "client_secret": config.mcp_client_secret,
                },
            )
            if r.status_code == 200:
                _gateway_token = r.json().get("access_token", "")
    except Exception as e:
        log.warning(f"MCP auth error: {e}")


async def call_tool(tool: str, params: dict = None) -> dict[str, Any]:
    await _ensure_token()
    if not _gateway_token:
        return {"error": "MCP gateway not authenticated"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                f"{config.mcp_gateway_url}/api/call",
                json={"tool": tool, "params": params or {}},
                headers={"Authorization": f"Bearer {_gateway_token}"},
            )
            if r.status_code == 200:
                return r.json()
            return {"error": f"MCP call failed: {r.status_code}", "detail": r.text}
    except Exception as e:
        log.warning(f"MCP call error: {e}")
        return {"error": str(e)}


async def list_tools() -> list[dict]:
    await _ensure_token()
    if not _gateway_token:
        return []
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(
                f"{config.mcp_gateway_url}/api/tools",
                headers={"Authorization": f"Bearer {_gateway_token}"},
            )
            if r.status_code == 200:
                return r.json().get("tools", [])
    except Exception:
        pass
    return []


async def health() -> dict:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{config.mcp_gateway_url}/api/health")
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return {"status": "unavailable"}
