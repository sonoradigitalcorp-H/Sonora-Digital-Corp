"""WebSocket Bridge — Redis pub/sub → WebSocket.

Subscribes to Redis channels and forwards events to connected WebSocket clients.
Also proxies MCP Gateway calls from the dashboard.
"""

import asyncio
import json
import os

import asyncpg
import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SDC Control Center Bridge", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "IJsa2asL9CYlZDN6HUYl")
MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8180")
HASURA_URL = os.getenv("HASURA_URL", "http://127.0.0.1:8082/v1/graphql")
HASURA_SECRET = os.getenv("HASURA_ADMIN_SECRET", "sonora-admin")

CHANNELS = [
    "agent:content:done", "agent:content:failed",
    "agent:sales:new-order", "agent:support:ticket",
    "system:pipeline:start", "system:pipeline:end",
    "system:alert", "system:service:health",
]

connections: set[WebSocket] = set()


@app.on_event("startup")
async def startup():
    asyncio.create_task(redis_listener())


async def redis_listener():
    while True:
        try:
            r = await aioredis.from_url(
                f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}",
                decode_responses=True,
            )
            pubsub = r.pubsub()
            await pubsub.subscribe(*CHANNELS)
            async for msg in pubsub.listen():
                if msg["type"] == "message":
                    dead = set()
                    for ws in connections:
                        try:
                            await ws.send_text(json.dumps({
                                "channel": msg["channel"],
                                "data": json.loads(msg["data"]),
                            }))
                        except Exception:
                            dead.add(ws)
                    connections -= dead
        except Exception as e:
            print(f"[ws-bridge] Redis error: {e}")
            await asyncio.sleep(5)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connections.add(ws)
    try:
        while True:
            msg = await ws.receive_text()
            try:
                cmd = json.loads(msg)
                if cmd.get("type") == "mcp":
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(
                            f"{MCP_URL}/mcp/execute",
                            json={"tool": cmd["tool"], "args": cmd.get("args", {})},
                            timeout=30,
                        )
                        data = resp.json()
                        await ws.send_text(json.dumps({"type": "mcp_result", "result": data}))
                elif cmd.get("type") == "hasura":
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(
                            HASURA_URL,
                            json={"query": cmd["query"]},
                            headers={
                                "x-hasura-admin-secret": HASURA_SECRET,
                                "Content-Type": "application/json",
                            },
                            timeout=15,
                        )
                        data = resp.json()
                        await ws.send_text(json.dumps({"type": "hasura_result", "data": data}))
            except Exception as e:
                await ws.send_text(json.dumps({"type": "error", "error": str(e)}))
    except WebSocketDisconnect:
        connections.discard(ws)
    except Exception:
        connections.discard(ws)
