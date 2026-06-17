from pathlib import Path
from datetime import datetime, timezone

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from webui.routes.app_state import app, sessions, get_orchestrator

router = APIRouter()
BASE_DIR = Path(__file__).parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
async def mystic_ui():
    ui_path = BASE_DIR / "static" / "new-ui.html"
    if ui_path.exists():
        return HTMLResponse(content=ui_path.read_text(encoding="utf-8"))
    return templates.TemplateResponse(
        "index.html", {"request": Request({"type": "http"})}
    )


@router.get("/legacy", response_class=HTMLResponse)
async def legacy_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/api/status")
async def system_status():
    return {
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {"webui": "running", "sessions": len(sessions)},
    }


@router.get("/api/unified/status")
async def unified_status():
    result = {
        "jarvis": {"status": "ok", "version": "2.0.0"},
        "hermes": {"status": "unknown"},
        "openclaw": {"status": "unknown"},
        "gbrain": {"status": "unknown"},
        "memory": {"neo4j": False, "qdrant": False},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        import httpx

        hr = httpx.get("http://localhost:8000/health", timeout=3)
        result["hermes"] = (
            {"status": "ok", "version": hr.json().get("version", "?")}
            if hr.status_code == 200
            else {"status": "error"}
        )
    except Exception:
        result["hermes"] = {"status": "offline"}
    try:
        import httpx

        oc = httpx.get("http://localhost:18789/health", timeout=3)
        result["openclaw"] = (
            {"status": "ok"} if oc.status_code == 200 else {"status": "error"}
        )
    except Exception:
        result["openclaw"] = {"status": "offline"}
    try:
        from src.core.unified_bridge import GbrainBridge

        result["gbrain"] = GbrainBridge().health()
    except Exception:
        result["gbrain"] = {"status": "offline"}
    try:
        from src.core.neo4j_store import test_connection

        result["memory"]["neo4j"] = test_connection()
    except Exception:
        pass
    try:
        import httpx

        result["memory"]["qdrant"] = (
            httpx.get("http://localhost:6333/healthz", timeout=3).status_code == 200
        )
    except Exception:
        pass
    return result
