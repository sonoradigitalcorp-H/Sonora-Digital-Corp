#!/usr/bin/env python3
"""Generador de presentaciones reveal.js — automatico, reusable, desplegable.

Uso:
  python3 scripts/presentar.py --session memory/learning/session-20260701.json
  python3 scripts/presentar.py --title "Mi Sesion" --date 2026-07-01 --score 77

Crea un HTML autónomo en ~/evolucion/presentacion-YYYYMMDD.html
"""
import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

EVOLUCION_DIR = Path.home() / "evolucion"
TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Presentacion</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/night.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/highlight/monokai.css">
<style>
  :root {{
    --accent: #3b82f6;
    --accent2: #06b6d4;
    --green: #22c55e;
    --yellow: #eab308;
    --red: #ef4444;
  }}
  .reveal {{ font-family: 'Inter', system-ui, sans-serif; }}
  .reveal h1 {{ color: var(--accent); text-transform: none; font-size: 2.5em; }}
  .reveal h2 {{ color: var(--accent2); text-transform: none; font-size: 1.6em; border-bottom: 2px solid #1e3a5f; padding-bottom: 0.3em; }}
  .reveal h3 {{ color: var(--accent); text-transform: none; }}
  .reveal p, .reveal li {{ color: #cbd5e1; font-size: 0.85em; }}
  .reveal ul {{ list-style: none; }}
  .reveal ul li::before {{ content: "▸ "; color: var(--accent2); }}
  .reveal code {{ background: #1e293b; padding: 0.15em 0.4em; border-radius: 4px; font-size: 0.8em; }}
  .reveal pre code {{ padding: 1em; font-size: 0.7em; line-height: 1.5; max-height: 400px; }}
  .reveal table {{ font-size: 0.75em; }}
  .reveal th {{ color: var(--accent2); border-bottom: 2px solid var(--accent); }}
  .reveal td {{ border-bottom: 1px solid #1e3a5f; }}
  .score-big {{ font-size: 3em; font-weight: bold; color: var(--accent2); }}
  .status {{ display: inline-block; padding: 0.15em 0.6em; border-radius: 4px; font-size: 0.7em; font-weight: bold; }}
  .status-ok {{ background: rgba(34,197,94,0.2); color: var(--green); }}
  .status-warn {{ background: rgba(234,179,8,0.2); color: var(--yellow); }}
  .status-fail {{ background: rgba(239,68,68,0.2); color: var(--red); }}
  .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1em; margin-top: 0.5em; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1em; margin-top: 0.5em; }}
  .card {{ background: #1e293b; border: 1px solid #1e3a5f; border-radius: 8px; padding: 0.8em; }}
  .card h4 {{ color: var(--accent); margin: 0 0 0.3em; font-size: 0.9em; }}
  .card p, .card li {{ font-size: 0.75em; }}
  .fragment {{ opacity: 0; transition: opacity 0.3s ease; }}
  .fragment.visible {{ opacity: 1; }}
  .subtitle {{ color: #64748b; font-size: 0.6em; margin-top: 0.3em; }}
  .big-number {{ font-size: 2.2em; font-weight: bold; color: var(--accent2); }}
  .big-label {{ font-size: 0.5em; color: #64748b; }}
  .revenue-row {{ display: flex; justify-content: space-between; padding: 0.4em 0; border-bottom: 1px solid #1e3a5f; }}
  .revenue-row:last-child {{ border: none; }}
  .revenue-artist {{ color: var(--accent); }}
  .revenue-rate {{ color: var(--green); font-weight: bold; }}
  blockquote {{ border-left: 3px solid var(--accent); padding-left: 1em; color: #94a3b8; font-style: italic; }}
</style>
</head>
<body>
<div class="reveal">
<div class="slides">

{slides}

</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/highlight/highlight.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/notes/notes.js"></script>
<script>
  Reveal.initialize({{
    hash: true,
    controls: true,
    progress: true,
    slideNumber: true,
    plugins: [ RevealHighlight, RevealNotes ]
  }});
</script>
</body>
</html>"""


def slide(tag, content):
    return f"<{tag}>\n{content}\n</{tag}>"


def section(name, content, cls=""):
    c = f"<section class='{cls}'><h2>{name}</h2>\n{content}</section>"
    return slide("section", c)


def title_slide(title, subtitle, metrics):
    metrics_html = ""
    if metrics:
        items = "".join(
            f"<div style='text-align:center;flex:1;'>"
            f"<div style='font-size:1.8em;font-weight:bold;color:var(--accent2);'>{v}</div>"
            f"<div style='font-size:0.5em;color:#64748b;'>{k}</div></div>"
            for k, v in metrics.items()
        )
        metrics_html = f"<div style='display:flex;gap:1em;justify-content:center;margin-top:1.5em;'>{items}</div>"
    return slide("section", f"""
<section>
  <h1 style="font-size:3em;">{title}</h1>
  <p style="color:#64748b;font-size:0.7em;margin-top:0.3em;">{subtitle}</p>
  {metrics_html}
</section>
""")


def timeline_slide(events):
    items = "".join(
        f"""
        <div style="display:flex;gap:1em;margin:0.5em 0;padding:0.5em;
                    background:#1e293b;border-radius:6px;border-left:3px solid var(--accent2);">
          <div style="min-width:80px;color:#64748b;font-size:0.7em;">{e['date']}</div>
          <div style="flex:1;">
            <div style="color:var(--accent);font-weight:bold;font-size:0.85em;">{e['title']}</div>
            <div style="color:#94a3b8;font-size:0.75em;">{e['desc']}</div>
          </div>
        </div>"""
        for e in events
    )
    return section("📅 Evolucion", f"""
<div style="text-align:left;max-width:700px;margin:0 auto;">
{items}
</div>
""")


def architecture_slide():
    return section("🏗 Arquitectura", """
<div class="grid-3">
  <div class="card">
    <h4>1. Capability Layer</h4>
    <p><code>planner/</code> — 7 modulos, 70 tests</p>
    <ul>
      <li>Registry JSON v2 + Pydantic</li>
      <li>Decision Engine + fallback chain</li>
      <li>Health checker TTL 5min</li>
      <li>5 executores: HTTP, CLI, Browser, MCP, SDK</li>
      <li>3 capabilities, 10 providers</li>
    </ul>
  </div>
  <div class="card">
    <h4>2. Collector Layer</h4>
    <p><code>scrapers/collectors/</code> — 8 colectores</p>
    <ul>
      <li>Deezer: search → ID → detail → tracks</li>
      <li>Apple Music: search API publica</li>
      <li>YouTube: yt-dlp CLI</li>
      <li>TikTok / Spotify: Playwright browser</li>
      <li>Instagram: login wall detection</li>
      <li>Cada uno con CAPABILITY_ID</li>
    </ul>
  </div>
  <div class="card">
    <h4>3. Sync + Data Layer</h4>
    <p><code>scrapers/sync.py</code> + <code>data/</code></p>
    <ul>
      <li>abe-music.json: fuente de verdad</li>
      <li>abe-contracts.json, abe-ledger.json</li>
      <li>Backup automatico pre-sync</li>
      <li>Eventos a events.jsonl</li>
      <li>Lead bridge a sales pipeline</li>
    </ul>
  </div>
</div>
""")


def production_slide(services):
    rows = "".join(
        f"<tr><td>{s['port']}</td><td>{s['name']}</td>"
        f"<td><span class='status-{s['status']}'>{s['label']}</span></td>"
        f"<td style='font-size:0.8em;color:#64748b;'>{s['note']}</td></tr>"
        for s in services
    )
    return section("🚀 Produccion", f"""
<table>
<thead><tr><th>Puerto</th><th>Servicio</th><th>Estado</th><th>Notas</th></tr></thead>
<tbody>{rows}</tbody>
</table>
""")


def revenue_slide(artists):
    rows = "".join(
        f"<div class='revenue-row'>"
        f"<span class='revenue-artist'>{a['name']}</span>"
        f"<span>{a['streams']:,} streams</span>"
        f"<span>${a['revenue']:,.2f}</span>"
        f"<span class='revenue-rate'>${a['rate']:.4f}/stream</span>"
        f"</div>"
        for a in artists
    )
    return section("💰 Revenue Intelligence", f"""
<div style="text-align:left;max-width:650px;margin:0 auto;">
{rows}
</div>
<pre style="margin-top:0.8em;"><code class="language-bash"># Todos los artistas = $0.004/stream → 100% Spotify
# Apple Music ($0.008) daria 2x revenue (no reportado)
# YouTube ($0.001) daria 0.25x revenue (no reportado)
# → Oplaai paga solo Spotify</code></pre>
""")


def broken_slide(issues):
    items = "".join(
        f"<div style='display:flex;gap:1em;margin:0.4em 0;padding:0.4em 0.6em;"
        f"background:#1e293b;border-radius:4px;border-left:3px solid "
        f"{'var(--red)' if i['sev']=='high' else 'var(--yellow)'};'>"
        f"<span style='min-width:120px;font-size:0.75em;color:#64748b;'>{i['sev'].upper()}</span>"
        f"<span style='font-size:0.8em;'>{i['desc']}</span></div>"
        for i in issues
    )
    return section("⚠️ Que se Rompe", f"<div style='text-align:left;max-width:700px;margin:0 auto;'>{items}</div>")


def missing_slide(priorities):
    sections_html = ""
    for section_name, items in priorities.items():
        lis = "".join(f"<li>{i}</li>" for i in items)
        sections_html += f"<div class='card'><h4>{section_name}</h4><ul>{lis}</ul></div>"
    return section("🧩 Que Falta", f"<div class='grid-3'>{sections_html}</div>")


def senior_slide():
    return section("🧠 Senior Thinking", """
<div class="grid-3">
  <div class="card"><h4>1. Capability First</h4><p>Nunca "que API uso". Siempre "que capacidad necesito". El sistema decide quien ejecuta.</p></div>
  <div class="card"><h4>2. Fallback es la Unica Verdad</h4><p>Siempre plan B, C, D. Health check da prioridad, no bloquea.</p></div>
  <div class="card"><h4>3. Eventos como Fuente de Verdad</h4><p>Toda accion deja traza estructurada. JSONL es grep-friendly, importable.</p></div>
</div>
<div class="grid-3" style="margin-top:0.5em;">
  <div class="card"><h4>4. Zero Config del Fundador</h4><p>Abraham no configura nada. Si necesita tocar algo, el sistema fallo.</p></div>
  <div class="card"><h4>5. Costo $0 es Restriccion de Diseno</h4><p>Sin API keys de pago fuerza excelencia tecnica.</p></div>
  <div class="card"><h4>6. Specs > Codigo</h4><p>SPEC → Gherkin → ADR → Code → Score → LECCION. El codigo es el ultimo paso.</p></div>
</div>
""")


def next_steps_slide(steps):
    items = "".join(
        f"<div style='display:flex;gap:0.8em;margin:0.5em 0;padding:0.5em 0.8em;"
        f"background:#1e293b;border-radius:6px;'>"
        f"<span style='color:var(--accent2);font-weight:bold;'>{i['num']}.</span>"
        f"<span>{i['desc']}</span></div>"
        for i in steps
    )
    return section("📌 Proximos Pasos", f"""
<div style='text-align:left;max-width:600px;margin:0 auto;'>{items}</div>
""")


def closing_slide():
    return slide("section", """
<section>
  <h1 style="font-size:2.5em;">⏚</h1>
  <p style="color:#64748b;font-size:0.7em;">Construye el registry. Todo lo demas emerge.</p>
  <p style="color:#64748b;font-size:0.6em;margin-top:1em;">Sonora Digital Corp — Sistema Autonomo de Inteligencia Musical</p>
</section>
""")


def generate_presentation(title, subtitle, metrics=None, timeline=None, services=None,
                          artists=None, issues=None, priorities=None, steps=None):
    slides = []
    slides.append(title_slide(title, subtitle, metrics))
    if timeline:
        slides.append(timeline_slide(timeline))
    slides.append(architecture_slide())
    if services:
        slides.append(production_slide(services))
    if artists:
        slides.append(revenue_slide(artists))
    if issues:
        slides.append(broken_slide(issues))
    if priorities:
        slides.append(missing_slide(priorities))
    slides.append(senior_slide())
    if steps:
        slides.append(next_steps_slide(steps))
    slides.append(closing_slide())

    return TEMPLATE.format(title=title, slides="\n".join(slides))


def load_session(path):
    with open(path) as f:
        return json.load(f)


def build_from_session(session):
    title = session.get("title", "Session Review")
    date_str = session.get("date", str(date.today()))
    score = session.get("score", 0)
    spec = session.get("spec", "")

    subtitle = f"{spec} · {date_str} · Score: {score}/100"

    learnings = session.get("learnings", [])
    builds = session.get("builds", [])
    broken_list = session.get("broken", [])
    missing_list = session.get("missing", [])
    services = session.get("services", {})
    artists = session.get("artists", {})

    metrics = {
        "Specs": "3",
        "Tests": "79",
        "Providers": "10",
        "Capabilities": "3",
    }

    timeline = [
        {"date": "Jun 29", "title": "ABE Music OS + Live Data Pipeline",
         "desc": "SPEC-20260701-003. Nace ABE Music, Deezer/Apple Music collectors, sync engine, PWA. Score 84."},
        {"date": "Jun 30", "title": "Browser Scraping",
         "desc": "TikTok (Playwright), Spotify (raw text), Instagram login detection. Playwright chromium instalado."},
        {"date": "Jul 1", "title": "Capability Registry + Decision Engine",
         "desc": f"SPEC-{spec}. Planner 7 modulos, 70 tests, registry v2, SDK bridge, 10 providers. Score {score}."},
    ]

    services_list = [
        {"port": p, "name": n, "status": "ok" if p in ("5174", "5180", "8000", "18789", "6333", "7687", "5678") else "warn",
         "label": "activo", "note": ""}
        for p, n in services.items()
    ]

    artists_list = []
    for name, data in artists.items():
        streams = data.get("streams", 0)
        revenue = data.get("revenue", 0)
        rate = revenue / streams if streams > 0 else 0
        artists_list.append({
            "name": name,
            "streams": streams,
            "revenue": revenue,
            "rate": rate,
        })
    artists_list.sort(key=lambda x: x["streams"], reverse=True)

    issues = [{"sev": "high" if "login" in b.lower() or "cron" in b.lower() else "med", "desc": b}
              for b in broken_list[:6]]

    priorities = {
        "🔴 Alta": [m for m in missing_list[:4]],
        "🟡 Media": [m for m in missing_list[4:8]],
        "🟢 Baja": [m for m in missing_list[8:12]],
    }

    next_steps = [
        {"num": 1, "desc": "Git push + verificar CI verde en GitHub Actions"},
        {"num": 2, "desc": "Instalar sync cron cada 6h (scripts/install-sync-cron.sh)"},
        {"num": 3, "desc": "Seedear Qdrant coleccion abe-artists"},
        {"num": 4, "desc": "Fix lead bridge a Neo4j (import path)"},
        {"num": 5, "desc": "Dashboard de salud de providers"},
        {"num": 6, "desc": "Instagram cookie auth para perfiles reales"},
    ]

    return generate_presentation(title, subtitle, metrics, timeline, services_list,
                                  artists_list, issues, priorities, next_steps)


def main():
    parser = argparse.ArgumentParser(description="Generador de presentaciones reveal.js")
    parser.add_argument("--session", help="Path a session JSON (en memory/learning/)")
    parser.add_argument("--title", default="Session Review")
    parser.add_argument("--date", default=str(date.today()))
    parser.add_argument("--score", type=int, default=0)
    parser.add_argument("--output", help="Output path (default: ~/evolucion/presentacion-YYYYMMDD.html)")
    args = parser.parse_args()

    if args.session:
        session = load_session(args.session)
        html = build_from_session(session)
        date_str = session.get("date", str(date.today()))
    else:
        html = generate_presentation(args.title, f"Score: {args.score}/100")
        date_str = args.date

    output = args.output or str(EVOLUCION_DIR / f"presentacion-{date_str.replace('-', '')}.html")
    EVOLUCION_DIR.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        f.write(html)
    print(f"✅ Presentacion generada: {output}")
    print(f"   http://149.56.46.173:8080/{Path(output).name}")


if __name__ == "__main__":
    main()
