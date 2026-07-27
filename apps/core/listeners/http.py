"""HTTP Listener — Kernel entry point via FastAPI (HAS-004)
Provides REST API for the Kernel: process, health, stats.
"""
import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from kernel.main import HermesKernel


ROOT = Path(__file__).resolve().parent.parent.parent
app = FastAPI(title="Hermes Kernel", version="1.0.0", docs_url="/kernel/docs")
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
