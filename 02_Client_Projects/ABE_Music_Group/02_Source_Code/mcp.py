import json
import logging
from typing import Any

import httpx

from ..config import config

log = logging.getLogger("abe.bridge.mcp")

_gateway_token: str | None = None


async def _ensure_token():
    global _gateway_token
    if _gateway_token or not getattr(config, "mcp_client_secret", None):
        return
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.post(
                f"{config.mcp_gateway_url}/api/auth/token",
                json={
                    "client_id": getattr(config, "mcp_client_id", "abe-service"),
                    "client_secret": config.mcp_client_secret,
                },
            )
            if r.status_code == 200:
                _gateway_token = r.json().get("access_token", "")
    except Exception as e:
        log.debug(f"MCP auth skipped (gateway may not require auth): {e}")


async def call_tool(tool: str, params: dict = None) -> dict[str, Any]:
    await _ensure_token()
    headers = {}
    if _gateway_token:
        headers["Authorization"] = f"Bearer {_gateway_token}"

    # Prefer native /mcp/execute endpoint; fallback to legacy /api/call
    endpoints = [
        ("POST", f"{config.mcp_gateway_url}/mcp/execute", {"tool": tool, "args": params or {}}),
        ("POST", f"{config.mcp_gateway_url}/api/call", {"tool": tool, "params": params or {}}),
    ]

    for method, url, payload in endpoints:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.request(method, url, json=payload, headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    # /mcp/execute returns the raw result (possibly a JSON string)
                    if isinstance(data, str):
                        try:
                            data = json.loads(data)
                        except json.JSONDecodeError:
                            data = {"text": data}
                    return data
                if r.status_code == 404:
                    continue
                log.warning(f"MCP call failed: {r.status_code} {r.text[:200]}")
        except Exception as e:
            log.warning(f"MCP endpoint {url} error: {e}")

    return {"error": "MCP gateway unreachable or tool not found"}


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
