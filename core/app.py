"""Kernel FastAPI app — HTTP + WebSocket (HAS-004, HAS-009)
Serves as the main entry point for the Kernel daemon.
Emits progressive Orb states during processing.
"""
import asyncio
import json
import time
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from kernel.main import HermesKernel
from events.listener import EventListener
from events.handlers import MemoryHandler, AlertHandler


ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Hermes Kernel", version="1.0.0")
kernel: HermesKernel | None = None
active_connections: list[WebSocket] = []
event_listener: EventListener | None = None


@app.on_event("startup")
async def startup():
    global kernel, event_listener
    config = {}
    config_path = ROOT / "kernel" / "config.json"
    if config_path.exists():
        config = json.loads(config_path.read_text())
    kernel = HermesKernel(config)
    event_listener = EventListener()
    event_listener.register(MemoryHandler())
    event_listener.register(AlertHandler())
    await event_listener.start()
    print("[kernel] Event listeners started")


async def broadcast(data: dict):
    """Send to all connected WebSocket clients."""
    for ws in active_connections.copy():
        try:
            await ws.send_json(data)
        except Exception:
            active_connections.remove(ws)


async def _orb_state(ws, state: str, message: str, progress: int | None = None, actions: list | None = None):
    await ws.send_json({
        "type": "orb.state",
        "state": state,
        "message": message,
        "progress": progress,
        "actions": actions or [],
    })


@app.post("/kernel/process")
async def process(request: Request):
    body = await request.json()
    t0 = time.monotonic()
    await broadcast({"type": "orb.state", "state": "thinking", "message": "Processing request...", "progress": None})
    results = await kernel.process(body)
    await broadcast({"type": "orb.state", "state": "completed", "message": f"Done in {int((time.monotonic() - t0) * 1000)}ms", "progress": 100})
    return JSONResponse(content={"results": results})


@app.get("/kernel/health")
async def health():
    status = await kernel.health()
    return JSONResponse(content=status)


@app.get("/kernel/stats")
async def stats():
    return JSONResponse(content={
        "context": kernel.context.get_stats(),
        "executor": kernel.executor.get_stats(),
        "agents": len(kernel.router.list_agents()),
        "tenants": kernel.tenants.get_stats(),
        "capabilities": len(kernel.bus.list_status()),
    })


@app.get("/kernel/events")
async def recent_events(limit: int = 20):
    events_file = ROOT / "state" / "events" / "events.jsonl"
    if not events_file.exists():
        return JSONResponse(content={"events": []})
    lines = events_file.read_text().strip().split("\n")
    recent = [json.loads(l) for l in lines[-limit:] if l.strip()]
    return JSONResponse(content={"events": recent})


@app.websocket("/kernel/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    active_connections.append(ws)
    await _orb_state(ws, "idle", "Connected to Hermes Kernel", 0)
    try:
        while True:
            data = await ws.receive_text()
            raw = json.loads(data)
            input_text = raw.get("input", "")
            channel = raw.get("channel", "web")

            await _orb_state(ws, "listening", f"Received: {input_text[:100]}", 0)

            await _orb_state(ws, "thinking", "Planning execution...", 10)
            await asyncio.sleep(0.05)

            await _orb_state(ws, "executing", "Running through pipeline...", 30)
            t0 = time.monotonic()
            results = await kernel.process(raw)

            for i, r in enumerate(results, 1):
                progress = 30 + int(70 * i / len(results))
                status_icon = "✅" if r.get("status") == "success" else "❌"
                await _orb_state(ws, "executing" if i < len(results) else "completed",
                    f"{status_icon} Task {i}/{len(results)}: {r.get('status', '?')} via {r.get('agent', '?')} ({r.get('duration_ms', 0)}ms)",
                    progress)
                await ws.send_json({"type": "result", **r})
                await asyncio.sleep(0.03)

            await _orb_state(ws, "completed", f"Done — {len(results)} tasks in {int((time.monotonic() - t0) * 1000)}ms", 100)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await _orb_state(ws, "alert", f"Error: {str(e)[:200]}")
        except Exception:
            pass
    finally:
        if ws in active_connections:
            active_connections.remove(ws)


@app.on_event("shutdown")
async def shutdown():
    global event_listener
    if event_listener:
        await event_listener.stop()


@app.get("/kernel/alerts")
async def alerts(limit: int = 10):
    if not event_listener:
        return JSONResponse(content={"alerts": []})
    handler = event_listener._handlers.get("alert")
    if handler:
        return JSONResponse(content={"alerts": handler.recent_alerts(limit)})
    return JSONResponse(content={"alerts": []})


@app.get("/kernel/listener")
async def listener_status():
    if not event_listener:
        return JSONResponse(content={"running": False, "handlers": []})
    return JSONResponse(content=event_listener.get_stats())
