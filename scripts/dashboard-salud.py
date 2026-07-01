#!/usr/bin/env python3
"""Genera dashboard de salud de providers — HTML visual.

Uso: python3 scripts/dashboard-salud.py [--watch]
     --watch: regenera cada 30s (dejalo corriendo)
"""
import argparse
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("dashboard")

BASE = Path(__file__).resolve().parent.parent
OUTPUT = Path.home() / "evolucion" / "dashboard-salud.html"
REFRESH = 30  # segundos

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard Salud — Providers</title>
<style>
  :root {{
    --bg: #0a0e17; --bg2: #111827; --bg3: #1a2332;
    --border: #1e3a5f; --accent: #3b82f6; --accent2: #06b6d4;
    --green: #22c55e; --yellow: #eab308; --red: #ef4444;
    --text: #e2e8f0; --text2: #94a3b8; --text3: #64748b;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'SF Mono', 'Fira Code', monospace;
    background: var(--bg); color: var(--text);
    padding: 30px; max-width: 900px; margin: 0 auto;
  }}
  h1 {{ color: var(--accent); font-size: 1.5em; margin-bottom: 5px; }}
  .subtitle {{ color: var(--text3); font-size: 0.8em; margin-bottom: 25px; }}
  .last-update {{ color: var(--text3); font-size: 0.75em; margin-bottom: 20px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 12px; }}
  .card {{
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 8px; padding: 15px; position: relative;
  }}
  .card h3 {{ font-size: 0.9em; color: var(--accent2); margin-bottom: 6px; }}
  .card .status {{
    display: inline-block; padding: 2px 10px; border-radius: 4px;
    font-size: 0.75em; font-weight: bold;
  }}
  .ok {{ background: rgba(34,197,94,0.2); color: var(--green); }}
  .warn {{ background: rgba(234,179,8,0.2); color: var(--yellow); }}
  .fail {{ background: rgba(239,68,68,0.2); color: var(--red); }}
  .unknown {{ background: rgba(100,116,139,0.2); color: var(--text3); }}
  .card .detail {{ margin-top: 8px; font-size: 0.78em; color: var(--text2); }}
  .card .detail span {{ display: block; margin: 2px 0; }}
  .legend {{ display: flex; gap: 20px; margin-bottom: 20px; font-size: 0.8em; }}
  .legend-item {{ display: flex; align-items: center; gap: 5px; }}
  .dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
</style>
</head>
<body>
<h1>⚕ Dashboard de Salud</h1>
<p class="subtitle">Estado de providers del sistema Sonora Digital Corp</p>
<div class="legend">
  <div class="legend-item"><span class="dot" style="background:var(--green)"></span> Healthy</div>
  <div class="legend-item"><span class="dot" style="background:var(--yellow)"></span> Degraded</div>
  <div class="legend-item"><span class="dot" style="background:var(--red)"></span> Down</div>
  <div class="legend-item"><span class="dot" style="background:var(--text3)"></span> Unknown</div>
</div>
<p class="last-update">Ultima actualizacion: {timestamp}</p>
<div class="grid">
{cards}
</div>
<script>
  setTimeout(function() {{ location.reload(); }}, {refresh} * 1000);
</script>
</body>
</html>"""

CARD = """  <div class="card">
    <h3>{name}</h3>
    <span class="status {css_class}">{label}</span>
    <div class="detail">
      <span>Capability: {capability}</span>
      <span>Type: {ctype}</span>
      <span>Ultimo check: {last_check}</span>
      <span>Latencia: {latency}</span>
    </div>
  </div>"""


def get_health_data():
    """Obtiene datos de salud usando planner."""
    os.environ["PYTHONPATH"] = str(BASE)
    import sys
    sys.path.insert(0, str(BASE))

    from planner.registry import load_registry, get_capability, list_capabilities
    from planner.health import get_provider_health
    from planner.models import ProviderRef

    registry = load_registry()
    providers = []

    for cid, cap in registry.items():
        for p in cap.providers:
            health = get_provider_health(p.id)
            providers.append({
                "id": p.id,
                "name": p.id,
                "capability": cid,
                "contract_type": p.contract_type,
                "health": health,
            })

    return providers


def status_info(health):
    if health is None:
        return "unknown", "Unknown"
    if health.is_healthy:
        return "ok", "Healthy"
    elif health.is_degraded:
        return "warn", "Degraded"
    else:
        return "fail", "Down"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true", help="Regenera cada 30s")
    args = parser.parse_args()

    while True:
        try:
            providers = get_health_data()
            cards = []
            for p in providers:
                css_class, label = status_info(p["health"])
                last_check = "never"
                latency = "N/A"
                if p["health"]:
                    if p["health"].last_checked:
                        last_check = p["health"].last_checked.strftime("%H:%M:%S")
                    latency = f"{p['health'].latency or 0:.0f}ms"
                cards.append(CARD.format(
                    name=p["id"],
                    css_class=css_class,
                    label=label,
                    capability=p["capability"],
                    ctype=p["contract_type"],
                    last_check=last_check,
                    latency=latency,
                ))

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            html = HTML_TEMPLATE.format(
                timestamp=now,
                cards="\n".join(cards),
                refresh=REFRESH,
            )

            Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)
            with open(OUTPUT, "w") as f:
                f.write(html)

            log.info(f"Dashboard generado: {OUTPUT}")

        except Exception as e:
            log.error(f"Error generando dashboard: {e}")

        if not args.watch:
            break
        time.sleep(REFRESH)


if __name__ == "__main__":
    main()
