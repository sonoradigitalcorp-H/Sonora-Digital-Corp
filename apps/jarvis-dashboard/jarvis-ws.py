"""JARVIS WebSocket Bridge — Voice-to-action pipeline via aiohttp.

Listens on port 8769, receives voice transcripts, classifies intents,
executes actions, and returns results. Also serves the dashboard static files.
"""

import json
import logging
import os
import sys
from pathlib import Path

from aiohttp import web

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from jarvis_actions import ActionRouter, ActionResult

log = logging.getLogger("jarvis.ws")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

DASHBOARD_DIR = Path(__file__).resolve().parent
PORT = int(os.getenv("JARVIS_WS_PORT", "8769"))

router = ActionRouter()

INTENT_KEYWORDS = {
    "open_page": ["abre", "abrir", "open", "navega", "ir a", "go to", "visita"],
    "query_db": ["consulta", "query", "select", "sql", "datos"],
    "show_content": ["muestra", "show", "presenta", "display", "enseña"],
    "create_dashboard": ["dashboard", "panel", "resumen visual"],
    "send_message": ["envía", "envia", "manda", "send", "mensaje"],
    "take_screenshot": ["screenshot", "captura", "pantallazo", "capture"],
    "playwright_action": ["click", "haz click", "presiona", "llena", "fill"],
    "system_status": ["estado", "status", "salud", "health", "servicios"],
    "shutdown_mic": ["apaga", "para", "stop", "callar", "silencio", "mute"],
}


def classify_intent(text: str) -> tuple[str, dict]:
    lower = text.lower().strip()
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                return intent, _extract_params(intent, text)
    return "show_content", {"title": "Respuesta", "items": [text]}


def _extract_params(intent: str, text: str) -> dict:
    if intent == "open_page":
        for w in text.split():
            if w.startswith("http") or ("." in w and not w.startswith(".")):
                return {"url": w.rstrip(",.;:!?")}
        return {"url": "https://google.com"}
    if intent == "query_db":
        lower = text.lower()
        if "select" in lower:
            return {"sql": text[lower.find("select"):].strip()}
        return {"sql": "SELECT now() AS timestamp"}
    if intent == "send_message":
        return {"text": text, "target": "", "platform": "telegram"}
    if intent == "take_screenshot":
        return {"url": None}
    return {}


async def get_context(user_id: str, text: str) -> str:
    """Placeholder — integrate with engram memory and RAG search."""
    return ""


def build_response(result: ActionResult, context: str) -> dict:
    resp = {"type": "response", "text": result.text, "action": result.action}
    if result.screenshot_path:
        resp["screenshot"] = result.screenshot_path
    if result.dashboard_html:
        resp["dashboard_html"] = result.dashboard_html
    if result.needs_confirmation:
        resp["needs_confirmation"] = True
    if result.extra:
        resp["extra"] = result.extra
    return resp


connected_clients: set[web.WebSocketResponse] = set()


async def ws_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    connected_clients.add(ws)
    log.info("Client connected (%d total)", len(connected_clients))
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = json.loads(msg.data)
                await ws.send_json(await _process_message(data))
            elif msg.type == web.WSMsgType.ERROR:
                log.warning("WS error: %s", ws.exception())
    finally:
        connected_clients.discard(ws)
    return ws


async def _process_message(data: dict) -> dict:
    if data.get("type") != "voice_input":
        return {"type": "error", "text": f"Tipo no soportado: {data.get('type')}"}
    text, user_id = data.get("text", "").strip(), data.get("user_id", "unknown")
    if not text:
        return {"type": "error", "text": "Texto vacío"}
    intent, params = classify_intent(text)
    ctx = await get_context(user_id, text)
    if ctx:
        params["_context"] = ctx
    log.info("[%s] intent=%s", user_id, intent)
    return build_response(await router.execute(intent, params), ctx)


async def health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "clients": len(connected_clients)})


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/ws", ws_handler)
    app.router.add_get("/health", health)
    if DASHBOARD_DIR.exists():
        app.router.add_static("/", path=str(DASHBOARD_DIR), name="dashboard", show_index=True)

    @web.middleware
    async def cors_middleware(request, handler):
        if request.method == "OPTIONS":
            resp = web.Response(status=204)
        else:
            resp = await handler(request)
        resp.headers["Access-Control-Allow-Origin"] = "http://localhost:*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return resp
    app.middlewares.append(cors_middleware)
    return app


if __name__ == "__main__":
    log.info("Starting JARVIS WS on port %d", PORT)
    web.run_app(create_app(), host="0.0.0.0", port=PORT)
