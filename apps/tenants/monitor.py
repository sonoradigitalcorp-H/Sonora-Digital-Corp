"""Nightly monitoring and reporting for multi-tenant system."""

import argparse
from datetime import datetime, timezone

from .db import (
    get_all_health_checks,
    get_all_tenants,
    get_latest_health,
    init_db,
)
from .models import HealthStatus


def nightly_check() -> dict:
    init_db()
    tenants = get_all_tenants()
    now = datetime.now(timezone.utc)

    results = []
    for t in tenants:
        hc = get_latest_health(t.id)
        last_active = datetime.fromisoformat(t.last_active)
        hours_since_active = (now - last_active).total_seconds() / 3600

        entry = {
            "tenant_id": t.id,
            "tenant_name": t.name,
            "status": t.status,
            "plan": t.plan,
            "last_active": t.last_active,
            "hours_since_active": round(hours_since_active, 1),
            "last_health": vars(hc) if hc else None,
            "needs_attention": hours_since_active > 48 or (hc and hc.status == HealthStatus.ERROR.value),
        }
        results.append(entry)

    return {
        "check_timestamp": now.isoformat(),
        "tenants_checked": len(results),
        "results": results,
    }


def generate_report() -> dict:
    init_db()
    tenants = get_all_tenants()
    now = datetime.now(timezone.utc)

    total = len(tenants)
    active = sum(1 for t in tenants if t.status == "active")
    inactive = sum(1 for t in tenants if t.status == "inactive")
    trial = sum(1 for t in tenants if t.status == "trial")

    healthy = 0
    warnings = 0
    errors = 0
    no_health = 0
    health_details = []

    for t in tenants:
        hc = get_latest_health(t.id)
        if hc is None:
            no_health += 1
            health_details.append({"tenant_id": t.id, "name": t.name, "status": "no_data"})
        elif hc.status == "ok":
            healthy += 1
            health_details.append({"tenant_id": t.id, "name": t.name, "status": "ok", "last_check": hc.timestamp})
        elif hc.status == "warning":
            warnings += 1
            health_details.append({"tenant_id": t.id, "name": t.name, "status": "warning", "last_check": hc.timestamp, "message": hc.message})
        else:
            errors += 1
            health_details.append({"tenant_id": t.id, "name": t.name, "status": "error", "last_check": hc.timestamp, "message": hc.message})

    return {
        "generated_at": now.isoformat(),
        "summary": {
            "total_tenants": total,
            "active": active,
            "inactive": inactive,
            "trial": trial,
        },
        "health": {
            "healthy": healthy,
            "warnings": warnings,
            "errors": errors,
            "no_data": no_health,
        },
        "details": health_details,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SDC Tenants Monitor")
    parser.add_argument("--report", action="store_true", help="Generate nightly report")
    args = parser.parse_args()

    if args.report:
        import json
        report = generate_report()
        print(json.dumps(report, indent=2))
    else:
        result = nightly_check()
        import json
        print(json.dumps(result, indent=2))
