#!/usr/bin/env python3
"""Founder Dependency Index — Mide qué tan dependiente es el sistema del fundador.

Métricas:
  - % de sesiones que requirieron intervención manual del fundador
  - % de tareas que el sistema ejecutó autónomamente
  - Cantidad de decisiones que tomó el fundador vs el sistema
  - Cantidad de comandos "/" (automáticos) vs instrucciones libres (manuales)
  - Score 0-100 (100 = fully autonomous)
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent
COMPLETED_DIR = REPO / "process" / "completed"
MEMORY_LEARNING_DIR = REPO / "memory" / "learning"
SCRIPTS_DIR = REPO / "scripts"


def count_manual_interventions_in_session(session_dir: Path) -> dict:
    manual = 0
    auto = 0
    total = 0

    leccion_file = session_dir / "LECCION.md"
    if leccion_file.exists():
        text = leccion_file.read_text()
        fallos = re.findall(r"-\s*\*\*.*?\*\*", text)
        manual += len(fallos)

    spec_file = session_dir / "SPEC.md"
    if spec_file.exists():
        text = spec_file.read_text()
        auto_commands = len(re.findall(r"/[a-z]+", text))
        auto += auto_commands

    events_file = session_dir / "events.jsonl"
    if events_file.exists():
        with open(events_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    total += 1
                    if "manual" in line.lower() or "founder" in line.lower():
                        manual += 1
                    else:
                        auto += 1

    return {"manual": manual, "auto": auto, "total": total}


def count_slash_commands_in_agents_md() -> dict:
    agents_md = REPO / "AGENTS.md"
    if not agents_md.exists():
        return {"slash_commands": 0, "auto_commands": []}
    text = agents_md.read_text()
    commands = re.findall(r"`/([a-z\-]+)`", text)
    return {"slash_commands": len(commands), "auto_commands": commands}


def count_scripts() -> dict:
    if not SCRIPTS_DIR.exists():
        return {"total": 0, "automated": 0}
    total = len([f for f in SCRIPTS_DIR.iterdir() if f.is_file() and f.name.endswith((".py", ".sh"))])
    cron_scripts = len(list(SCRIPTS_DIR.glob("*-cron*"))) + len(list(SCRIPTS_DIR.glob("cron*")))
    return {"total": total, "cron_automated": cron_scripts}


def compute_index() -> dict:
    sessions_analyzed = 0
    total_manual = 0
    total_auto = 0

    if COMPLETED_DIR.exists():
        for session_dir in sorted(COMPLETED_DIR.iterdir()):
            if not session_dir.is_dir():
                continue
            stats = count_manual_interventions_in_session(session_dir)
            if stats["total"] > 0 or stats["manual"] > 0 or stats["auto"] > 0:
                total_manual += stats["manual"]
                total_auto += stats["auto"]
                sessions_analyzed += 1

    scripts_info = count_scripts()
    commands_info = count_slash_commands_in_agents_md()

    total_ops = total_manual + total_auto
    autonomy_rate = (total_auto / total_ops * 100) if total_ops > 0 else 0
    manual_rate = (total_manual / total_ops * 100) if total_ops > 0 else 0

    # Score: 70% autonomy rate + 15% script automation + 15% commands coverage
    autonomy_score = autonomy_rate * 0.70
    script_score = min(100, scripts_info["cron_automated"] * 10) * 0.15
    command_score = min(100, commands_info["slash_commands"] * 2) * 0.15
    overall = min(100, round(autonomy_score + script_score + command_score))

    return {
        "founder_dependency_index": 100 - overall,
        "autonomy_score": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": {
            "sessions_analyzed": sessions_analyzed,
            "total_manual_events": total_manual,
            "total_auto_events": total_auto,
            "autonomy_rate_pct": round(autonomy_rate, 1),
            "manual_rate_pct": round(manual_rate, 1),
        },
        "components": {
            "autonomy_rate_weighted": round(autonomy_score, 1),
            "script_automation": round(script_score, 1),
            "commands_coverage": round(command_score, 1),
        },
        "scripts": scripts_info,
        "commands": commands_info,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Founder Dependency Index")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = compute_index()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n=== Founder Dependency Index ===")
        print(f"Score: {result['autonomy_score']}/100 (0=dependent, 100=autonomous)")
        print(f"Founder Dependency: {result['founder_dependency_index']}%")
        print(f"\nSessions analyzed: {result['details']['sessions_analyzed']}")
        print(f"Auto events: {result['details']['total_auto_events']} | Manual: {result['details']['total_manual_events']}")
        print(f"Autonomy rate: {result['details']['autonomy_rate_pct']}%")
        print(f"\nComponents:")
        for k, v in result['components'].items():
            print(f"  {k}: {v}")
        print(f"\nScripts: {result['scripts']['total']} total, {result['scripts']['cron_automated']} cron-automated")
        print(f"Slash commands: {result['commands']['slash_commands']}")


if __name__ == "__main__":
    main()
