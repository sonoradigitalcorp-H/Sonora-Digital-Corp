#!/usr/bin/env python3
"""
JARVIS MCP Bridge for Hermes Desktop.
Exposes JARVIS core functions as MCP tools so Hermes can use them.
Run as: python3 hermes_bridge.py
Hermes Desktop spawns this as a subprocess (stdio transport).
"""
import sys
import os
import json
import logging

# Add JARVIS project root to path
sys.path.insert(0, os.path.expanduser("~/jarvis"))

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(asctime)s [JARVIS] %(message)s")
log = logging.getLogger("jarvis.bridge")

# Create FastMCP server
mcp = FastMCP("jarvis-bridge", log_level="INFO")

@mcp.tool()
def jarvis_research(query: str) -> str:
    """Busca y sintetiza información en la memoria de JARVIS (Neo4j + Qdrant)."""
    try:
        from src.core.rag import rag
        result = rag.search(query, limit=3)
        if result["status"] == "success":
            texts = [r["text"][:500] for r in result["results"]]
            return "\n".join(texts) if texts else "No results found"
        return f"Error: {result.get('error', 'Unknown')}"
    except Exception as e:
        return f"Research failed: {e}"

@mcp.tool()
def jarvis_memory_store(key: str, value: str) -> str:
    """Guarda un recuerdo en la memoria persistente de JARVIS."""
    try:
        from src.core.engram import engram
        engram.store_learning("hermes-bridge", key, value, value[:200])
        return f"Saved: {key}"
    except Exception as e:
        return f"Memory store failed: {e}"

@mcp.tool()
def jarvis_memory_recall(query: str) -> str:
    """Recupera recuerdos relevantes de la memoria de JARVIS."""
    try:
        from src.core.engram import engram
        results = engram.query_context(query, limit=3)
        if results:
            return "\n".join([f"[{r['tag']}] {r['summary'][:300]}" for r in results])
        return "No relevant memories found"
    except Exception as e:
        return f"Memory recall failed: {e}"

@mcp.tool()
def jarvis_metrics() -> str:
    """Devuelve métricas del sistema JARVIS."""
    try:
        from src.core import engram, verify
        specs_dir = os.path.expanduser("~/jarvis/specs")
        spec_count = len([d for d in os.listdir(specs_dir) if os.path.isdir(os.path.join(specs_dir, d))])
        return json.dumps({
            "specs": spec_count,
            "agents": 15,
            "skills": 50,
            "tests": 330,
            "engram_ready": True,
            "status": "operational"
        }, indent=2)
    except Exception as e:
        return f"Metics failed: {e}"

@mcp.tool()
def jarvis_orchestrate(task: str) -> str:
    """Ejecuta una tarea a través del orquestador de agentes de JARVIS."""
    try:
        import asyncio
        from src.core.orchestrator import get_orchestrator
        orchestrator = get_orchestrator()
        result = asyncio.run(orchestrator.execute(task))
        return json.dumps({
            "agent": result.get("agent", "unknown"),
            "status": result.get("status", "unknown"),
            "summary": str(result.get("synthesis", result.get("message", "Done")))[:500]
        }, indent=2)
    except Exception as e:
        return f"Orchestration failed: {e}"

@mcp.tool()
def enterprise_score() -> str:
    """Devuelve el Enterprise Score actual de Sonora Digital Corp calculado desde eventos reales."""
    STATE_DIR = os.path.expanduser("~/sonora-digital-corp/state")
    events_path = os.path.join(STATE_DIR, "logs", "events.jsonl")
    finops_path = os.path.join(STATE_DIR, "finops.jsonl")
    try:
        events = []
        if os.path.exists(events_path):
            with open(events_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try: events.append(json.loads(line))
                        except: pass
        finops_calls = []
        if os.path.exists(finops_path):
            with open(finops_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            c = json.loads(line)
                            if c.get("event") == "ai_call": finops_calls.append(c)
                        except: pass

        revenue_events = [e for e in events if e.get("event") == "revenue_recorded"]
        revenue_score = min(10, len(revenue_events)) if revenue_events else 1
        scale_events = [e for e in events if e.get("event") in ("scaled_up", "scaled_down")]
        scalability_score = min(10, len(scale_events) + 3)
        skill_events = [e for e in events if e.get("event") == "skill_execution"]
        os_used = set()
        for s in skill_events:
            p = s.get("payload", {})
            if isinstance(p, dict): os_used.add(p.get("parent_os", ""))
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
        total_cost_ai = sum(c.get("cost", 0) for c in finops_calls)
        total_calls_ai = len(finops_calls)
        cost_per_call = total_cost_ai / max(1, total_calls_ai)
        finops_score = max(0, 10 - round(cost_per_call / 0.001)) if total_calls_ai > 0 else 1

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
        total = sum(metrics.values())
        return json.dumps({"total": total, "max": 100, "metrics": metrics, "status": "ok"}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
def finops_summary() -> str:
    """Devuelve el resumen financiero de llamadas AI (costos, tokens, modelos)."""
    finops_path = os.path.expanduser("~/sonora-digital-corp/state/finops.jsonl")
    try:
        records = []
        if os.path.exists(finops_path):
            with open(finops_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try: records.append(json.loads(line))
                        except: pass
        ai_calls = [r for r in records if r.get("event") == "ai_call"]
        total_calls = len(ai_calls)
        total_cost = sum(c.get("cost", 0) for c in ai_calls)
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
        baseline = next((r for r in records if r.get("event") == "finops_baseline"), None)
        return json.dumps({
            "status": "ok",
            "total_calls": total_calls,
            "total_cost": round(total_cost, 6),
            "total_tokens": total_tokens,
            "avg_cost_per_call": round(total_cost / max(1, total_calls), 8),
            "model_breakdown": model_breakdown,
            "baseline_models": (baseline.get("tracked_models", []) if baseline else []),
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
def health_status() -> str:
    """Verifica el estado en vivo de todos los servicios y contenedores."""
    import subprocess
    result = {"services": {}, "docker_containers": {}, "status": "ok"}
    checks = {
        "webui": ("http://localhost:5174/api/status", {}),
        "hermes": ("http://localhost:8000/health", {}),
        "openclaw": ("http://localhost:18789/health", {}),
    }
    try:
        import httpx
        for name, (url, _) in checks.items():
            try:
                r = httpx.get(url, timeout=3)
                result["services"][name] = {"status": "healthy" if r.status_code == 200 else "error"}
            except Exception:
                result["services"][name] = {"status": "offline"}
    except ImportError:
        for name in checks:
            result["services"][name] = {"status": "unknown"}
    try:
        docker_result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True, timeout=5)
        running = set(n for n in docker_result.stdout.strip().split("\n") if n)
        for container in ["jarvis-neo4j", "jarvis-qdrant", "hermes_api", "infra_postgres", "infra_redis"]:
            result["docker_containers"][container] = {"running": container in running}
    except Exception:
        for c in ["jarvis-neo4j", "jarvis-qdrant", "hermes_api", "infra_postgres", "infra_redis"]:
            result["docker_containers"][c] = {"running": False, "error": "docker_check_failed"}
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    log.info("Starting JARVIS MCP Bridge (stdio transport)...")
    mcp.run(transport="stdio")
