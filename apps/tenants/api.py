"""FastAPI multi-tenant management API — port 8100."""

import json
import os
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .db import (
    create_agent,
    create_health_check,
    create_tenant,
    get_agents,
    get_all_tenants,
    get_env_vars,
    get_latest_health,
    get_tenant,
    init_db,
    set_env_vars,
    update_tenant_status,
)
from .models import Agent, EnvVar, HealthCheck, Tenant
from .monitor import generate_report, nightly_check

app = FastAPI(title="SDC Multi-Tenant System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    init_db()


# ── Register ──


@app.post("/api/tenants/register")
def register(name: str, email: str, plan: str = "trial"):
    tenant = create_tenant(name, email, plan)
    agent = create_agent(tenant.id, "voice")
    create_health_check(tenant.id, "ok", "Tenant created")
    return {
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "email": tenant.email,
            "plan": tenant.plan,
            "status": tenant.status,
            "api_key": tenant.api_key,
        },
        "agent": {
            "id": agent.id,
            "type": agent.agent_type,
            "status": agent.status,
        },
    }


# ── Onboard: generate env vars + credentials ──


@app.post("/api/tenants/onboard")
def onboard(name: str, email: str, plan: str = "trial"):
    tenant = create_tenant(name, email, plan)

    envs = [
        ("MCP_GATEWAY_URL", "http://localhost:8000", False),
        ("API_KEY", tenant.api_key, True),
        ("AGENT_CONFIG", json.dumps({"tenant_id": tenant.id, "plan": plan}), True),
        ("WEBHOOK_TOKEN", tenant.webhook_token, True),
        ("WEBHOOK_URL", f"http://localhost:8100/api/tenants/{tenant.id}/health", False),
        ("TENANT_ID", tenant.id, False),
    ]
    set_env_vars(tenant.id, envs)

    web_embed = f"""<!-- SDC Tenant Widget -->
<script>
  window.SDC_CONFIG = {{
    tenantId: "{tenant.id}",
    apiKey: "{tenant.api_key}",
    gatewayUrl: "http://localhost:8000"
  }};
</script>
<script src="http://localhost:8100/static/sdc-widget.js"></script>"""

    return {
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "email": tenant.email,
            "plan": tenant.plan,
            "status": tenant.status,
            "api_key": tenant.api_key,
        },
        "credentials": {
            "api_key": tenant.api_key,
            "webhook_token": tenant.webhook_token,
        },
        "environment_variables": [
            {"key": k, "value": v if not is_secret else "***"} for k, v, is_secret in envs
        ],
        "connections": {
            "web": {
                "url": f"http://localhost:8100/api/tenants/{tenant.id}/env",
                "embed_script": web_embed,
            },
            "telegram": {
                "bot_token": "YOUR_BOT_TOKEN",
                "webhook_url": f"http://localhost:8100/api/tenants/{tenant.id}/health",
                "instructions": f"Send /start {tenant.id} to connect this tenant to Telegram.",
            },
        },
    }


# ── Get env vars ──


@app.get("/api/tenants/{tid}/env")
def get_env(tid: str):
    tenant = get_tenant(tid)
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    vars = get_env_vars(tid)
    return {
        "tenant_id": tid,
        "tenant_name": tenant.name,
        "variables": [
            {
                "key": v.key,
                "value": v.value if not v.is_secret else "***",
                "is_secret": v.is_secret,
            }
            for v in vars
        ],
    }


# ── List agents ──


@app.get("/api/tenants/{tid}/agents")
def list_agents(tid: str):
    tenant = get_tenant(tid)
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    agents = get_agents(tid)
    return {"tenant_id": tid, "agents": [vars(a) for a in agents]}


# ── Health ──


@app.get("/api/tenants/{tid}/health")
def get_health(tid: str):
    tenant = get_tenant(tid)
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    hc = get_latest_health(tid)
    if not hc:
        return {"tenant_id": tid, "health": None}
    return {"tenant_id": tid, "health": vars(hc)}


@app.post("/api/tenants/{tid}/health")
def post_health(
    tid: str,
    status: str = Query("ok"),
    message: str = Query(""),
):
    tenant = get_tenant(tid)
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    hc = create_health_check(tid, status, message)
    return {"tenant_id": tid, "health": vars(hc)}


# ── Dashboard ──


@app.get("/api/tenants/dashboard")
def dashboard(admin_key: str = Query("")):
    MCP_GATEWAY_URL = os.environ.get("MCP_GATEWAY_URL", "")
    expected = os.environ.get("SDC_ADMIN_KEY", "sdc-admin-secret")
    if admin_key != expected:
        raise HTTPException(403, "Admin access required")
    tenants = get_all_tenants()
    rows = []
    for t in tenants:
        hc = get_latest_health(t.id)
        agents = get_agents(t.id)
        rows.append({
            "id": t.id,
            "name": t.name,
            "plan": t.plan,
            "status": t.status,
            "last_active": t.last_active,
            "health": vars(hc) if hc else None,
            "agents_count": len(agents),
        })
    return {
        "total": len(rows),
        "tenants": rows,
    }


@app.get("/api/tenants/dashboard/nightly-report")
def nightly_report(admin_key: str = Query("")):
    expected = os.environ.get("SDC_ADMIN_KEY", "sdc-admin-secret")
    if admin_key != expected:
        raise HTTPException(403, "Admin access required")
    report = generate_report()
    report["generated_at"] = datetime.now(timezone.utc).isoformat()
    return report


# ── Main ──


def main():
    uvicorn.run(app, host="127.0.0.1", port=8100)


if __name__ == "__main__":
    main()
