import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

logger = logging.getLogger(__name__)

app = FastAPI(title="Control Kernel (Level 7)", version="1.0.0")

SERVICES = {
    "webui": {"port": 5174, "label": "Web UI", "level": "core"},
    "abe-service": {"port": 5180, "label": "ABE Service", "level": "core"},
    "hermes": {"port": 8000, "label": "Hermes MCP", "level": "core"},
    "evolution": {"port": 8080, "label": "Evolution Dashboard", "level": "core"},
    "guardian": {"port": 8088, "label": "Truth Guardian", "level": "core"},
    "content-server": {"port": 8765, "label": "Content Server MCP", "level": "product"},
    "open-notebook-ui": {"port": 8502, "label": "Open Notebook UI", "level": "product"},
    "open-notebook-api": {"port": 5055, "label": "Open Notebook API", "level": "product"},
    "omnivoice": {"port": 3900, "label": "OmniVoice", "level": "product"},
}

KERNEL_LEVELS = {
    1: {"name": "Observe", "app": "apps/observe/", "status": "implemented"},
    2: {"name": "Understand", "app": "apps/understand/", "status": "implemented"},
    3: {"name": "Decide", "app": "apps/decide/", "status": "partial"},
    4: {"name": "Act", "app": "apps/act/", "status": "partial"},
    5: {"name": "Measure", "app": "apps/measure/", "status": "partial"},
    6: {"name": "Learn", "app": "apps/learn/", "status": "partial"},
    7: {"name": "Control", "app": "apps/control/", "status": "implemented"},
}


async def check_service(host: str, port: int) -> dict:
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex((host, port))
        s.close()
        return {"alive": result == 0, "port": port}
    except Exception as e:
        return {"alive": False, "error": str(e), "port": port}


@app.get("/api/v1/control/status")
async def control_status():
    results = {}
    for name, svc in SERVICES.items():
        results[name] = await check_service("localhost", svc["port"])
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": results,
        "alive_count": sum(1 for s in results.values() if s["alive"]),
        "total": len(SERVICES),
    }


@app.get("/api/v1/control/kernel")
async def kernel_status():
    return {"levels": KERNEL_LEVELS}


