"""MCP Native Gateway — exposes all services as MCP tools via FastAPI.

Each MCP server module in mcp/servers/ auto-registers its tools.
Used by: OpenCode agents, LangGraph, n8n, and any MCP client.
"""

import json
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from mcp.servers import execute_any, execute_tool, get_all_tools

log = logging.getLogger("mcp.gateway")

app = FastAPI(title="Sonora OS MCP Gateway", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ToolRequest(BaseModel):
    tool: str
    args: dict = {}
    server: str | None = None


@app.get("/mcp/tools")
async def list_tools():
    """List all available MCP tools across all servers."""
    servers = get_all_tools()
    result = []
    for server_name, tools in servers.items():
        for tool_name, tool_def in tools.items():
            result.append({
                "server": server_name,
                "name": tool_name,
                "description": tool_def["description"],
                "input_schema": tool_def["input_schema"],
            })
    return {"tools": result, "count": len(result)}


@app.post("/mcp/execute")
async def run_tool(req: ToolRequest):
    """Execute a tool by name (auto-discovered across servers)."""
    if req.server:
        result = await execute_tool(req.server, req.tool, req.args)
    else:
        result = await execute_any(req.tool, req.args)
    return {"result": json.loads(result) if isinstance(result, str) else result}


@app.post("/mcp/execute/{server}/{tool}")
async def run_tool_full(server: str, tool: str, args: dict = {}):
    result = await execute_tool(server, tool, args)
    return {"result": json.loads(result) if isinstance(result, str) else result}


@app.get("/mcp/health")
async def health():
    return {"status": "ok", "servers": list(get_all_tools().keys())}

@app.post("/webhooks/mercadopago")
async def mercadopago_webhook(request: Request):
    import json as json_mod
    body = await request.body()
    body_str = body.decode()
    try:
        data = json_mod.loads(body_str)
    except Exception:
        return {"received": True}
    topic = data.get("topic") or data.get("type", "")
    rid = data.get("data", {}).get("id") or data.get("id", "")
    x_sig = request.headers.get("x-signature", "")
    from mcp.servers.mercadopago_mcp import mp_handle_webhook
    result = await mp_handle_webhook(topic, str(rid), body_str, x_sig)
    return {"received": True, "result": json_mod.loads(result)}
import json as _json_module

@app.get("/webhooks/mercadopago")
async def mercadopago_webhook_verify():
    return {"status": "ok", "endpoint": "webhook", "ready": True}

@app.post("/webhooks/mercadopago")
async def mercadopago_webhook(request: Request):
    body = await request.body()
    body_str = body.decode()
    try:
        data = _json_module.loads(body_str)
    except Exception:
        return {"received": True}
    topic = data.get("topic") or data.get("type", "")
    rid = data.get("data", {}).get("id") or data.get("id", "")
    x_sig = request.headers.get("x-signature", "")
    from mcp.servers.mercadopago_mcp import mp_handle_webhook
    result = await mp_handle_webhook(topic, str(rid) if rid else "0", body_str, x_sig)
    return {"received": True, "result": _json_module.loads(result)}
