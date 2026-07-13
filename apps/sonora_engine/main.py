"""Sonora OS Engine — FastAPI entry point [FR5, FR8].

Procesa mensajes de la cola telegram:inbox y expone WebSocket para dashboards.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from .router import RouterAgent

log = logging.getLogger("sonora.engine.main")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
INBOX_KEY = "telegram:inbox"
OUTBOX_KEY = "telegram:outbox"
EVENTS_KEY = "agent:events"

router_agent = RouterAgent()

# Active WebSocket connections: tenant_id -> set of WebSocket
active_connections: dict[str, set[WebSocket]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background workers on startup."""
    task = asyncio.create_task(inbox_worker())
    yield
    task.cancel()


app = FastAPI(title="Sonora OS Engine", lifespan=lifespan)

# Serve dashboard + client static files
_dashboard_dir = Path(__file__).resolve().parent.parent.parent / "products" / "sonora-dashboard"
if _dashboard_dir.exists():
    app.mount("/dashboard", StaticFiles(directory=str(_dashboard_dir), html=True), name="dashboard")
_client_dir = Path(__file__).resolve().parent.parent.parent / "products" / "sonora-client"
if _client_dir.exists():
    app.mount("/app", StaticFiles(directory=str(_client_dir), html=True), name="client")


async def inbox_worker():
    """Background: poll telegram:inbox and route messages."""
    r = aioredis.from_url(REDIS_URL)
    last_id = "0-0"

    while True:
        try:
            result = await r.xread({INBOX_KEY: last_id}, count=10, block=1000)
            for stream, entries in result:
                for entry_id, data in entries:
                    last_id = entry_id
                    message = {k.decode(): v.decode() for k, v in data.items()}
                    await process_message(message)
        except Exception as e:
            log.error(f"Inbox worker error: {e}")
        await asyncio.sleep(0.1)


async def process_message(message: dict):
    """Route a single message through the engine."""
    chat_id = int(message.get("chat_id", 0))
    text = message.get("text", "")
    user_id = int(message.get("user_id", 0))

    result = router_agent.process(text, telegram_id=user_id)

    # Build response based on routed agent
    response = await execute_agent(result["agent"], result["tenant"], text)

    # Push response to outbox
    r = aioredis.from_url(REDIS_URL)
    await r.xadd(OUTBOX_KEY, {
        "chat_id": str(chat_id),
        "text": response,
        "parse_mode": "HTML",
    }, maxlen=10000)

    # Emit agent event for WebSocket dashboards
    await r.publish(EVENTS_KEY, json.dumps({
        "event_type": f"agent:{result['agent']}",
        "tenant_id": result["tenant"].get("tenant_id", "unknown") if result["tenant"] else "unknown",
        "intent": result["intent"],
        "agent": result["agent"],
    }))


async def execute_agent(agent_name: str, tenant_info: dict | None, text: str) -> str:
    """Execute the routed agent and return a response."""
    tenant_slug = tenant_info.get("slug", "unknown") if tenant_info else "unknown"

    if agent_name == "chat_agent":
        return f"Procesando tu consulta como {tenant_slug}..."
    elif agent_name == "monetization_agent":
        return "Veo que quieres información sobre precios o saludos. ¿Qué artista te interesa?"
    elif agent_name == "gamification_agent":
        return "¡Genial! Puedes ganar $BEAT completando quests. ¿Qué tipo de actividad prefieres?"
    elif agent_name == "knowledge_agent":
        return "Déjame consultar la información del artista..."
    elif agent_name == "automation_agent":
        return "Puedo ayudarte a programar mensajes automáticos. ¿Qué horario prefieres?"
    else:
        return f"Entendido. Estoy procesando tu solicitud."


@app.get("/health")
async def health():
    return {"status": "ok", "engine": "sonora"}


# ─── Dashboard API [FR7] ───


@app.get("/api/v1/dashboard/revenue")
async def dashboard_revenue(tenant_id: str = Query(...)):
    from .dashboard import DashboardService
    svc = DashboardService()
    return svc.get_revenue_stats(tenant_id)


@app.get("/api/v1/dashboard/tokens")
async def dashboard_tokens(tenant_id: str = Query(...)):
    from .dashboard import DashboardService
    svc = DashboardService()
    return svc.get_token_stats(tenant_id)


@app.get("/api/v1/dashboard/greetings")
async def dashboard_greetings(tenant_id: str = Query(...)):
    from .dashboard import DashboardService
    svc = DashboardService()
    return svc.get_greeting_stats(tenant_id)


@app.get("/api/v1/dashboard/quests")
async def dashboard_quests(tenant_id: str = Query(...)):
    from .dashboard import DashboardService
    svc = DashboardService()
    return svc.get_quest_stats(tenant_id)


