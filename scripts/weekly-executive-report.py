#!/usr/bin/env python3
"""Weekly Executive Report — Genera 11 reportes automáticamente.

Basado en OMEGA-PROMPT: Revenue, Customer, Capability, Agent, Automation,
Risk, Technical Debt, Founder Dependency, Knowledge Growth, Kill, Scale.

Uso: python3 scripts/weekly-executive-report.py [--json] [--output DIR]
"""

import json
import logging
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent


def report_revenue() -> dict:
    return {
        "title": "Revenue Report",
        "generated": datetime.now(timezone.utc).isoformat(),
        "period": "weekly",
        "artists": [
            {"name": "Hector Rubio", "streams": 115093009, "revenue": 460372},
            {"name": "Jesus Urquijo", "streams": 4635222, "revenue": 18540},
            {"name": "Javier Arvayo", "streams": 50000, "revenue": 200},
        ],
        "total_revenue": 479112,
        "note": "100% Spotify. Oplaai no paga multi-plataforma.",
    }


def report_customers() -> dict:
    return {
        "title": "Customer Report",
        "clients": [
            {"name": "ABE Music (Abraham Ortega)", "status": "active", "product": "ABE Music OS"},
            {"name": "Alejandro Zamora Recording", "status": "active", "product": "AZREC landing"},
        ],
        "total_clients": 2,
    }


def report_capabilities() -> dict:
    from capabilities.bus.router import load_registry
    registry = load_registry()
    caps = registry.get("capabilities", [])
    active = [c for c in caps if c.get("status") == "active"]
    experimental = [c for c in caps if c.get("status") == "experimental"]
    return {
        "title": "Capability Report",
        "total": len(caps),
        "active": len(active),
        "experimental": len(experimental),
        "list": caps,
    }


def report_agents() -> dict:
    agents_dir = REPO / "agents"
    if agents_dir.exists():
        total = len(list(agents_dir.glob("*.yaml")))
    else:
        total = 0
    adk_dir = REPO / "mcp" / "adk" / "agents"
    adk_total = len(list(adk_dir.glob("*.yaml"))) if adk_dir.exists() else 0
    return {
        "title": "Agent Report",
        "registry_agents": total,
        "adk_agents": adk_total,
        "total": total + adk_total,
    }


def report_automation() -> dict:
    scripts = list(REPO.glob("scripts/*.sh")) + list(REPO.glob("scripts/*.py"))
    cron = [s for s in scripts if "cron" in s.name]
    total_tests = 0
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no", "--collect-only"],
            capture_output=True, text=True, timeout=30, cwd=str(REPO),
        )
        import re
        total_tests = sum(int(m) for m in re.findall(r'(\d+) collected', result.stdout + result.stderr) or [0])
    except Exception:
        pass
    return {
        "title": "Automation Report",
        "scripts_total": len(scripts),
        "cron_jobs": len(cron),
        "automated_tests": total_tests,
    }


def report_risk() -> dict:
    return {
        "title": "Risk Report",
        "risks": [
            {"name": "Single VPS", "severity": "high", "mitigation": "Backup cron diario + recovery manual"},
            {"name": "No multi-tenancy", "severity": "medium", "mitigation": "HAS-011 planned"},
            {"name": "SSH key single-point", "severity": "medium", "mitigation": "HTTPS token backup"},
        ],
        "overall_risk": "medium",
    }


def report_tech_debt() -> dict:
    return {
        "title": "Technical Debt Report",
        "items": [
            {"area": "apps/observe/", "debt": "resolved", "note": "Now implemented"},
            {"area": "apps/understand/", "debt": "resolved", "note": "Now implemented"},
            {"area": "apps/control/", "debt": "resolved", "note": "Now implemented"},
            {"area": "apps/agents/hermes_client.py", "debt": "partial", "note": "Re-export from act"},
            {"area": "apps/learning/", "debt": "duplicate", "note": "Merge with apps/learn/"},
        ],
        "estimated_hours_to_clear": 4,
    }


def report_founder_dependency() -> dict:
    try:
        from metrics.founder_dependency import compute_index
        return {"title": "Founder Dependency Report", **compute_index()}
    except Exception as e:
        return {"title": "Founder Dependency Report", "error": str(e)}


def report_knowledge_growth() -> dict:
    completed = list(REPO.glob("process/completed/*"))
    lecciones = list(REPO.glob("process/completed/*/LECCION.md"))
    docs = list(REPO.glob("docs/*.md"))
    return {
        "title": "Knowledge Growth Report",
        "total_sessions": len(completed),
        "sessions_with_lessons": len(lecciones),
        "doc_files": len(docs),
    }


def report_kill() -> dict:
    return {
        "title": "Kill/Scale Report",
        "recommendations": [
            {"item": "apps/learning/", "action": "KILL", "reason": "Duplicate of apps/learn/"},
            {"item": "apps/agent_metrics/", "action": "KILL", "reason": "Absorbed by measure/scoreboard"},
            {"item": "Capability Bus", "action": "SCALE", "reason": "New, needs adoption"},
        ],
    }


def report_scale() -> dict:
    return {
        "title": "Scale Report",
        "scale_candidates": [
            {"item": "Content Studio", "potential": "high", "next_step": "Multi-tenant MCP tools"},
            {"item": "OmniVoice", "potential": "high", "next_step": "API marketplace"},
            {"item": "Capability Bus", "potential": "medium", "next_step": "Adopt across all products"},
        ],
    }


def generate_all_reports() -> dict:
    reports = {
        "revenue": report_revenue(),
        "customers": report_customers(),
        "capabilities": report_capabilities(),
        "agents": report_agents(),
        "automation": report_automation(),
        "risk": report_risk(),
        "tech_debt": report_tech_debt(),
        "founder_dependency": report_founder_dependency(),
        "knowledge_growth": report_knowledge_growth(),
        "kill": report_kill(),
        "scale": report_scale(),
    }
    return {
        "report_id": f"WER-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        "generated": datetime.now(timezone.utc).isoformat(),
        "period": "weekly",
        "reports": reports,
        "report_count": len(reports),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Weekly Executive Reports")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--output", help="Output directory (default: stdout)")
    args = parser.parse_args()

    all_reports = generate_all_reports()

    if args.json:
        output = json.dumps(all_reports, indent=2)
        if args.output:
            out_dir = Path(args.output)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"WER-{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
            out_file.write_text(output)
            print(f"Written to {out_file}")
        else:
            print(output)
    else:
        print(f"\n{'='*60}")
        print(f"WEEKLY EXECUTIVE REPORT")
        print(f"{all_reports['report_id']} | {all_reports['generated']}")
        print(f"{'='*60}")
        for name, report in all_reports["reports"].items():
            print(f"\n--- {report['title']} ---")
            for k, v in report.items():
                if k in ("title",):
                    continue
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict):
                            print(f"  • {item.get('name', item.get('item', ''))}")
                        else:
                            print(f"  • {item}")
                elif isinstance(v, (int, float, str)):
                    print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
