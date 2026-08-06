#!/usr/bin/env python3
"""Config Unification — fleet.yml genera configs de servicios + truth/40-infrastructure.yaml [FR11-FR13]"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
FLEET = REPO / "fleet.yml"
INFRA_TRUTH = REPO / "truth" / "40-infrastructure.yaml"
OUTPUT_DIR = REPO / "config" / "generated"


def load_fleet():
    if not FLEET.exists():
        print(f"ERROR: {FLEET} not found", file=sys.stderr)
        sys.exit(1)
    with open(FLEET) as f:
        return yaml.safe_load(f)


def generate_service_list(fleet):
    """Genera lista de servicios desde fleet.yml"""
    services = []
    for svc in fleet.get("services", []):
        entry = {
            "name": svc["name"],
            "port": svc.get("port"),
            "bind": svc.get("bind", "127.0.0.1"),
            "protocol": svc.get("protocol", "tcp"),
            "machine": svc.get("machine", "sdc-prod"),
        }
        if svc.get("docker"):
            entry["type"] = "docker"
        if svc.get("systemd"):
            entry["type"] = "systemd"
        if svc.get("proxy"):
            entry["proxy"] = True
            entry["proxy_domain"] = svc.get("proxy_domain", "")
        services.append(entry)
    return services


def generate_health_check_config(fleet):
    """Genera config de health checks desde fleet.yml"""
    targets = fleet.get("health", {}).get("blackbox_targets", [])
    return {
        "check_interval": fleet.get("health", {}).get("check_interval", 60),
        "alerts": fleet.get("health", {}).get("alerts", "telegram"),
        "targets": targets
    }


def generate_nginx_upstreams(fleet):
    """Genera bloques de upstream para nginx"""
    upstreams = []
    for svc in fleet.get("services", []):
        if svc.get("proxy"):
            domain = svc.get("proxy_domain", "")
            port = svc.get("port", "")
            upstreams.append({
                "domain": domain,
                "upstream": f"{svc['name']}",
                "server": f"127.0.0.1:{port}"
            })
    return upstreams


def update_infrastructure_truth(fleet, services):
    """Actualiza truth/40-infrastructure.yaml con datos de fleet.yml"""
    data = {
        "version": 1,
        "domain": "infrastructure",
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "description": "Infraestructura actualizada automáticamente desde fleet.yml",
        "rules": [
            {
                "id": "INFRA-001",
                "description": "fleet.yml es la única fuente de verdad de infraestructura",
                "category": "configuration",
                "severity": "error",
                "applies_to": ["all_agents"],
                "enforcement": "automated"
            }
        ],
        "machines": fleet.get("machines", {}),
        "networking": fleet.get("networking", {}),
        "services": services,
        "generated_from": "fleet.yml",
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    with open(INFRA_TRUTH, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    return len(services)


def generate_all():
    """Genera todas las configuraciones desde fleet.yml"""
    fleet = load_fleet()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Service list
    services = generate_service_list(fleet)
    svc_file = OUTPUT_DIR / "services.json"
    with open(svc_file, "w") as f:
        json.dump(services, f, indent=2)
    print(f"Generated: {svc_file} ({len(services)} services)", file=sys.stderr)

    # 2. Health check config
    health = generate_health_check_config(fleet)
    health_file = OUTPUT_DIR / "health.json"
    with open(health_file, "w") as f:
        json.dump(health, f, indent=2)
    print(f"Generated: {health_file} ({len(health['targets'])} targets)", file=sys.stderr)

    # 3. Nginx upstreams
    upstreams = generate_nginx_upstreams(fleet)
    up_file = OUTPUT_DIR / "nginx-upstreams.json"
    with open(up_file, "w") as f:
        json.dump(upstreams, f, indent=2)
    print(f"Generated: {up_file} ({len(upstreams)} upstreams)", file=sys.stderr)

    # 4. Update truth/40-infrastructure.yaml
    n = update_infrastructure_truth(fleet, services)
    print(f"Updated: {INFRA_TRUTH} ({n} services)", file=sys.stderr)

    # Emit event
    try:
        import subprocess
        subprocess.run(
            [sys.executable, str(REPO / "scripts" / "emit-event.py"),
             "--event", "knowledge.indexed",
             "--kernel", "infrastructure",
             "--agent", "generate-configs",
             "--subject-type", "config",
             "--subject-id", "fleet.yml",
             "--payload", json.dumps({
                 "services": len(services),
                 "health_targets": len(health["targets"]),
                 "upstreams": len(upstreams)
             })],
            capture_output=True, timeout=5
        )
    except Exception:
        pass

    return {"services": len(services), "health_targets": len(health["targets"]), "upstreams": len(upstreams)}


if __name__ == "__main__":
    result = generate_all()
    print(json.dumps(result))
