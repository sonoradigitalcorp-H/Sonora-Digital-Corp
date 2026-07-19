#!/usr/bin/env python3
"""System Catalog — Genera el mapa completo del sistema Sonora OS.

Escanea el repositorio y produce state/system-catalog.yaml con:
  - skills (completas, por fuente, por estado)
  - products (con API, frontend, tests)
  - services (MCP servers, systemd, docker, puertos)
  - agents (registry, ADK, opencode subagents)
  - events (catalogo de eventos)
  - ADRs (activos, completados, faltantes)
  - health (estado de servicios en VPS)

Uso: python3 scripts/generate-catalog.py
      python3 scripts/generate-catalog.py --watch  # cada 60s
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent


# ─── Helpers ───────────────────────────────────────────────────────────

def _count_skills() -> dict:
    skills_dir = REPO / "skills"
    all_skills = []
    complete = 0
    by_source = {}
    sections = [
        "Business Objective", "Inputs (Gherkin)", "Outputs (Gherkin)",
        "Events", "Dependencies", "Tools", "Policies",
        "Success Metrics", "Failure Conditions", "Recovery Procedure",
        "Business Value", "Parent OS", "Version", "Audit Trail",
    ]

    for f in sorted(skills_dir.rglob("*")):
        if f.is_file() and f.suffix == ".md" and "SKILL-TEMPLATE" not in f.name:
            name = f.name.replace(".skill.md", "").replace("SKILL.md", f.parent.name)
            content = f.read_text()
            present = sum(1 for s in sections if s in content)
            complete += 1 if present == 14 else 0

            src = "sdc"
            if "hermes-" in f.name:
                src = "hermes"
            elif "openclaw-" in f.name:
                src = "openclaw"
            elif f.parent.name in ("process",):
                src = "process"
            by_source[src] = by_source.get(src, 0) + 1
            all_skills.append(name)

    return {
        "total": len(all_skills),
        "complete_14_fields": complete,
        "incomplete": len(all_skills) - complete,
        "by_source": by_source,
        "names": all_skills,
    }


def _count_products() -> dict:
    products_dir = REPO / "products"
    products = []
    for d in sorted(products_dir.iterdir()):
        if d.is_dir():
            has_api = (d / "main.py").exists()
            has_frontend = (d / "frontend").exists() or (d / "templates").exists()
            has_tests = (d / "tests").exists()
            port = None
            if has_api:
                content = (d / "main.py").read_text()
                m = re.search(r'port\s*[:=]\s*(\d{4,5})', content)
                if m:
                    port = int(m.group(1))
            products.append({
                "name": d.name,
                "has_api": has_api,
                "has_frontend": has_frontend,
                "has_tests": has_tests,
                "port": port,
            })
    with_frontend = [p["name"] for p in products if p["has_frontend"]]
    without_frontend = [p["name"] for p in products if p["has_api"] and not p["has_frontend"]]
    return {
        "total": len(products),
        "with_api": [p for p in products if p["has_api"]],
        "with_frontend": with_frontend,
        "without_frontend": without_frontend,
        "all": products,
    }


def _count_services() -> dict:
    mcp_servers = list((REPO / "mcp" / "servers").glob("*_mcp.py"))
    adk_agents = list((REPO / "mcp" / "adk" / "agents").glob("*.yaml"))
    systemd_files = list((REPO / "infra" / "systemd").glob("*.service"))

    ports = set()
    for py_file in list(Path(REPO).rglob("main.py"))[:50]:
        sp = str(py_file)
        if "venv" not in sp and "node_modules" not in sp and ".opencode" not in sp:
            try:
                content = py_file.read_text()
                for m in re.finditer(r'port\s*[:=]\s*(\d{4,5})', content):
                    ports.add(int(m.group(1)))
            except Exception:
                pass

    return {
        "mcp_servers": len(mcp_servers),
        "mcp_server_names": [f.name for f in mcp_servers],
        "adk_agents": len(adk_agents),
        "systemd_services": len(systemd_files),
        "systemd_names": [f.stem for f in systemd_files],
        "ports_found": sorted(ports),
    }


def _count_agents() -> dict:
    registry_file = REPO / "agents" / "registry.yaml"
    registry_agents = []
    if registry_file.exists():
        with open(registry_file) as f:
            data = yaml.safe_load(f)
            registry_agents = [a.get("name", "") for a in data.get("agents", [])]

    opencode_file = REPO / "opencode.json"
    opencode_agents = []
    if opencode_file.exists():
        with open(opencode_file) as f:
            data = json.load(f)
            opencode_agents = list(data.get("agent", {}).keys())

    return {
        "registry_agents": len(registry_agents),
        "registry_names": registry_agents,
        "opencode_subagents": len(opencode_agents),
        "opencode_names": opencode_agents,
    }


def _count_events() -> dict:
    catalog_file = REPO / "state" / "events" / "catalog.yaml"
    if not catalog_file.exists():
        return {"total": 0}

    with open(catalog_file) as f:
        data = yaml.safe_load(f)

    categories = data.get("categories", {})
    total = sum(len(v) if isinstance(v, list) else 0 for v in categories.values())
    return {
        "total_events": total,
        "total_categories": len(categories),
        "catalog_version": data.get("version"),
    }


def _count_adrs() -> dict:
    active = list((REPO / "process" / "active").glob("ADR-*.md"))
    completed = []
    completed_dir = REPO / "process" / "completed"
    if completed_dir.exists():
        for d in completed_dir.iterdir():
            for f in d.glob("ADR*.md"):
                completed.append(f)

    return {
        "active": len(active),
        "active_names": sorted([f.stem for f in active]),
        "completed": len(completed),
    }


def _get_git_info() -> dict:
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5, cwd=REPO,
        ).stdout.strip()
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5, cwd=REPO,
        ).stdout.strip()[:12]
        return {"branch": branch, "commit": commit}
    except Exception:
        return {"branch": "unknown", "commit": "unknown"}


def _check_vps_health() -> dict:
    services = {name: "unknown" for name in ["notifier", "tracker", "affiliates", "adk_bridge", "dashboard"]}
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=2", "-o", "StrictHostKeyChecking=no",
             "-o", "BatchMode=yes", "ubuntu@149.56.46.173",
             "echo notifier:$(curl -so /dev/null -w '%{http_code}' http://localhost:6200/notifier/health 2>/dev/null || echo '000'); "
             "echo tracker:$(curl -so /dev/null -w '%{http_code}' http://localhost:6300/tracker/health 2>/dev/null || echo '000'); "
             "echo affiliates:$(curl -so /dev/null -w '%{http_code}' http://localhost:6400/affiliates/health 2>/dev/null || echo '000'); "
             "echo adk:$(curl -so /dev/null -w '%{http_code}' http://localhost:6401/adk/health 2>/dev/null || echo '000')"],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.strip().split("\n"):
            if ":" in line:
                name, code = line.split(":", 1)
                services[name] = "online" if code == "200" else "offline"
    except Exception:
        pass
    return services


def generate_catalog() -> dict:
    git = _get_git_info()
    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "commit": git["commit"],
        "branch": git["branch"],
        "skills": _count_skills(),
        "products": _count_products(),
        "services": _count_services(),
        "agents": _count_agents(),
        "events": _count_events(),
        "adrs": _count_adrs(),
        "health_vps": _check_vps_health(),
    }
    return catalog


def save_catalog(catalog: dict):
    output_path = REPO / "state" / "system-catalog.yaml"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        yaml.dump(catalog, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    print(f"✅ System Catalog generado: {output_path}")
    print(f"   Skills: {catalog['skills']['total']} ({catalog['skills']['complete_14_fields']} completas)")
    print(f"   Products: {catalog['products']['total']} ({len(catalog['products']['without_frontend'])} sin frontend)")
    print(f"   Services: {catalog['services']['mcp_servers']} MCP, {catalog['services']['systemd_services']} systemd")
    print(f"   Agents: {catalog['agents']['registry_agents']} registry + {catalog['agents']['opencode_subagents']} opencode")
    print(f"   ADRs: {catalog['adrs']['active']} activos, {catalog['adrs']['completed']} completados")
    vps = catalog.get("health_vps", {})
    online = sum(1 for v in vps.values() if v == "online")
    print(f"   VPS health: {online}/{len(vps)} servicios online")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="System Catalog Generator")
    parser.add_argument("--watch", action="store_true", help="Regenerate every 60s")
    args = parser.parse_args()

    if args.watch:
        while True:
            catalog = generate_catalog()
            save_catalog(catalog)
            time.sleep(60)
    else:
        catalog = generate_catalog()
        save_catalog(catalog)


if __name__ == "__main__":
    main()
