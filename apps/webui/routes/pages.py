import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from webui.routes.app_state import sessions

router = APIRouter()
BASE_DIR = Path(__file__).parent.parent
ROOT_DIR = (BASE_DIR / ".." / "..").resolve()
STATE_DIR = ROOT_DIR / "state"
INITIATIVES_DIR = ROOT_DIR / "sonora-enterprise-os" / "initiatives"
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
async def mystic_ui():
    ui_path = BASE_DIR / "static" / "new-ui.html"
    if ui_path.exists():
        return HTMLResponse(content=ui_path.read_text(encoding="utf-8"))
    return templates.TemplateResponse(
        "index.html", {"request": Request({"type": "http"})}
    )

@router.get("/landing", response_class=HTMLResponse)
@router.get("/mystic", response_class=HTMLResponse)
async def mystic_landing():
    landing_path = ROOT_DIR / "apps" / "landing" / "index.html"
    if landing_path.exists():
        return HTMLResponse(content=landing_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Landing page not found</h1>")


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
        result["memory"]["qdrant"] = (
            httpx.get("http://localhost:6333/healthz", timeout=3).status_code == 200
        )
    except Exception:
        pass
    return result


def _read_jsonl(path):
    records = []
    if path.exists():
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return records


@router.get("/api/enterprise-score")
async def enterprise_score():
    from metrics.enterprise_score import compute_enterprise_score
    result = compute_enterprise_score()
    return {
        "total": result["enterprise_score"],
        "max": 100,
        "metrics": result["metrics"],
        "threshold_met": result["threshold_met"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/finops")
async def finops_summary():
    records = _read_jsonl(STATE_DIR / "finops.jsonl")
    ai_calls = [r for r in records if r.get("event") == "ai_call"]
    total_calls = len(ai_calls)
    total_cost = sum(c.get("cost", 0) for c in ai_calls)
    total_input_tokens = sum(c.get("input_tokens", 0) for c in ai_calls)
    total_output_tokens = sum(c.get("output_tokens", 0) for c in ai_calls)
    total_tokens = sum(c.get("total_tokens", 0) for c in ai_calls)

    model_breakdown = {}
    for c in ai_calls:
        model = c.get("model", "unknown")
        if model not in model_breakdown:
            model_breakdown[model] = {"calls": 0, "cost": 0.0, "tokens": 0}
        model_breakdown[model]["calls"] += 1
        model_breakdown[model]["cost"] += c.get("cost", 0)
        model_breakdown[model]["tokens"] += c.get("total_tokens", 0)
    for m in model_breakdown.values():
        m["cost"] = round(m["cost"], 6)
        m["avg_cost_per_call"] = round(m["cost"] / m["calls"], 8) if m["calls"] > 0 else 0

    return {
        "total_calls": total_calls,
        "total_cost": round(total_cost, 6),
        "total_tokens": total_tokens,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "avg_cost_per_call": round(total_cost / max(1, total_calls), 8),
        "model_breakdown": model_breakdown,
        "baseline": next((r for r in records if r.get("event") == "finops_baseline"), None),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/health")
async def health_status():
    result = {
        "services": {},
        "docker_containers": {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    checks = {
        "webui": "http://localhost:5174/api/status",
        "hermes": "http://localhost:8000/health",
        "openclaw": "http://localhost:18789/health",
    }
    for name, url in checks.items():
        try:
            r = httpx.get(url, timeout=3)
            result["services"][name] = {"status": "healthy" if r.status_code == 200 else "error", "status_code": r.status_code}
        except Exception:
            result["services"][name] = {"status": "offline"}
    try:
        docker_result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True, timeout=5)
        running = set(n for n in docker_result.stdout.strip().split("\n") if n)
        for container in ["jarvis-neo4j", "jarvis-qdrant", "hermes_api", "infra_postgres", "infra_redis"]:
            result["docker_containers"][container] = {"running": container in running}
    except Exception:
        for c in ["jarvis-neo4j", "jarvis-qdrant", "hermes_api", "infra_postgres", "infra_redis"]:
            result["docker_containers"][c] = {"running": False, "error": "docker_check_failed"}
    return result


@router.get("/api/initiatives")
async def list_initiatives():
    initiatives = []
    if not INITIATIVES_DIR.exists():
        return initiatives
    for fpath in sorted(INITIATIVES_DIR.glob("*.md")):
        if fpath.name in ("initiative-TEMPLATE.md", "REGISTRY.md"):
            continue
        text = fpath.read_text(encoding="utf-8")
        lines = text.split("\n")
        in_objective = False
        objective_parts = []
        score = ""
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## 1. Objective"):
                in_objective = True
                continue
            if in_objective:
                if stripped.startswith("##"):
                    break
                if stripped and not stripped.startswith("<!--"):
                    objective_parts.append(stripped)
            if "**Total Score:" in stripped or stripped.startswith("**Total Score:"):
                score = stripped.split("**Total Score:")[-1].strip().removesuffix("**").strip()
            elif "Total Score:" in stripped and not score:
                score = stripped.split("Total Score:")[-1].strip()
        initiatives.append({
            "name": fpath.stem,
            "objective": " ".join(objective_parts),
            "score": score,
            "file": fpath.name,
        })
    return initiatives


@router.get("/omega", response_class=HTMLResponse)
async def omega_dashboard():
    dashboard_path = BASE_DIR / "static" / "omega-dashboard.html"
    if dashboard_path.exists():
        return HTMLResponse(content=dashboard_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Dashboard not found</h1>")
