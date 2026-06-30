import json
import logging
import subprocess

from fastapi import APIRouter
from webui.routes.app_state import PROJECT_DIR

router = APIRouter()
log = logging.getLogger("jarvis.webui.webhooks")


@router.post("/api/webhook/n8n-backup")
async def n8n_trigger_backup():
    try:
        result = subprocess.run(
            ["bash", str(PROJECT_DIR / "scripts" / "backup.sh")],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "status": "ok" if result.returncode == 0 else "error",
            "output": result.stdout[-500:],
            "error": result.stderr[-500:],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.post("/api/webhook/n8n-healthcheck")
async def n8n_trigger_healthcheck():
    try:
        result = subprocess.run(
            ["bash", str(PROJECT_DIR / "scripts" / "healthcheck.sh")],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {
            "status": "healthy" if result.returncode == 0 else "unhealthy",
            "output": result.stdout[-500:],
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@router.post("/api/webhook/n8n-restore")
async def n8n_trigger_restore():
    try:
        services = ["jarvis-neo4j"]
        results = []
        for svc in services:
            r = subprocess.run(
                ["docker", "start", svc], capture_output=True, text=True, timeout=15
            )
            results.append({"service": svc, "status": r.returncode})
        return {"status": "restored", "services": results}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.post("/api/webhook/n8n-incoming")
async def n8n_incoming(data: dict):
    log.info(f"n8n incoming: {json.dumps(data)[:200]}")
    return {"status": "received", "echo": data}


@router.get("/api/webhook/n8n-status")
async def n8n_status():
    return {
        "n8n_url": "http://localhost:5679",
        "webhooks": [
            "/api/webhook/n8n-backup",
            "/api/webhook/n8n-healthcheck",
            "/api/webhook/n8n-restore",
            "/api/webhook/n8n-incoming",
        ],
        "workflow_templates": [
            "config/n8n/backup-workflow.json",
            "config/n8n/healthcheck-workflow.json",
            "config/n8n/webhook-bridge.json",
        ],
    }
