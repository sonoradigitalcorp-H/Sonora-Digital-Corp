#!/usr/bin/env python3
"""
proactive_scheduler.py — Morning briefing para Hermes Agent (VPS Hostinger).
Gather system health, check services, detect contradictions in ESTADO.md,
and send a formatted briefing via Hermes → Telegram.

Usage:
  python3 proactive_scheduler.py                    # Run briefing
  python3 proactive_scheduler.py --dry-run          # Print only, no send
  python3 proactive_scheduler.py --json             # JSON output
  python3 proactive_scheduler.py --check            # Health check only (exit 0/1)

Deploy: VPS Hostinger 45.90.108.12
Timer:  daily 7am CDT (14:00 UTC)
"""

import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# ─── CONFIG ───────────────────────────────────────────────────────────────────

VPS_HOST = os.environ.get("VPS_HOST", "45.90.108.12")
VPS_USER = os.environ.get("VPS_USER", "root")
HERMES_URL = os.environ.get("HERMES_URL", "http://127.0.0.1:8642")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://127.0.0.1:6333")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
ESTADO_PATH = os.environ.get(
    "ESTADO_PATH",
    "/home/mystic/Documentos/Sonora Digital Corp Nuevo/ESTADO.md",
)
OPENROUTER_KEY_PATHS = [
    os.environ.get("OPENROUTER_KEY_PATH", ""),
    "/opt/sdc/.env",
    os.path.expanduser("~/.hermes/.env"),
]
LOG_DIR = Path(os.environ.get("LOG_DIR", "/var/log/proactive-scheduler"))
LOCK_FILE = Path("/tmp/proactive-scheduler.lock")

CDT = timezone(timedelta(hours=-6))

# Critical services to monitor (name → expected port)
CRITICAL_SERVICES = {
    "vps-ai-server": 8643,
    "sdc-stt": 5292,
    "sdc-tts": 5293,
    "hermes-gateway": 8642,
    "cloudflared-tunnel": None,
    "nginx": None,
}

# Docker compose project
COMPOSE_DIR = "/opt/sdc"

# ─── UTILITIES ────────────────────────────────────────────────────────────────

def now_cdt() -> datetime:
    return datetime.now(CDT)


def log(msg: str, level: str = "INFO"):
    ts = now_cdt().strftime("%Y-%m-%d %H:%M:%S CDT")
    print(f"[{ts}] [{level}] {msg}", file=sys.stderr)


