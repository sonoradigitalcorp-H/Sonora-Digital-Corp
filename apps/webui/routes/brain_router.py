"""
Brain Graph Visualization — JARVIS System Architecture as a Knowledge Graph.
Includes live agent activity stream.
"""

import asyncio
import json
import logging
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse

from src.core.brain_graph import SYSTEM_GRAPH
from src.core.activity_broadcaster import get_broadcaster

log = logging.getLogger("jarvis.webui.brain")
router = APIRouter(prefix="/api/brain", tags=["brain"])
STATIC_DIR = Path(__file__).parent.parent / "static"


@router.get("/graph")
async def get_brain_graph():
    """Returns the full system architecture as a JSON graph."""
    return JSONResponse(SYSTEM_GRAPH)


@router.get("/graph-page", response_class=HTMLResponse)
async def get_brain_page():
    """Returns the D3.js brain visualization HTML page."""
    brain_html = STATIC_DIR / "brain.html"
    if brain_html.exists():
        return HTMLResponse(brain_html.read_text())
    return HTMLResponse(
        "<html><body><h1>Brain visualization not found</h1></body></html>",
        status_code=404,
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def get_brain_dashboard():
    """Returns the professional JARVIS Command Center dashboard."""
    dashboard = STATIC_DIR / "brain-dashboard.html"
    if dashboard.exists():
        return HTMLResponse(dashboard.read_text())
    return HTMLResponse(
        "<html><body><h1>Dashboard not found</h1></body></html>", status_code=404
    )


@router.get("/activity")
async def get_recent_activity(limit: int = 50):
    """Returns recent agent activity events."""
    return JSONResponse(get_broadcaster().recent(limit))


@router.get("/stream")
async def stream_activity(request: Request):
    """SSE endpoint for live agent activity."""
    broadcaster = get_broadcaster()
    q = broadcaster.subscribe()

    async def event_generator():
        try:
            # Send recent history as replay
            for event in broadcaster.recent(20):
                yield f"data: {json.dumps(event)}\n\n"
            yield f"data: {json.dumps({'type': 'connected', 'data': {}, 'timestamp': ''})}\n\n"

            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(q.get(), timeout=15)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            broadcaster.unsubscribe(q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )
