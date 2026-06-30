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
    events = _read_jsonl(STATE_DIR / "logs" / "events.jsonl")
    finops_calls = [c for c in _read_jsonl(STATE_DIR / "finops.jsonl") if c.get("event") == "ai_call"]

    revenue_score = min(10, len([e for e in events if e.get("event") == "revenue_recorded"])) if any(e.get("event") == "revenue_recorded" for e in events) else 1
    scale_events = [e for e in events if e.get("event") in ("scaled_up", "scaled_down")]
    scalability_score = min(10, len(scale_events) + 3)
    skill_events = [e for e in events if e.get("event") == "skill_execution"]
    os_used = set()
    for s in skill_events:
        p = s.get("payload", {})
        if isinstance(p, dict):
            os_used.add(p.get("parent_os", ""))
    reusability_score = min(10, len(os_used))
    auto_events = len(skill_events)
    total_ops = len(events)
    automation_score = min(10, round(auto_events / max(1, total_ops) * 10)) if total_ops > 0 else 1
    knowledge_events = [e for e in events if e.get("event") == "knowledge_stored"]
    knowledge_score = min(10, len(knowledge_events))
    healthy = len([e for e in events if e.get("event") == "service_healthy"])
    down = len([e for e in events if e.get("event") == "service_down"])
    reliability_score = round(healthy / max(1, healthy + down) * 10) if (healthy + down) > 0 else 5
    recovered = len([e for e in events if e.get("event") == "service_recovered"])
    total_incidents = down + recovered
    founder_score = min(10, round(recovered / max(1, total_incidents) * 10)) if total_incidents > 0 else 1
    event_types = len(set(e.get("event", "") for e in events))
    simplicity_score = max(0, 10 - event_types // 10) if event_types > 0 else 10
    satisfaction_events = [e for e in events if e.get("event") == "satisfaction_recorded"]
    customer_score = min(10, len(satisfaction_events)) if satisfaction_events else 1
    total_cost = sum(c.get("cost", 0) for c in finops_calls)
    total_calls = len(finops_calls)
    cost_per_call = total_cost / max(1, total_calls)
    finops_score = max(0, 10 - round(cost_per_call / 0.001)) if total_calls > 0 else 1

    metrics = {
        "Revenue Impact": revenue_score,
        "Scalability": scalability_score,
        "Reusability": reusability_score,
        "Automation Impact": automation_score,
        "Knowledge Impact": knowledge_score,
        "Reliability": reliability_score,
        "Founder Independence": founder_score,
        "Operational Simplicity": simplicity_score,
        "Customer Value": customer_score,
        "FinOps Efficiency": finops_score,
    }
    return {
        "total": sum(metrics.values()),
        "max": 100,
        "metrics": metrics,
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
                score = stripped.split("**Total Score:")[-1].strip().rstrip("**").strip()
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