def run_cmd(cmd: str, timeout: int = 10, shell: bool = True) -> tuple[int, str, str]:
    """Run command, return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(
            cmd, shell=shell, capture_output=True, text=True, timeout=timeout
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


def http_get(url: str, timeout: int = 5, headers: Optional[dict] = None) -> tuple[int, str]:
    """HTTP GET, return (status_code, body)."""
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)


# ─── HEALTH CHECKS ────────────────────────────────────────────────────────────

def check_docker() -> dict:
    """Docker containers status."""
    rc, out, err = run_cmd("docker ps --format '{{.Names}}|{{.Status}}|{{.Ports}}'", timeout=15)
    containers = []
    unhealthy = []
    if rc == 0 and out:
        for line in out.split("\n"):
            if not line.strip():
                continue
            parts = line.split("|", 2)
            name = parts[0] if len(parts) > 0 else "?"
            status = parts[1] if len(parts) > 1 else "?"
            ports = parts[2] if len(parts) > 2 else ""
            containers.append({"name": name, "status": status, "ports": ports})
            if "unhealthy" in status.lower() or "restarting" in status.lower():
                unhealthy.append(name)
    return {
        "total": len(containers),
        "containers": containers,
        "unhealthy": unhealthy,
        "ok": len(unhealthy) == 0,
    }


def check_system_resources() -> dict:
    """Memory, disk, load, uptime."""
    # Memory
    rc, out, _ = run_cmd("free -m | awk '/Mem:/{print $2,$3,$4,$7}'")
    mem = {"total": 0, "used": 0, "free": 0, "available": 0}
    if rc == 0 and out:
        parts = out.split()
        if len(parts) >= 4:
            mem = {
                "total": int(parts[0]),
                "used": int(parts[1]),
                "free": int(parts[2]),
                "available": int(parts[3]),
            }

    # Disk
    rc, out, _ = run_cmd("df -h / | awk 'NR==2{print $2,$3,$4,$5}'")
    disk = {"total": "?", "used": "?", "free": "?", "pct": "?"}
    if rc == 0 and out:
        parts = out.split()
        if len(parts) >= 4:
            disk = {
                "total": parts[0],
                "used": parts[1],
                "free": parts[2],
                "pct": parts[3],
            }

    # Load
    rc, out, _ = run_cmd("cat /proc/loadavg")
    load = out.split()[:3] if rc == 0 else ["?", "?", "?"]

    # Uptime
    rc, out, _ = run_cmd("uptime -p")
    uptime = out if rc == 0 else "?"

    return {
        "memory": mem,
        "memory_pct": round(mem["used"] / mem["total"] * 100, 1) if mem["total"] > 0 else 0,
        "disk": disk,
        "load_1m": load[0],
        "load_5m": load[1],
        "load_15m": load[2],
        "uptime": uptime,
    }


def check_services() -> dict:
    """Systemd + Docker services status."""
    # Systemd-based services
    SYSTEMD_SERVICES = {
        "vps-ai-server": 8643,
        "sdc-stt": 5292,
        "sdc-tts": 5293,
    }
    # Docker-based services (check via docker ps)
    DOCKER_SERVICES = {
        "hermes-gateway": "sdc-hermes",
        "cloudflared-tunnel": "sdc-cloudflared",
        "nginx": "sdc-nginx",
    }
    services = {}
    # Check systemd
    for name in SYSTEMD_SERVICES:
        rc, out, _ = run_cmd(f"systemctl is-active {name} 2>/dev/null")
        active = out == "active"
        rc2, out2, _ = run_cmd(f"systemctl is-enabled {name} 2>/dev/null")
        enabled = out2 == "enabled"
        services[name] = {"active": active, "enabled": enabled, "type": "systemd"}
    # Check Docker containers
    rc, out, _ = run_cmd("docker ps --format '{{.Names}}|{{.Status}}'", timeout=10)
    running_containers = {}
    if rc == 0 and out:
        for line in out.split("\n"):
            if "|" in line:
                name, status = line.split("|", 1)
                running_containers[name.strip()] = status.strip()
    for svc_name, container_name in DOCKER_SERVICES.items():
        is_running = any(container_name in k for k in running_containers)
        services[svc_name] = {"active": is_running, "enabled": True, "type": "docker"}
    return services


def check_endpoints() -> dict:
    """HTTP health endpoints."""
    endpoints = {
        "hermes-gateway": f"{HERMES_URL}/health",
        "qdrant": f"{QDRANT_URL}/collections",
        "ollama": f"{OLLAMA_URL}/api/tags",
    }
    results = {}
    for name, url in endpoints.items():
        status, body = http_get(url, timeout=5)
        results[name] = {"status": status, "ok": 200 <= status < 400}
    return results


def check_qdrant() -> dict:
    """Qdrant collections health."""
    status, body = http_get(f"{QDRANT_URL}/collections", timeout=5)
    if status != 200:
        return {"ok": False, "error": f"HTTP {status}", "collections": []}
    try:
        data = json.loads(body)
        collections = []
        for c in data.get("result", {}).get("collections", []):
            name = c.get("name", "?")
            # Get point count
            s2, b2 = http_get(f"{QDRANT_URL}/collections/{name}", timeout=5)
            points = 0
            if s2 == 200:
                d2 = json.loads(b2)
                points = d2.get("result", {}).get("optimizer_status", "?")
                # Try vectors_count
                points = d2.get("result", {}).get("vectors_count", 0)
            collections.append({"name": name, "points": points})
        return {"ok": True, "collections": collections}
    except Exception as e:
        return {"ok": False, "error": str(e), "collections": []}


def check_openrouter_credits() -> dict:
    """Check OpenRouter API key credits."""
    # Try to load key from env or .env files
    key = OPENROUTER_KEY
    if not key:
        for path in OPENROUTER_KEY_PATHS:
            if not path:
                continue
            try:
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("OPENROUTER_API_KEY="):
                            key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
                if key:
                    break
            except FileNotFoundError:
                pass

    if not key:
        return {"ok": False, "error": "No OPENROUTER_API_KEY found"}

    status, body = http_get(
        "https://openrouter.ai/api/v1/auth/key",
        headers={"Authorization": f"Bearer {key}"},
        timeout=10,
    )
    if status != 200:
        return {"ok": False, "error": f"HTTP {status}"}

    try:
        data = json.loads(body)
        limit = data.get("data", {}).get("limit", 0)
        usage = data.get("data", {}).get("usage", 0)
        remaining = limit - usage if limit else 0
        return {
            "ok": True,
            "limit": limit,
            "usage": usage,
            "remaining": round(remaining, 2),
            "label": data.get("data", {}).get("label", "?"),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def check_cpu_intensive() -> dict:
    """Find processes using >80% CPU."""
    rc, out, _ = run_cmd("ps aux --sort=-%cpu | awk 'NR>1 && $3>20{print $3, $11}' | head -5")
    processes = []
    if rc == 0 and out:
        for line in out.split("\n"):
            parts = line.split(None, 1)
            if len(parts) == 2:
                processes.append({"cpu_pct": float(parts[0]), "cmd": parts[1]})
    return {"hog_processes": processes, "ok": len(processes) == 0}


def check_systemd_failed() -> dict:
    """List failed systemd units."""
    rc, out, _ = run_cmd("systemctl --failed --no-legend --no-pager | head -10")
    failed = []
    if rc == 0 and out:
        for line in out.split("\n"):
            if line.strip():
                failed.append(line.strip())
    return {"failed": failed, "ok": len(failed) == 0}


# ─── ESTADO CONTRADICTION DETECTOR ────────────────────────────────────────────

def load_estado() -> str:
    """Load ESTADO.md content."""
    try:
        with open(ESTADO_PATH, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def detect_contradictions(estado: str, health: dict) -> list[str]:
    """
    Cross-check ESTADO.md claims against live system state.
    Returns list of contradiction strings.
    """
    contradictions = []

    # 1. ESTADO claims services are active — verify
    if "24/7 VPS VERIFICADO" in estado or "Todos" in estado:
        services = health.get("services", {})
        for svc, info in services.items():
            if not info["active"]:
                contradictions.append(
                    f"ESTADO dice '{svc}' activo, pero esta {info['active']}"
                )

    # 2. ESTADO claims specific containers — verify docker
    docker = health.get("docker", {})
    expected_containers = ["sdc-hermes", "sdc-nginx", "sdc-ollama", "sdc-qdrant"]
    running_names = [c["name"] for c in docker.get("containers", [])]
    for ec in expected_containers:
        found = any(ec in name for name in running_names)
        if not found:
            contradictions.append(
                f"ESTADO menciona container '{ec}' pero no esta corriendo"
            )

    # 3. Memory claims — if ESTADO says "RAM libre" but actually critical
    mem = health.get("resources", {}).get("memory_pct", 0)
    if mem > 90:
        contradictions.append(f"RAM al {mem}% — riesgo alto de swap/OOM")

    # 4. Disk claims
    disk_pct_str = health.get("resources", {}).get("disk", {}).get("pct", "0%")
    try:
        disk_pct = int(disk_pct_str.replace("%", ""))
        if disk_pct > 85:
            contradictions.append(f"Disco al {disk_pct}% — cerca del limite")
    except (ValueError, AttributeError):
        pass

    # 5. OpenRouter credits
    credits = health.get("credits", {})
    if credits.get("ok") and credits.get("remaining", 0) < 1.0:
        contradictions.append(
            f"OpenRouter creditos bajos: ${credits['remaining']:.2f} restantes"
        )

    # 6. CPU hogs
    cpu = health.get("cpu", {})
    for proc in cpu.get("hog_processes", []):
        contradictions.append(
            f"Proceso con CPU alta: {proc['cmd'][:60]} ({proc['cpu_pct']}%)"
        )

    # 7. Failed systemd units
    failed = health.get("failed_units", {}).get("failed", [])
    for f_unit in failed:
        contradictions.append(f"Unidad systemd fallida: {f_unit[:60]}")

    return contradictions


# ─── BRIEFING GENERATOR ───────────────────────────────────────────────────────

def health_emoji(ok: bool) -> str:
    return "✅" if ok else "🚨"


def format_briefing(health: dict, contradictions: list[str]) -> str:
    """Generate the morning briefing in Spanish."""
    now = now_cdt()
    date_str = now.strftime("%A %d de %B %Y").replace(
        "Monday", "Lunes"
    ).replace(
        "Tuesday", "Martes"
    ).replace(
        "Wednesday", "Miércoles"
    ).replace(
        "Thursday", "Jueves"
    ).replace(
        "Friday", "Viernes"
    ).replace(
        "Saturday", "Sábado"
    ).replace(
        "Sunday", "Domingo"
    ).replace(
        "January", "Enero"
    ).replace(
        "February", "Febrero"
    ).replace(
        "March", "Marzo"
    ).replace(
        "April", "Abril"
    ).replace(
        "May", "Mayo"
    ).replace(
        "June", "Junio"
    ).replace(
        "July", "Julio"
    ).replace(
        "August", "Agosto"
    ).replace(
        "September", "Septiembre"
    ).replace(
        "October", "Octubre"
    ).replace(
        "November", "Noviembre"
    ).replace(
        "December", "Diciembre"
    )

    lines = [
        f"🌅 BRIEFING MATUTINO — {date_str}",
        f"🕐 Hora: {now.strftime('%H:%M CDT')}",
        "",
        "═══ SISTEMA ═══",
    ]

    # Docker
    docker = health.get("docker", {})
    lines.append(
        f"{health_emoji(docker.get('ok', False))} Docker: {docker.get('total', 0)} containers"
    )
    if docker.get("unhealthy"):
        for u in docker["unhealthy"]:
            lines.append(f"  🚨 {u} — UNHEALTHY")

    # Resources
    res = health.get("resources", {})
    mem = res.get("memory", {})
    mem_pct = res.get("memory_pct", 0)
    mem_emoji = "✅" if mem_pct < 80 else "⚠️" if mem_pct < 90 else "🚨"
    lines.append(
        f"{mem_emoji} RAM: {mem.get('used', '?')}/{mem.get('total', '?')}MB ({mem_pct}%)"
    )
    lines.append(
        f"{health_emoji(int(res.get('disk', {}).get('pct', '0%').replace('%','')) < 85)} "
        f"Disco: {res.get('disk', {}).get('used', '?')}/{res.get('disk', {}).get('total', '?')} "
        f"({res.get('disk', {}).get('pct', '?')})"
    )
    lines.append(f"📊 Load: {res.get('load_1m', '?')} | {res.get('load_5m', '?')} | {res.get('load_15m', '?')}")
    lines.append(f"⏱️ Uptime: {res.get('uptime', '?')}")

    # Services
    lines.append("")
    lines.append("═══ SERVICIOS ═══")
    services = health.get("services", {})
    for name, info in services.items():
        emoji = "✅" if info["active"] else "🚨"
        enabled_str = "enabled" if info["enabled"] else "disabled"
        lines.append(f"{emoji} {name}: {'activo' if info['active'] else 'INACTIVO'} ({enabled_str})")

    # Endpoints
    lines.append("")
    lines.append("═══ ENDPOINTS ═══")
    endpoints = health.get("endpoints", {})
    for name, info in endpoints.items():
        lines.append(f"{health_emoji(info.get('ok', False))} {name}: HTTP {info.get('status', '?')}")

    # Qdrant
    qdrant = health.get("qdrant", {})
    if qdrant.get("ok"):
        lines.append("")
        lines.append("═══ QDRANT ═══")
        for c in qdrant.get("collections", []):
            lines.append(f"  📦 {c['name']}: {c.get('points', '?')} vectors")
    else:
        lines.append(f"🚨 Qdrant: {qdrant.get('error', 'desconocido')}")

    # Credits
    credits = health.get("credits", {})
    if credits.get("ok"):
        lines.append("")
        lines.append("═══ OPENROUTER ═══")
        lines.append(
            f"💳 ${credits.get('remaining', '?'):.2f} restantes "
            f"(uso: ${credits.get('usage', 0):.2f})"
        )
        if credits.get("remaining", 0) < 2.0:
            lines.append("⚠️ CRÍTICO: Créditos bajos — recargar ASAP")
    else:
        lines.append(f"🚨 OpenRouter: {credits.get('error', '?')}")

    # CPU hogs
    cpu = health.get("cpu", {})
    if cpu.get("hog_processes"):
        lines.append("")
        lines.append("═══ PROCESOS CPU ALTA ═══")
        for p in cpu["hog_processes"]:
            lines.append(f"🔥 {p['cmd'][:50]} — {p['cpu_pct']}%")

    # Contradictions
    if contradictions:
        lines.append("")
        lines.append("═══ ⚠️ CONTRADECIONES DETECTADAS ═══")
        for c in contradictions:
            lines.append(f"  ❓ {c}")

    # Recommendations
    lines.append("")
    lines.append("═══ RECOMENDACIONES ═══")
    recommendations = []
    if mem_pct > 80:
        recommendations.append("Liberar RAM — considerar restart de procesos pesados")
    if docker.get("unhealthy"):
        recommendations.append("Revisar containers unhealthy en docker")
    if credits.get("ok") and credits.get("remaining", 0) < 2.0:
        recommendations.append("Recargar key OpenRouter antes de gastar más")
    if cpu.get("hog_processes"):
        recommendations.append("Revisar procesos con CPU alta — posible stuck process")
    failed = health.get("failed_units", {}).get("failed", [])
    if failed:
        recommendations.append("Investigar unidades systemd fallidas")
    if not recommendations:
        recommendations.append("Todo verde — ideal para tareas nuevas")
    for r in recommendations:
        lines.append(f"  → {r}")

    lines.append("")
    lines.append("═" * 40)
    lines.append(f"🤖 Hermes proactive-scheduler v1.0")
    lines.append(f"📡 VPS Hostinger {VPS_HOST}")

    return "\n".join(lines)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def acquire_lock() -> bool:
    """Simple file lock for idempotency."""
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text().strip())
            # Check if process is still alive
            os.kill(pid, 0)
            log(f"Another instance running (PID {pid}), skipping", "WARN")
            return False
        except (ValueError, ProcessLookupError, PermissionError):
            pass  # Stale lock
    LOCK_FILE.write_text(str(os.getpid()))
    return True


def release_lock():
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def gather_health() -> dict:
    """Collect all health data."""
    log("Gathering docker status...")
    docker = check_docker()

    log("Gathering system resources...")
    resources = check_system_resources()

    log("Gathering systemd services...")
    services = check_services()

    log("Checking HTTP endpoints...")
    endpoints = check_endpoints()

    log("Checking Qdrant collections...")
    qdrant = check_qdrant()

    log("Checking OpenRouter credits...")
    credits = check_openrouter_credits()

    log("Checking CPU hogs...")
    cpu = check_cpu_intensive()

    log("Checking failed systemd units...")
    failed_units = check_systemd_failed()

    return {
        "docker": docker,
        "resources": resources,
        "services": services,
        "endpoints": endpoints,
        "qdrant": qdrant,
        "credits": credits,
        "cpu": cpu,
        "failed_units": failed_units,
    }


def send_via_hermes(message: str) -> bool:
    """Send briefing via hermes send -t telegram."""
    # Escape message for shell
    escaped = message.replace("'", "'\\''")
    rc, out, err = run_cmd(
        f"hermes send -t telegram '{escaped}'",
        timeout=30,
    )
    if rc != 0:
        log(f"hermes send failed (rc={rc}): {err}", "ERROR")
        return False
    log(f"hermes send OK: {out[:100]}")
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Hermes proactive morning briefing")
    parser.add_argument("--dry-run", action="store_true", help="Print only, don't send")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--check", action="store_true", help="Health check only (exit 0=ok)")
    parser.add_argument("--no-lock", action="store_true", help="Skip lock file")
    args = parser.parse_args()

    if not args.no_lock and not acquire_lock():
        sys.exit(0)

    try:
        log("=== Proactive Scheduler starting ===")
        health = gather_health()
        estado = load_estado()
        contradictions = detect_contradictions(estado, health) if estado else []

        if args.json:
            output = {
                "timestamp": now_cdt().isoformat(),
                "health": health,
                "contradictions": contradictions,
            }
            print(json.dumps(output, indent=2, default=str))
            sys.exit(0)

        if args.check:
            # Exit 1 if any critical issue
            all_ok = (
                health["docker"]["ok"]
                and health["resources"]["memory_pct"] < 90
                and all(s["active"] for s in health["services"].values())
            )
            sys.exit(0 if all_ok else 1)

        briefing = format_briefing(health, contradictions)

        if args.dry_run:
            print(briefing)
        else:
            # Save to log
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            log_file = LOG_DIR / f"briefing-{now_cdt().strftime('%Y%m%d-%H%M')}.txt"
            log_file.write_text(briefing, encoding="utf-8")

            # Send via Hermes
            send_via_hermes(briefing)

        log("=== Proactive Scheduler complete ===")

    finally:
        if not args.no_lock:
            release_lock()


if __name__ == "__main__":
    main()
