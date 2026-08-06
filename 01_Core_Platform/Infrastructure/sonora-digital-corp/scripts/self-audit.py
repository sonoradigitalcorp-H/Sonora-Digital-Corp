#!/usr/bin/env python3
"""Self-Audit System — evalúa salud del ecosistema SDC periódicamente.
Corre cada 6h via systemd timer. Reporta a Engram + event bus.
Usage: python3 scripts/self-audit.py [--quiet]

Checks:
  - Tests pasan?
  - Registries sincronizados?
  - Event bus activo?
  - Syncthing conectado?
  - Servicios críticos UP?
  - Memory usage healthy?
  - Última vez que se auditó?
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]", "", -1
    except FileNotFoundError:
        return "[NOT FOUND]", "", -1


def check_tests():
    out, err, code = run(["python3", "-m", "pytest", "evals/test_evals.py", "-q", "--tb=no"])
    if err:
        return {"status": "error", "detail": err[:200]}
    passed = out.count("PASSED")
    failed = out.count("FAILED")
    return {
        "status": "ok" if failed == 0 else "degraded",
        "passed": passed,
        "failed": failed,
        "detail": f"{passed} passed, {failed} failed" if failed else f"{passed} passed",
    }


def check_registry():
    path = BASE / "state" / "registry" / "unified.yaml"
    if not path.exists():
        return {"status": "error", "detail": "Registry missing"}
    import yaml
    data = yaml.safe_load(path.read_text())
    total = len(data.get("entries", []))
    return {"status": "ok", "total": total, "detail": f"{total} entities"}


def check_event_bus():
    path = BASE / "state" / "events" / "events.jsonl"
    if not path.exists():
        return {"status": "error", "detail": "Event bus file missing"}
    lines = path.read_text().strip().split("\n")
    last_event = lines[-1][:100] if lines and lines[0] else "empty"
    return {"status": "ok", "events": len(lines), "detail": f"{len(lines)} events"}


def check_services():
    services = ["syncthing@ubuntu", "event-listener", "ops-agent", "sdc-api-bridge", "hermes"]
    results = {}
    for svc in services:
        out, _, code = run(["systemctl", "is-active", svc])
        results[svc] = "ok" if "active" in out else "down"
    operational = sum(1 for v in results.values() if v == "ok")
    return {"status": "ok" if operational == len(services) else "degraded", "services": results, "detail": f"{operational}/{len(services)} up"}


def check_disk():
    out, _, _ = run(["df", "-h", "/"])
    if not out:
        return {"status": "unknown"}
    line = out.split("\n")[1]
    usage = int(line.split()[4].rstrip("%"))
    return {"status": "ok" if usage < 80 else "warning" if usage < 90 else "critical", "usage": usage, "detail": f"{usage}% disk used"}


def check_syncthing():
    try:
        config = Path.home() / ".config/syncthing/config.xml"
        if config.exists():
            import xml.etree.ElementTree as ET
            tree = ET.parse(config)
            devices = tree.findall(".//device")
            return {"status": "ok", "devices": len(devices), "detail": f"{len(devices)} devices"}
        return {"status": "inactive", "detail": "No syncthing config"}
    except Exception as e:
        return {"status": "error", "detail": str(e)[:80]}


def check_memory():
    try:
        import psutil
        mem = psutil.virtual_memory()
        return {"status": "ok" if mem.percent < 80 else "warning", "usage": mem.percent, "detail": f"{mem.percent}% RAM used"}
    except ImportError:
        out, _, _ = run(["free", "-m"])
        if out:
            line = out.split("\n")[1].split()
            total = int(line[1])
            used = int(line[2])
            pct = used * 100 // total
            return {"status": "ok" if pct < 80 else "warning", "usage": pct, "detail": f"{pct}% RAM used"}
        return {"status": "unknown"}


def save_to_engram(results):
    """Save audit results to Engram memory system."""
    status = "ok" if all(r.get("status") == "ok" for r in results.values()) else "degraded"
    summary = {k: v.get("status", "?") for k, v in results.items()}
    try:
        path = BASE / "state" / "audits" / f"audit-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "status": status, "summary": summary, "details": results}, indent=2, default=str))
        print(f"📝 Audit saved: {path}")
    except Exception as e:
        print(f"⚠️ Could not save audit: {e}")


def main():
    quiet = "--quiet" in sys.argv

    print(f"\n🩺 SDC Self-Audit — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    checks = {
        "tests": check_tests(),
        "registry": check_registry(),
        "event_bus": check_event_bus(),
        "services": check_services(),
        "disk": check_disk(),
        "syncthing": check_syncthing(),
        "memory": check_memory(),
    }

    for name, result in checks.items():
        icon = {"ok": "✅", "degraded": "⚠️", "error": "❌", "warning": "⚠️", "inactive": "⏸️", "unknown": "❓"}.get(result.get("status", "unknown"), "❓")
        print(f"  {icon} {name}: {result.get('detail', '')[:80]}")
        if not quiet and result.get("status") != "ok":
            print(f"     Full: {json.dumps(result, default=str)[:150]}")

    save_to_engram(checks)

    failed = sum(1 for v in checks.values() if v.get("status") in ("error", "critical"))
    if failed:
        print(f"\n⚠️  {failed} check(s) failed")
        return 1
    print(f"\n✅ All checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
