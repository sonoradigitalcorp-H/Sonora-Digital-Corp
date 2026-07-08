"""Kernel FastAPI app — HTTP + WebSocket (HAS-004)
Serves as the main entry point for the Kernel daemon.
"""
import json
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from kernel.main import HermesKernel


ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Hermes Kernel", version="1.0.0")
kernel: HermesKernel | None = None


@app.on_event("startup")
async def startup():
    global kernel
    config = {}
    config_path = ROOT / "kernel" / "config.json"
    if config_path.exists():
        config = json.loads(config_path.read_text())
    kernel = HermesKernel(config)


@app.post("/kernel/process")
async def process(request: Request):
    body = await request.json()
    results = await kernel.process(body)
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
    })


@app.websocket("/kernel/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            raw = json.loads(data)
            # Emit orb state transitions as the kernel processes
            await ws.send_json({"type": "orb.state", "state": "thinking", "message": "Processing...", "progress": None, "actions": []})
            results = await kernel.process(raw)
            for r in results:
                await ws.send_json(r)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await ws.send_json({"type": "orb.state", "state": "alert", "message": str(e), "progress": None, "actions": []})
