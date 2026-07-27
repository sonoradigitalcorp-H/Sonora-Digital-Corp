"""MCP executor — calls MCP tools for MCP contract type providers."""
from __future__ import annotations

import logging
from typing import Any

import httpx

from planner.exceptions import ProviderExecutionError
from planner.models import ProviderRef

log = logging.getLogger("planner.executors.mcp")

TIMEOUT = 30


async def execute(provider: ProviderRef, input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute an MCP provider by calling its tool endpoint."""
    config = provider.config
    mcp_url = config.get("mcp_url", "")
    tool = config.get("tool", "")
    arguments = config.get("arguments", {})

    if not mcp_url:
        raise ProviderExecutionError(provider.id, provider.id, "No mcp_url configured")
    if not tool:
        raise ProviderExecutionError(provider.id, provider.id, "No tool configured")

    for k, v in input_data.items():
        if k not in arguments:
            arguments[k] = v

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(
                f"{mcp_url}/tools/call",
                json={"name": tool, "arguments": arguments},
            )
            if resp.status_code >= 500:
                raise ProviderExecutionError(
                    provider.id, provider.id,
                    f"MCP HTTP {resp.status_code}: {resp.text[:200]}"
                )
            return resp.json()
    except httpx.TimeoutException:
        raise ProviderExecutionError(provider.id, provider.id, "MCP timeout") from None
    except httpx.HTTPError as e:
        raise ProviderExecutionError(provider.id, provider.id, str(e)) from e
