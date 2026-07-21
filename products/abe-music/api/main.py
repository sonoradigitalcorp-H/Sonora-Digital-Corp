import logging
import sys
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

BASE = Path(__file__).resolve().parent.parent.parent
for p in [BASE, BASE / "apps", BASE / "apps" / "jarvis" / "src"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from .api.rest import router as rest_router
from .api.ws import handle_websocket
from .config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("abe.main")

app = FastAPI(
    title="ABE Music OS",
    version="1.0.0",
    description="Internal OS for ABE Music — voice-first, AI-powered label management",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rest_router)

PWA_DIR = Path(__file__).resolve().parent / "pwa"
if PWA_DIR.exists():
    app.mount("/pwa", StaticFiles(directory=str(PWA_DIR), html=True), name="pwa")

AVATAR_DIR = Path(__file__).resolve().parent / "avatar"
if AVATAR_DIR.exists():
    app.mount("/avatar", StaticFiles(directory=str(AVATAR_DIR), html=True), name="avatar")

WEB_DIR = Path(__file__).resolve().parent / "web"
if WEB_DIR.exists():
    app.mount("/web", StaticFiles(directory=str(WEB_DIR), html=True), name="web")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await handle_websocket(websocket)


@app.on_event("startup")
async def startup():
    log.info(f"ABE Music OS starting on {config.ws_host}:{config.ws_port}")
    log.info(f"Brand: {config.name}")
    log.info(f"Tenant: {config.tenant_id}")
    log.info(f"MCP Gateway: {config.mcp_gateway_url}")
    log.info(f"Sys.path: {[p for p in sys.path if 'sonora' in p]}")


@app.on_event("shutdown")
async def shutdown():
    log.info("ABE Music OS shutting down")


@app.get("/")
async def root():
    web_index = WEB_DIR / "index.html"
    if web_index.exists():
        return HTMLResponse(web_index.read_text())
    return {
        "service": "ABE Music OS", "powered_by": "Sonora Digital Corp",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "ws": "/ws",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.ws_host, port=config.ws_port)
