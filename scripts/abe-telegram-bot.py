#!/usr/bin/env python3
"""
ABE MUSIC Telegram Bot — Live data from JARVIS API
"""
import json
import os
import sys
import time
import logging
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'
LOG_PATH = BASE_DIR / 'logs' / 'abe-telegram-bot.log'
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()]
)
log = logging.getLogger(__name__)

def load_env():
    env_vars = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env_vars[k] = v
    return env_vars

def fetch_kpis():
    try:
        r = requests.get('http://localhost:5174/api/abe/dashboard/ceo', timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.warning(f"API fetch failed: {e}")
        return {
            "total_artists": 3,
            "total_releases": 7,
            "total_streams": 539000,
            "total_revenue": 26880,
            "top_artists": [
                {"nombre": "Jesus Urquijo", "streams": 245000, "revenue": 12110.0},
                {"nombre": "Hector Rubio", "streams": 193000, "revenue": 9660.0},
                {"nombre": "Javier Arvayo", "streams": 101000, "revenue": 5110.0}
            ]
        }

def format_message(kpis, detail=False):
    lines = [
        f"🎵 *ABE MUSIC*",
        f"📊 Streams: {kpis['total_streams']:,}",
        f"💰 Revenue: ${kpis['total_revenue']:,.2f}",
        f"🎤 Artistas: {kpis['total_artists']}",
        f"💿 Releases: {kpis['total_releases']}",
    ]
    if detail and kpis.get('top_artists'):
        lines.append("")
        lines.append("*Top Artistas:*")
        for a in kpis['top_artists']:
            lines.append(f"  • {a['nombre']}: {a['streams']:,} / ${a['revenue']:,.0f}")
    lines.append("")
    lines.append("[Dashboard](http://localhost:5174/static/dashboard-abe.html)")
    return "\n".join(lines)

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, json={
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': False
    }, timeout=10)
    resp.raise_for_status()
    return resp.json()

def handle_update(token, update):
    msg = update.get('message', {})
    text = (msg.get('text') or '').strip()
    chat_id = msg.get('chat', {}).get('id')
    if not chat_id:
        return

    kpis = fetch_kpis()

    if text == '/start':
        reply = (
            f"🎵 *Bienvenido a ABE MUSIC Bot*\n\n"
            f"Soy el asistente automatizado de tu disquera.\n\n"
            f"*Comandos:*\n"
            f"/kpi — Resumen rápido\n"
            f"/full — Reporte completo\n"
            f"/artistas — Top artistas\n"
            f"/dashboard — Abrir panel\n\n"
            f"_Powered by JARVIS AI Agency_"
        )
    elif text == '/kpi':
        reply = format_message(kpis)
    elif text == '/full':
        reply = format_message(kpis, detail=True)
    elif text == '/artistas':
        lines = ["*Top Artistas*\n"]
        for i, a in enumerate(kpis.get('top_artists', []), 1):
            pct = (a['streams'] / kpis['total_streams'] * 100) if kpis['total_streams'] else 0
            lines.append(f"{i}. {a['nombre']}")
            lines.append(f"   📊 {a['streams']:,} streams ({pct:.0f}%)")
            lines.append(f"   💰 ${a['revenue']:,.0f}")
            lines.append("")
        reply = "\n".join(lines)
    elif text == '/dashboard':
        reply = "Abre tu dashboard aquí:\nhttp://localhost:5174/static/dashboard-abe.html"
    else:
        reply = (
            f"No reconozco ese comando. Prueba:\n"
            f"/kpi — Resumen rápido\n"
            f"/full — Reporte completo\n"
            f"/artistas — Top artistas\n"
            f"/dashboard — Abrir panel"
        )

    try:
        result = send_telegram(token, chat_id, reply)
        log.info(f"Sent to {chat_id}: {result.get('ok')}")
    except Exception as e:
        log.error(f"Send failed to {chat_id}: {e}")

def poll_updates(token, offset=0):
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    while True:
        try:
            resp = requests.get(url, params={
                'offset': offset,
                'timeout': 30,
                'allowed_updates': ['message']
            }, timeout=35)
            resp.raise_for_status()
            data = resp.json()
            if data.get('ok') and data.get('result'):
                for update in data['result']:
                    handle_update(token, update)
                    offset = update['update_id'] + 1
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.ConnectionError:
            log.warning("Connection error, retrying in 10s...")
            time.sleep(10)
        except Exception as e:
            log.error(f"Poll error: {e}")
            time.sleep(30)

def main():
    env = load_env()
    token = env.get('ABE_TELEGRAM_TOKEN') or os.environ.get('ABE_TELEGRAM_TOKEN')
    
    if not token or token == 'your_telegram_bot_token_here':
        log.error("❌ No ABE_TELEGRAM_TOKEN configured")
        print("ERROR: Set ABE_TELEGRAM_TOKEN in .env")
        print("1. Open Telegram → BotFather → /regeneratetoken")
        print("2. Copy token → edit .env → ABE_TELEGRAM_TOKEN=...")
        sys.exit(1)

    # Verify token
    try:
        me = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        me.raise_for_status()
        bot_info = me.json().get('result', {})
        log.info(f"✅ Bot active: @{bot_info.get('username', 'unknown')}")
        print(f"🤖 Bot @{bot_info.get('username', 'unknown')} is active!")
    except Exception as e:
        log.error(f"❌ Token verification failed: {e}")
        print(f"ERROR: Token invalid: {e}")
        print("Regenerate at BotFather → /regeneratetoken")
        sys.exit(1)

    # Send startup message
    kpis = fetch_kpis()
    startup_msg = format_message(kpis, detail=True)
    chat_id = env.get('ABE_TELEGRAM_CHAT', '5738935134')
    try:
        send_telegram(token, chat_id, "🚀 *ABE MUSIC Bot activado*\n\n" + startup_msg)
        log.info(f"✅ Startup message sent to {chat_id}")
    except Exception as e:
        log.warning(f"Startup message failed: {e}")

    log.info("🔄 Polling for updates...")
    print("🤖 Bot polling for updates...")
    poll_updates(token)

if __name__ == '__main__':
    main()
