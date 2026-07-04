"""Agent Scoreboard — métricas por agente: accuracy, latency, cost, deploys, tests [FR8-FR10]"""
import json
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
ECO_DB = REPO / "state" / "economics.db"
VIOLATIONS = REPO / "state" / "quality" / "violations.jsonl"


def get_economics():
    """Lee datos de economics.db"""
    if not ECO_DB.exists():
        return {}
    conn = sqlite3.connect(str(ECO_DB))
    rows = conn.execute(
        "SELECT agent, operation, model, tokens_input, tokens_output, latency_ms, cost_usd, timestamp "
        "FROM operations ORDER BY timestamp DESC LIMIT 1000"
    ).fetchall()
    conn.close()

    agents = defaultdict(lambda: {
        "operations": 0, "total_tokens": 0, "total_cost": 0.0,
        "total_latency_ms": 0, "models_used": set(), "last_seen": None
    })

    for r in rows:
        a = r[0]
        agents[a]["operations"] += 1
        agents[a]["total_tokens"] += r[3] + r[4]
        agents[a]["total_cost"] += r[6]
        agents[a]["total_latency_ms"] += r[5]
        if r[2]:
            agents[a]["models_used"].add(r[2])
        if not agents[a]["last_seen"] or r[7] > agents[a]["last_seen"]:
            agents[a]["last_seen"] = r[7]

    return dict(agents)


def get_violations():
    """Lee violaciones por agente"""
    if not VIOLATIONS.exists():
        return defaultdict(int)
    counts = defaultdict(int)
    with open(VIOLATIONS) as f:
        for line in f:
            try:
                v = json.loads(line)
                agent = v.get("source", {}).get("agent", "unknown")
                counts[agent] += 1
            except json.JSONDecodeError:
                pass
    return dict(counts)


def get_agent_registry():
    """Lee agent registry"""
    registry_file = REPO / "agents" / "registry.yaml"
    if not registry_file.exists():
        return []
    import yaml
    with open(registry_file) as f:
        data = yaml.safe_load(f)
    return {a["name"]: a for a in data.get("agents", [])}


def compute_scoreboard():
    """Calcula scoreboard completo"""
    economics = get_economics()
    violations = get_violations()
    registry = get_agent_registry()
    all_agents = set(list(economics.keys()) + list(registry.keys()) + ["mystic", "hermes", "builder", "auditor", "reviewer", "devops", "sales", "process-doc"])

    scoreboard = []
    for agent in sorted(all_agents):
        eco = economics.get(agent, {})
        reg = registry.get(agent, {})
        v_count = violations.get(agent, 0)

        ops = eco.get("operations", 0)
        avg_latency = (eco.get("total_latency_ms", 0) / ops) if ops > 0 else 0
        avg_cost = (eco.get("total_cost", 0) / ops) if ops > 0 else 0

        scoreboard.append({
            "agent": agent,
            "role": reg.get("role", "unknown"),
            "level": reg.get("level", "?"),
            "status": reg.get("status", "unknown"),
            "operations": ops,
            "total_cost_usd": round(eco.get("total_cost", 0), 4),
            "avg_latency_ms": round(avg_latency, 0),
            "avg_cost_per_op": round(avg_cost, 6),
            "total_tokens": eco.get("total_tokens", 0),
            "models_used": list(eco.get("models_used", [])),
            "violations": v_count,
            "last_seen": eco.get("last_seen", "never"),
        })

    return scoreboard


def to_html(scoreboard):
    """Genera HTML del scoreboard"""
    rows = ""
    colors = {"active": "#27ae60", "unknown": "#f39c12", "inactive": "#e74c3c"}
    for a in scoreboard:
        color = colors.get(a["status"], "#95a5a6")
        rows += f"""
        <tr>
            <td><strong>{a["agent"]}</strong></td>
            <td>{a["role"]}</td>
            <td>{a["level"]}</td>
            <td><span style="color:{color}">●</span> {a["status"]}</td>
            <td>{a["operations"]}</td>
            <td>${a["total_cost_usd"]}</td>
            <td>{a["avg_cost_per_op"]}</td>
            <td>{a["avg_latency_ms"]}ms</td>
            <td>{a["total_tokens"]}</td>
            <td>{", ".join(a["models_used"][:3]) if a["models_used"] else "—"}</td>
            <td>{a["violations"]}</td>
            <td>{a["last_seen"][:16] if a["last_seen"] != "never" else "—"}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><title>Agent Scoreboard</title>
<style>
body {{ font-family: monospace; background: #1a1a2e; color: #eee; padding: 20px; }}
h1 {{ color: #0f0; }}
table {{ border-collapse: collapse; width: 100%; }}
th {{ background: #16213e; color: #0f0; padding: 10px; text-align: left; }}
td {{ padding: 8px; border-bottom: 1px solid #333; }}
tr:hover {{ background: #16213e; }}
.green {{ color: #27ae60; }}
.red {{ color: #e74c3c; }}
</style></head>
<body>
<h1>🤖 Agent Scoreboard</h1>
<p>Updated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
<table>
<tr><th>Agent</th><th>Role</th><th>Lvl</th><th>Status</th><th>Ops</th><th>Cost</th><th>Avg $/op</th><th>Latency</th><th>Tokens</th><th>Models</th><th>Violations</th><th>Last Seen</th></tr>
{rows}
</table>
</body></html>"""


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Agent Scoreboard")
    parser.add_argument("--html", "-o", help="Output HTML file")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    scoreboard = compute_scoreboard()

    if args.html:
        html = to_html(scoreboard)
        Path(args.html).write_text(html)
        print(f"Scoreboard written to {args.html}")
    elif args.json:
        print(json.dumps(scoreboard, indent=2, default=str))
    else:
        print(f"{'Agent':15s} {'Role':20s} {'Ops':>5s} {'Cost':>10s} {'Latency':>10s} {'Status':10s}")
        print("-" * 75)
        for a in scoreboard:
            print(f"{a['agent']:15s} {a['role']:20s} {a['operations']:5d} ${a['total_cost_usd']:<8.2f} {a['avg_latency_ms']:>8.0f}ms {a['status']:10s}")