@app.get("/api/v1/control/execution")
async def execution_status():
    db_path = Path("state/execution/queue.db")
    if not db_path.exists():
        return {"status": "no_database", "tasks": 0}
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.execute("SELECT COUNT(*) FROM tasks")
        total = cur.fetchone()[0]
        cur = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='pending'")
        pending = cur.fetchone()[0]
        conn.close()
        return {"status": "ok", "tasks": total, "pending": pending, "db": str(db_path)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/api/v1/control/health")
async def health():
    svc = await control_status()
    return {"status": "ok" if svc["alive_count"] == svc["total"] else "degraded", "details": svc}


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return CONTROL_HTML


CONTROL_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Control Kernel — SDC</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #0a0a0f; color: #e0e0e0; font-family: 'SF Mono','Fira Code',monospace; padding: 2rem; }
  h1 { color: #00ff88; font-size: 1.5rem; margin-bottom: 0.5rem; }
  .sub { color: #888; font-size: 0.8rem; margin-bottom: 2rem; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
  .card { background: #12121a; border: 1px solid #2a2a3a; border-radius: 12px; padding: 1.25rem; }
  .card h3 { color: #00ff88; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.75rem; }
  .alive { color: #00ff88; }
  .dead { color: #ff4444; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; }
  .badge-core { background: #1a3a2a; color: #00ff88; }
  .badge-product { background: #2a1a3a; color: #b388ff; }
  .stat { font-size: 1.2rem; font-weight: bold; }
  .kernel-bar { display: flex; gap: 0.25rem; margin: 1rem 0; }
  .kernel-level { flex: 1; padding: 0.5rem; text-align: center; border-radius: 6px; font-size: 0.7rem; }
  .kl-done { background: #1a3a2a; color: #00ff88; }
  .kl-partial { background: #3a2a1a; color: #ffaa00; }
  .kl-stub { background: #2a1a1a; color: #ff4444; }
  .refresh { float: right; color: #666; cursor: pointer; font-size: 0.8rem; }
  .refresh:hover { color: #00ff88; }
</style>
</head>
<body>
<h1>◉ Control Kernel</h1>
<p class="sub">Cognitive Kernel Level 7 — Unified Dashboard <span class="refresh" onclick="location.reload()">↻ refresh</span></p>

<h3 style="margin-bottom:0.5rem;color:#888;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px">Kernel Levels</h3>
<div class="kernel-bar" id="kernel-bar"></div>

<div class="grid" id="services-grid"></div>

<h3 style="margin:1.5rem 0 0.5rem;color:#888;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px">Execution Queue</h3>
<div class="card" id="exec-card"><p>Loading...</p></div>

<script>
const LEVELS = {
  1: {name:"Observe",status:"done"}, 2:{name:"Understand",status:"done"},
  3:{name:"Decide",status:"partial"}, 4:{name:"Act",status:"partial"},
  5:{name:"Measure",status:"partial"}, 6:{name:"Learn",status:"partial"},
  7:{name:"Control",status:"done"}
};

function renderKernelBar() {
  const bar = document.getElementById('kernel-bar');
  bar.innerHTML = '';
  for (const [num, lvl] of Object.entries(LEVELS)) {
    const cls = lvl.status === 'done' ? 'kl-done' : lvl.status === 'partial' ? 'kl-partial' : 'kl-stub';
    const div = document.createElement('div');
    div.className = 'kernel-level ' + cls;
    div.innerHTML = `<strong>L${num}</strong><br>${lvl.name}`;
    bar.appendChild(div);
  }
}

function renderServices(data) {
  const grid = document.getElementById('services-grid');
  grid.innerHTML = '';
  const order = ['webui','abe-service','hermes','evolution','guardian','content-server','open-notebook-ui','open-notebook-api','omnivoice'];
  for (const name of order) {
    if (!data.services[name]) continue;
    const svc = data.services[name];
    const svcInfo = {'webui':{'label':'Web UI','level':'core'},'abe-service':{'label':'ABE Service','level':'core'},'hermes':{'label':'Hermes MCP','level':'core'},'evolution':{'label':'Evolution Dashboard','level':'core'},'guardian':{'label':'Truth Guardian','level':'core'},'content-server':{'label':'Content Server','level':'product'},'open-notebook-ui':{'label':'Open Notebook UI','level':'product'},'open-notebook-api':{'label':'Open Notebook API','level':'product'},'omnivoice':{'label':'OmniVoice','level':'product'}}[name];
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <h3>${svcInfo.label} <span class="badge badge-${svcInfo.level}">${svcInfo.level}</span></h3>
      <p class="${svc.alive ? 'alive' : 'dead'} stat">${svc.alive ? '● ONLINE' : '○ OFFLINE'}</p>
      <p style="font-size:0.75rem;color:#666">:${svc.port}${svc.error ? ' · '+svc.error : ''}</p>
    `;
    grid.appendChild(card);
  }
}

async function load() {
  renderKernelBar();
  try {
    const res = await fetch('/api/v1/control/status');
    const data = await res.json();
    renderServices(data);
    document.getElementById('services-grid').insertAdjacentHTML('beforebegin',
      `<p style="font-size:0.8rem;color:#666;margin-bottom:0.5rem">${data.alive_count}/${data.total} services online</p>`);
  } catch(e) {
    document.getElementById('services-grid').innerHTML = '<p class="dead">Failed to load status</p>';
  }
  try {
    const res = await fetch('/api/v1/control/execution');
    const data = await res.json();
    document.getElementById('exec-card').innerHTML = data.status === 'ok'
      ? `<p>Tasks: <strong>${data.tasks}</strong> · Pending: <strong>${data.pending}</strong></p><p style="font-size:0.75rem;color:#666">${data.db}</p>`
      : `<p style="color:#ffaa00">${data.status}${data.error ? ': '+data.error : ''}</p>`;
  } catch(e) {
    document.getElementById('exec-card').innerHTML = '<p class="dead">Failed to load execution stats</p>';
  }
}
load();
</script>
</body>
</html>"""
