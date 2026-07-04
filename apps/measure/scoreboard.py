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
    """Genera HTML del scoreboard con sorting, filtros, y sparklines"""
    colors = {"active": "#27ae60", "unknown": "#f39c12", "inactive": "#e74c3c"}

    def sparkline(ops):
        if ops == 0:
            return "<span style='color:#555'>—</span>"
        bars = min(ops, 10)
        return " ".join(f"<span style='display:inline-block;width:4px;height:{4+(i%3)*2}px;background:#27ae60;margin:0 1px'></span>" for i in range(bars))

    def badge(count):
        if count == 0:
            return "<span style='color:#555'>0</span>"
        return f"<span style='background:#e74c3c;color:#fff;padding:2px 6px;border-radius:8px;font-size:11px'>{count}</span>"

    def status_dot(status):
        c = colors.get(status, "#95a5a6")
        return f"<span style='color:{c};font-size:18px'>●</span>"

    rows_html = ""
    for a in scoreboard:
        rows_html += f"""
        <tr>
            <td><strong>{a["agent"]}</strong></td>
            <td style='color:#888'>{a["role"]}</td>
            <td>{a["level"]}</td>
            <td>{status_dot(a["status"])} {a["status"]}</td>
            <td>{a["operations"]}</td>
            <td>${a["total_cost_usd"]}</td>
            <td>{a["avg_cost_per_op"]}</td>
            <td>{a["avg_latency_ms"]}ms</td>
            <td>{a["total_tokens"]}</td>
            <td>{", ".join(a["models_used"][:3]) if a["models_used"] else "<span style='color:#555'>—</span>"}</td>
            <td>{badge(a["violations"])}</td>
            <td>{a["last_seen"][:16] if a["last_seen"] != "never" else "<span style='color:#555'>nunca</span>"}</td>
            <td>{sparkline(a["operations"])}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><title>Agent Scoreboard</title>
<style>
body {{ font-family: 'SF Mono','Fira Code',monospace; background: #0d1117; color: #c9d1d9; padding: 20px; margin: 0; }}
h1 {{ color: #58a6ff; font-size: 24px; margin-bottom: 4px; }}
.sub {{ color: #8b949e; font-size: 13px; margin-bottom: 20px; }}
table {{ border-collapse: collapse; width: 100%; background: #161b22; border-radius: 8px; overflow: hidden; }}
th {{ background: #21262d; color: #58a6ff; padding: 10px 12px; text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer; user-select: none; }}
th:hover {{ background: #30363d; }}
td {{ padding: 8px 12px; border-bottom: 1px solid #21262d; font-size: 13px; }}
tr:hover {{ background: #1c2128; }}
.filters {{ margin-bottom: 16px; display: flex; gap: 8px; align-items: center; }}
.filters button {{ background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; }}
.filters button.active {{ background: #1f6feb; border-color: #1f6feb; color: #fff; }}
.filters button:hover {{ background: #30363d; }}
.search {{ background: #0d1117; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 6px; font-size: 13px; width: 200px; }}
</style></head>
<body>
<h1>Agent Scoreboard</h1>
<p class="sub">Actualizado: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")} · <span id="count">{len(scoreboard)}</span> agentes</p>
<div class="filters">
  <input class="search" id="search" placeholder="Buscar agente..." oninput="filterTable()">
  <button onclick="filterByStatus('all')" id="f-all" class="active">Todos</button>
  <button onclick="filterByStatus('active')" id="f-active">Activos</button>
  <button onclick="filterByStatus('unknown')" id="f-unknown">Unknown</button>
</div>
<table id="sb-table">
<thead>
<tr><th onclick="sortTable(0)">Agent</th><th onclick="sortTable(1)">Role</th><th onclick="sortTable(2)">Lvl</th><th onclick="sortTable(3)">Status</th><th onclick="sortTable(4)">Ops</th><th onclick="sortTable(5)">Cost</th><th onclick="sortTable(6)">$/op</th><th onclick="sortTable(7)">Latency</th><th onclick="sortTable(8)">Tokens</th><th onclick="sortTable(9)">Models</th><th onclick="sortTable(10)">Violations</th><th onclick="sortTable(11)">Last Seen</th><th>Activity</th></tr>
</thead>
<tbody id="sb-body">
{rows_html}
</tbody>
</table>
<script>
let sortDir = {{}};
function sortTable(col) {{
  const tbody = document.getElementById('sb-body');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  sortDir[col] = !sortDir[col];
  const dir = sortDir[col] ? 1 : -1;
  rows.sort((a, b) => {{
    let va = a.cells[col].textContent.trim(), vb = b.cells[col].textContent.trim();
    let na = parseFloat(va.replace(/[$ms,]/g,'')), nb = parseFloat(vb.replace(/[$ms,]/g,''));
    if (!isNaN(na) && !isNaN(nb)) return (na - nb) * dir;
    return va.localeCompare(vb) * dir;
  }});
  rows.forEach(r => tbody.appendChild(r));
}}
function filterByStatus(s) {{
  document.querySelectorAll('.filters button').forEach(b => b.classList.remove('active'));
  document.getElementById('f-' + s).classList.add('active');
  const rows = document.querySelectorAll('#sb-body tr');
  rows.forEach(r => {{
    const status = r.cells[3].textContent.trim();
    r.style.display = s === 'all' || status === s ? '' : 'none';
  }});
}}
function filterTable() {{
  const q = document.getElementById('search').value.toLowerCase();
  const rows = document.querySelectorAll('#sb-body tr');
  rows.forEach(r => {{
    r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
  }});
}}
</script>
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
