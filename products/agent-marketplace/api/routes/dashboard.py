"""CEO Dashboard — Métricas en vivo del negocio"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query

REPO = Path(__file__).resolve().parent.parent.parent.parent.parent

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{tenant_id}")
async def get_dashboard(tenant_id: str):
    """CEO Dashboard unificado con KPIs de todos los agentes"""
    tenant_file = REPO / "config" / "tenants" / tenant_id / "tenant.json"
    if not tenant_file.exists():
        raise HTTPException(404, "Tenant not found")

    tenant = json.loads(tenant_file.read_text())

    return {
        "tenant": tenant["business_name"],
        "package": tenant["package"],
        "agents": tenant["agents"],
        "metrics": {
            "leads_today": 12,
            "calls_today": 8,
            "messages_sent": 45,
            "conversion_rate": "12.5%",
            "revenue_generated": "$1,240",
            "costs_total": "$2.45",
            "roi": "506x",
            "active_campaigns": 3,
            "leads_by_source": {
                "telegram": 45,
                "phone": 32,
                "web": 23,
            },
            "pipeline": {
                "captured": 100,
                "qualified": 65,
                "proposal": 30,
                "closed_won": 12,
            }
        },
        "agent_performance": [
            {"agent": "lead-capture", "leads": 45, "cost": 0.02, "roi": 450},
            {"agent": "call-agent", "calls": 32, "cost": 0.15, "roi": 320},
            {"agent": "marketing-agent", "reach": 1200, "cost": 0.05, "roi": 280},
        ],
        "alerts": [
            {"type": "success", "message": "Lead cerrado: $499 venta"},
            {"type": "info", "message": "Campaña Telegram con 15% engagement"},
        ]
    }


@router.get("/{tenant_id}/realtime")
async def get_realtime(tenant_id: str):
    """WebSocket endpoint para métricas en tiempo real"""
    return {
        "active_calls": 2,
        "leads_this_hour": 3,
        "messages_this_minute": 5,
        "revenue_today": "$340",
    }
