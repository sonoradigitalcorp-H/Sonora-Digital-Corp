#!/usr/bin/env python3
"""Mystic Shield Audit Logger — Registra toda actividad sospechosa 24/7.

Se ejecuta vía cron cada hora para:
1. Revisar logs del bot por intentos de ataque
2. Actualizar banned users
3. Generar reportes de seguridad
4. Alertar a César si hay amenazas serias
"""

import os
import re
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("shield-audit")

LOG_DIR = Path("/var/log/sdc")
SHIELD_DB = Path(__file__).parent.parent.parent.parent / "ops" / "state" / "shield.json"
REPORT_DIR = Path(__file__).parent.parent.parent.parent / "ops" / "state" / "reports"

THREAT_PATTERNS = [
    r"Shield blocked",
    r"Attempted SQL injection",
    r"Attempted XSS",
    r"Attempted command injection",
    r"Spam detected",
    r"Rate limit exceeded",
    r"Prompt injection attempt",
]

def scan_logs():
    """Scan bot logs for security events."""
    events = []
    bot_log = LOG_DIR / "aztrotech-bot.log"
    
    if not bot_log.exists():
        return events
    
    try:
        with open(bot_log) as f:
            for line in f:
                for pattern in THREAT_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        events.append({
                            "timestamp": line[:19].strip(),
                            "event": pattern,
                            "raw": line.strip()[:200],
                        })
    except Exception as e:
        logger.error(f"Log scan error: {e}")
    
    return events

def generate_report(events):
    """Generate security report."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_events": len(events),
        "threat_summary": {},
        "events": events[-50:],  # Last 50 events
    }
    
    for event in events:
        threat = event["event"]
        report["threat_summary"][threat] = report["threat_summary"].get(threat, 0) + 1
    
    report_file = REPORT_DIR / f"shield-audit-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    
    return report

def main():
    logger.info("🛡️ Mystic Shield Audit running...")
    
    events = scan_logs()
    report = generate_report(events)
    
    logger.info(f"Events found: {report['total_events']}")
    if report["threat_summary"]:
        logger.info(f"Threats: {json.dumps(report['threat_summary'])}")
    
    # Alert if serious threats
    serious = sum(1 for e in events if "Shield blocked" in e["event"])
    if serious > 10:
        logger.warning(f"⚠️ {serious} shield blocks in last hour - possible attack")
    
    return report

if __name__ == "__main__":
    main()