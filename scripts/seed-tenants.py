#!/usr/bin/env python3
"""Seed the multi-tenant database with 3 demo tenants."""

import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apps.tenants.db import (
    create_agent,
    create_health_check,
    create_tenant,
    get_all_tenants,
    init_db,
    set_env_vars,
)
from apps.tenants.models import AgentType, HealthStatus

init_db()

demo_tenants = [
    {
        "name": "ABE Music",
        "email": "abe@sonora.digital",
        "plan": "enterprise",
        "agents": [
            {"type": "voice", "clients_count": 45, "hours_worked": 320, "clients_helped": 180},
            {"type": "crm", "clients_count": 45, "hours_worked": 120, "clients_helped": 90},
            {"type": "sales", "clients_count": 45, "hours_worked": 80, "clients_helped": 200},
        ],
        "healths": [
            ("ok", "All systems operational", {"uptime": 99.9, "agents_active": 3}),
            ("ok", "Routine maintenance completed", {"uptime": 99.8, "agents_active": 3}),
            ("ok", "Voice agent processed 45 requests", {"uptime": 100.0, "agents_active": 3}),
        ],
    },
    {
        "name": "Alejandro Zamora Recording",
        "email": "azrec@sonora.digital",
        "plan": "medium",
        "agents": [
            {"type": "voice", "clients_count": 12, "hours_worked": 95, "clients_helped": 48},
            {"type": "support", "clients_count": 12, "hours_worked": 40, "clients_helped": 60},
        ],
        "healths": [
            ("ok", "Studio booking system online", {"uptime": 99.5, "agents_active": 2}),
            ("warning", "High memory usage detected on voice agent", {"uptime": 98.2, "agents_active": 2, "memory_pct": 87}),
            ("ok", "Memory optimized after restart", {"uptime": 100.0, "agents_active": 2}),
        ],
    },
    {
        "name": "El Joyero",
        "email": "joyero@sonora.digital",
        "plan": "small",
        "agents": [
            {"type": "crm", "clients_count": 3, "hours_worked": 15, "clients_helped": 8},
        ],
        "healths": [
            ("ok", "CRM agent initialized", {"uptime": 100.0, "agents_active": 1}),
            ("error", "CRM agent unreachable for 2 hours", {"uptime": 89.5, "agents_active": 0, "downtime_min": 120}),
            ("ok", "Agent recovered after restart", {"uptime": 99.0, "agents_active": 1}),
        ],
    },
]

created = []

for demo in demo_tenants:
    t = create_tenant(demo["name"], demo["email"], demo["plan"])
    envs = [
        ("MCP_GATEWAY_URL", "http://localhost:8000", False),
        ("API_KEY", t.api_key, True),
        ("AGENT_CONFIG", json.dumps({"tenant_id": t.id, "plan": demo["plan"]}), True),
        ("WEBHOOK_TOKEN", t.webhook_token, True),
        ("TENANT_ID", t.id, False),
        ("TENANT_NAME", demo["name"], False),
    ]
    set_env_vars(t.id, envs)

    for ad in demo["agents"]:
        agent = create_agent(t.id, ad["type"], {"auto_scale": True})
        created.append(agent)

    for status, message, metrics in demo["healths"]:
        create_health_check(t.id, status, message, metrics)

    created.append(t)

print(f"✅ Seeded {len(demo_tenants)} tenants with {len(created) - len(demo_tenants)} agents and {sum(len(d['healths']) for d in demo_tenants)} health checks.")
for t in get_all_tenants():
    print(f"  • {t.name:<35} plan={t.plan:<10} status={t.status}")