@app.get("/api/v1/dashboard/leaderboard")
async def dashboard_leaderboard(
    tenant_id: str = Query(...),
    metric: str = Query("xp"),
    limit: int = Query(5),
):
    from .dashboard import DashboardService
    svc = DashboardService()
    return svc.get_leaderboard(tenant_id, metric=metric, limit=limit)


@app.get("/api/v1/dashboard/streams")
async def dashboard_streams(tenant_id: str = Query(...)):
    from .dashboard import DashboardService
    svc = DashboardService()
    return svc.get_artist_streams(tenant_id)


@app.get("/api/v1/rag/query")
async def rag_query(tenant_id: str = Query(...), q: str = Query(...), limit: int = Query(5)):
    from .rag_per_tenant import query_rag as rag_search
    return rag_search(tenant_id, q, limit=limit)


@app.get("/api/v1/rag/collections")
async def rag_collections():
    from .rag_per_tenant import list_collections
    return list_collections()


@app.get("/api/v1/auth/me")
async def auth_me():
    """Return current auth status (for client session check)."""
    return {
        "authenticated": True,
        "tenant_id": "abe-music",
        "role": "client_admin",
    }


@app.get("/api/v1/dashboard/seed")
async def seed_demo_data(tenant_id: str = Query("abe-music")):
    from .gamification import QuestEngine, Leaderboard, _pool_balances, _completions, _leaderboard_data
    from .payments import _balances, _pools, _greetings

    _pool_balances[tenant_id] = 1000000
    _pools[tenant_id] = {"total": 1000000, "circulating": 250000, "burned": 50000}
    _balances.clear()
    _leaderboard_data.clear()
    _greetings.clear()

    fans = ["fan-alfonso", "fan-maria", "fan-carlos", "fan-diana", "fan-luis", "fan-sonia", "fan-pedro", "fan-ana"]
    levels = ["bronze", "silver", "gold", "platinum"]
    for i, fan in enumerate(fans):
        xp = (i + 1) * 120
        beat = (i + 1) * 25
        _balances[fan] = beat
        _leaderboard_data.setdefault(tenant_id, {})[fan] = {"xp": xp, "beat": beat, "level": levels[min(i // 2, 3)]}
        _greetings[f"greet-{i}"] = {"id": f"greet-{i}", "artist_name": "Hector Rubio", "message": f"Saludo #{i+1}", "status": ["approved","pending_approval","approved","rejected","approved","pending","approved","approved"][i]}

    return {"status": "seeded", "tenant": tenant_id}


def emit_event(event_type: str, tenant_id: str, payload: dict | None = None):
    """Emit event to Redis for WebSocket streaming [FR8]."""
    import redis as sync_redis
    try:
        r = sync_redis.Redis.from_url(REDIS_URL)
        r.publish(EVENTS_KEY, json.dumps({
            "event_type": event_type,
            "tenant_id": tenant_id,
            **({"payload": payload} if payload else {}),
        }))
    except Exception as e:
        log.error(f"Event emit failed: {e}")


@app.get("/events/{tenant_id}")
async def get_events(tenant_id: str, limit: int = 50):
    """Get recent events for a tenant (REST fallback for WebSocket)."""
    try:
        from .hasura import query
        result = query("""
            query GetEvents($tenant_id: uuid!, $limit: Int!) {
                agent_events(
                    where: {tenant_id: {_eq: $tenant_id}}
                    order_by: {created_at: desc}
                    limit: $limit
                ) {
                    event_type
                    agent_name
                    payload
                    created_at
                }
            }
        """, {"tenant_id": tenant_id, "limit": limit})
        return result.get("data", {}).get("agent_events", [])
    except Exception:
        return []


@app.websocket("/ws/{tenant_id}")
async def websocket_endpoint(websocket: WebSocket, tenant_id: str):
    """WebSocket endpoint for real-time dashboard events [FR8]."""
    await websocket.accept()

    if tenant_id not in active_connections:
        active_connections[tenant_id] = set()
    active_connections[tenant_id].add(websocket)

    try:
        # Subscribe to Redis events for this tenant
        r = aioredis.from_url(REDIS_URL)
        async def listener():
            async with r.pubsub() as pubsub:
                await pubsub.subscribe(EVENTS_KEY)
                async for msg in pubsub.listen():
                    if msg["type"] == "message":
                        data = json.loads(msg["data"])
                        if data.get("tenant_id") == tenant_id:
                            await websocket.send_json(data)

        # Run listener in background
        task = asyncio.create_task(listener())

        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        active_connections.get(tenant_id, set()).discard(websocket)
