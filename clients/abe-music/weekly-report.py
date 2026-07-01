#!/usr/bin/env python3
"""
ABE Music — Weekly Report Sender
Sends an automated KPI report to Abraham every Monday via Telegram.
Run via cron: 0 9 * * 1 /home/ubuntu/sdc/scripts/weekly-report.py
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'
LOG_PATH = BASE_DIR / 'logs' / 'weekly-report.log'
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()]
)
log = logging.getLogger(__name__)

def load_env():
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k] = v
    return env

def fetch_kpis():
    try:
        r = requests.get('http://localhost:8080/api/abe/dashboard/ceo', timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.warning(f"API failed: {e}")
        return None

def fetch_artists():
    try:
        r = requests.get('http://localhost:8080/api/abe/artists', timeout=5)
        r.raise_for_status()
        return r.json().get('artists', [])
    except Exception as e:
        log.warning(f"Artists API failed: {e}")
        return []

def format_report(kpis, artists):
    lines = [
        "📊 *ABE MUSIC — Reporte Semanal*",
        "",
        f"📅 *Resumen*",
        f"🎤 Artistas: {kpis['total_artists']}",
        f"💿 Releases: {kpis['total_releases']}",
        f"📊 Streams totales: {kpis['total_streams']:,}",
        f"💰 Revenue estimado: ${kpis['total_revenue']:,.2f}",
        "",
        "*Top Artistas:*",
    ]
    for a in kpis.get('top_artists', []):
        pct = (a['streams'] / kpis['total_streams'] * 100) if kpis['total_streams'] else 0
        lines.append(f"  • {a['nombre']}: {a['streams']:,} ({pct:.1f}%)")
    lines.append("")
    lines.append("🔗 https://sonoradigitalcorp.com/")
    return "\n".join(lines)

def send_telegram(token, chat_id, text):
    r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }, timeout=10)
    r.raise_for_status()
    return r.json()

def main():
    env = load_env()
    token = env.get('ABE_TELEGRAM_TOKEN')
    chat_id = env.get('ABE_TELEGRAM_CHAT', '5738935134')

    if not token:
        log.error("No ABE_TELEGRAM_TOKEN in .env")
        sys.exit(1)

    kpis = fetch_kpis()
    artists = fetch_artists()
    if not kpis:
        log.error("Could not fetch KPIs")
        sys.exit(1)

    report = format_report(kpis, artists)
    try:
        send_telegram(token, chat_id, report)
        log.info(f"Weekly report sent to {chat_id}")
    except Exception as e:
        log.error(f"Failed to send: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
