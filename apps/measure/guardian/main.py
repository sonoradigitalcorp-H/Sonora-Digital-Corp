"""Truth Guardian — Entry point que coordina drift scanning, health checks, compliance, y alertas [FR7-FR11]"""
import json
import logging
import os
import signal
import sys
import threading
import time
from pathlib import Path

from . import drift_scanner, health_checker, compliance_auditor, status_api, telegram_alerter

EMIT_SCRIPT = Path(__file__).resolve().parent.parent.parent / "scripts" / "emit-event.py"

LOG_FILE = Path(__file__).resolve().parent.parent.parent / "logs" / "guardian.log"

handlers = [logging.StreamHandler()]
try:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(LOG_FILE)
    handlers.append(fh)
except PermissionError:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=handlers)
log = logging.getLogger("guardian")

INTERVAL = int(os.environ.get("GUARDIAN_INTERVAL", "60"))
STATUS_PORT = int(os.environ.get("GUARDIAN_PORT", "8088"))
STATUS_HOST = os.environ.get("GUARDIAN_HOST", "127.0.0.1")
running = True


def signal_handler(sig, frame):
    global running
    log.info("Shutting down...")
    running = False


def drift_loop():
    """Loop principal: scan, check, alert"""
    global running
    last_alerts = {}

    while running:
        try:
            # Drift scan
            drifts = drift_scanner.scan()
            if drifts:
                drift_key = tuple(sorted([d["detail"] for d in drifts]))
                if drift_key != last_alerts.get("drift"):
                    msg = telegram_alerter.format_drift_alert(drifts)
                    result = telegram_alerter.send_alert(msg)
                    log.warning(f"Drift detected: {len(drifts)} issues — alert: {result['status']}")
                    last_alerts["drift"] = drift_key
                    for d in drifts:
                        log.warning(f"  [{d['type']}] {d['detail']}")

                    try:
                        import subprocess
                        subprocess.run(
                            ["python3", str(EMIT_SCRIPT),
                             "--event", "incident.detected",
                             "--kernel", "verification",
                             "--agent", "truth-guardian",
                             "--subject-type", "system",
                             "--subject-id", "vps",
                             "--payload", json.dumps({"drifts": drifts})],
                            capture_output=True, timeout=5
                        )
                    except Exception:
                        pass
            else:
                last_alerts.pop("drift", None)

            # Health check
            health = health_checker.check_all()
            unhealthy = [h for h in health if h["status"] == "unhealthy"]
            if unhealthy:
                uk = tuple(sorted([u.get("target", u.get("url", "")) for u in unhealthy]))
                if uk != last_alerts.get("health"):
                    msg = telegram_alerter.format_health_alert(unhealthy)
                    result = telegram_alerter.send_alert(msg)
                    log.warning(f"Unhealthy services: {len(unhealthy)} — alert: {result['status']}")
                    last_alerts["health"] = uk
                    for u in unhealthy:
                        log.warning(f"  [DOWN] {u.get('target', u.get('url', 'unknown'))}")
            else:
                last_alerts.pop("health", None)

            # Compliance (cada 10 ciclos)
            if int(time.time()) % (INTERVAL * 10) < INTERVAL:
                violations = compliance_auditor.run_all()
                if violations:
                    for v in violations:
                        log.warning(f"[compliance] {v['rule']}: {v['detail']}")

        except Exception as e:
            log.error(f"Loop error: {e}", exc_info=True)

        time.sleep(INTERVAL)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    log.info(f"Truth Guardian starting (interval={INTERVAL}s, status={STATUS_HOST}:{STATUS_PORT})")

    try:
        import subprocess
        subprocess.run(
            ["python3", str(Path(__file__).resolve().parent.parent.parent / "scripts" / "emit-event.py"),
             "--event", "session.started",
             "--kernel", "verification",
             "--agent", "truth-guardian",
             "--subject-type", "service",
             "--subject-id", "truth-guardian",
             "--payload", json.dumps({"interval": INTERVAL})],
            capture_output=True, timeout=5
        )
    except Exception:
        pass

    result = telegram_alerter.send_alert("🟢 Truth Guardian iniciado")
    log.info(f"Startup alert: {result['status']}")

    drift_thread = threading.Thread(target=drift_loop, daemon=True)
    drift_thread.start()

    status_api.start(port=STATUS_PORT, host=STATUS_HOST)


if __name__ == "__main__":
    main()
