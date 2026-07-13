"""MCP Server Registry — all tools from all services."""

import importlib
import json
import logging
import os
from typing import Any

log = logging.getLogger("mcp.registry")

SERVERS_DIR = os.path.dirname(os.path.abspath(__file__))

# Auto-discover all MCP servers
MCP_SERVERS = {}


def _load_servers():
    for f in sorted(os.listdir(SERVERS_DIR)):
        if f.endswith("_mcp.py") and f != "__init__.py":
            name = f[:-3]
            try:
                mod = importlib.import_module(f"mcp.servers.{name}")
                if hasattr(mod, "MCP_TOOLS"):
                    MCP_SERVERS[name] = mod.MCP_TOOLS
                    log.info(f"Loaded MCP server: {name} ({len(mod.MCP_TOOLS)} tools)")
            except Exception as e:
                log.warning(f"Failed to load MCP server {name}: {e}")


def get_all_tools() -> dict[str, dict[str, Any]]:
    if not MCP_SERVERS:
        _load_servers()
    return MCP_SERVERS


def get_tool(server: str, tool: str):
    servers = get_all_tools()
    return servers.get(server, {}).get(tool)


async def execute_tool(server: str, tool: str, args: dict) -> str:
    """Execute a tool from any MCP server by name."""
    tool_def = get_tool(server, tool)
    if not tool_def:
        return json.dumps({"error": f"Tool {server}/{tool} not found"})
    try:
        result = await tool_def["handler"](args)
        return result
    except Exception as e:
        return json.dumps({"error": str(e)})


async def execute_any(tool_name: str, args: dict) -> str:
    """Execute a tool by name, searching across all servers."""
    servers = get_all_tools()
    for server_name, tools in servers.items():
        if tool_name in tools:
            return await execute_tool(server_name, tool_name, args)
    return json.dumps({"error": f"Tool '{tool_name}' not found in any server"})


# Load on import
_load_servers()
