#!/usr/bin/env python3
"""
ABE DAEMON 24/7 — Monitoreo, auto-fix, reportes, y entrega continua
Corre como systemd service. Consume ~30MB RAM. Nunca duerme.
"""
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'abe-daemon.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger('abe-daemon')

# Config
TOKEN = os.environ.get('ABE_TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('ABE_TELEGRAM_CHAT') or '5738935134'
JARVIS_URL = 'http://localhost:5174'
ABE_SERVICE_URL = 'http://127.0.0.1:5180'
CYCLE_10M = 600
CYCLE_6H = 21600
CYCLE_24H = 86400

class AbeDaemon:
    def __init__(self):
        self.last_6h = 0
        self.last_24h = 0
        self.cycle_count = 0

    def send_alert(self, message):
        try:
            requests.post(
                f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                json={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'},
                timeout=10
            )
        except Exception as e:
            log.error(f"Alert failed: {e}")

    def healthcheck(self):
        results = {}
        # RAM
        free = subprocess.run(['free', '-m'], capture_output=True, text=True, timeout=5)
        for line in free.stdout.split('\n'):
            if 'Mem:' in line:
                parts = line.split()
                results['ram_free'] = int(parts[6])
                results['ram_total'] = int(parts[1])

        # JARVIS API
        try:
            r = requests.get(f'{JARVIS_URL}/api/status', timeout=5)
            results['jarvis'] = r.status_code == 200
        except Exception:
            results['jarvis'] = False

        # Docker containers
        try:
            r = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'],
                             capture_output=True, text=True, timeout=10)
            results['containers'] = [c for c in r.stdout.strip().split('\n') if c]
            results['container_count'] = len(results['containers'])
        except Exception:
            results['containers'] = []
            results['container_count'] = 0

        # Bot Telegram
        try:
            r = requests.get(f'https://api.telegram.org/bot{TOKEN}/getMe', timeout=10)
            results['bot_ok'] = r.json().get('ok', False)
        except Exception:
            results['bot_ok'] = False

        # ABE Service
        try:
            r = requests.get(f'{ABE_SERVICE_URL}/api/health', timeout=5)
            results['abe_service'] = r.status_code == 200
        except Exception:
            results['abe_service'] = False

        return results

    def auto_fix(self, status):
        fixes = []
        # RAM crítica
        if status.get('ram_free', 0) < 200:
            log.warning(f"RAM crítica: {status['ram_free']}MB — matando procesos basura")
            for proc in ['warp-svc']:
                subprocess.run(['pkill', '-f', proc], capture_output=True, timeout=5)
                fixes.append(f"killed {proc}")

        # JARVIS caído
        if not status.get('jarvis', False):
            log.warning("JARVIS caído — intentando restart")
            # Try docker restart first
            subprocess.run(['docker', 'restart', 'jarvis-neo4j', 'hermes_api'],
                         capture_output=True, timeout=30)
            fixes.append("restarted containers")

        # Bot caído
        if not status.get('bot_ok', False):
            log.error("BOT TELEGRAM MUERTO — necesita regenerar token")
            self.send_alert("⚠️ *ALERTA CRÍTICA*: El bot de Telegram no responde. "
                          "Regenera token en BotFather.")
            fixes.append("ALERT: bot token dead")

        # ABE Service caído
        if not status.get('abe_service', False):
            log.warning("ABE Service caído — intentando restart via systemd")
            subprocess.run(['systemctl', '--user', 'restart', 'abe-service'],
                         capture_output=True, timeout=30)
            fixes.append("restarted abe-service")

        return fixes

    def push_report(self):
        try:
            r = requests.get(f'{JARVIS_URL}/api/abe/dashboard/ceo', timeout=10)
            data = r.json()
            message = (
                f"📊 *ABE MUSIC — Reporte Automático*\n"
                f"⏱ {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
                f"🎤 Artistas: {data.get('total_artists', '?')}\n"
                f"💿 Releases: {data.get('total_releases', '?')}\n"
                f"📊 Streams: {data.get('total_streams', 0):,}\n"
                f"💰 Revenue: ${data.get('total_revenue', 0):,.2f}\n\n"
                f"[Dashboard]({JARVIS_URL}/static/dashboard-abe.html)"
            )
            self.send_alert(message)
            log.info("Report pushed to Telegram")
        except Exception as e:
            log.error(f"Report push failed: {e}")

    def daily_tasks(self):
        log.info("Running daily tasks...")
        # Run ABE tests
        result = subprocess.run(
            ['python3', '-m', 'pytest', 'tests/', '-k', 'abe', '-q'],
            capture_output=True, text=True, timeout=120,
            cwd=BASE_DIR
        )
        log.info(f"Tests: {result.stdout.strip()}")

        # Git commit + push
        subprocess.run(['git', 'add', '-A'], capture_output=True, timeout=30, cwd=BASE_DIR)
        subprocess.run(
            ['git', 'commit', '-m', f'auto: daily update {datetime.now().strftime("%Y-%m-%d")}'],
            capture_output=True, timeout=30, cwd=BASE_DIR
        )
        subprocess.run(['git', 'push'], capture_output=True, timeout=60, cwd=BASE_DIR)
        log.info("Daily commit + push done")

    def spotify_sync(self):
        pipeline = BASE_DIR / 'clients' / 'abe-music' / 'pipeline.py'
        if not pipeline.exists():
            log.warning("Spotify pipeline not found, skipping sync")
            return
        try:
            env = os.environ.copy()
            result = subprocess.run(
                ['python3', str(pipeline)],
                capture_output=True, text=True, timeout=120,
                cwd=BASE_DIR, env=env
            )
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    log.info(f"[pipeline] {line.strip()}")
            if result.returncode != 0:
                log.error(f"Spotify pipeline failed: {result.stderr.strip()[:200]}")
            else:
                log.info("Spotify sync complete")
        except Exception as e:
            log.error(f"Spotify sync error: {e}")

    def run_cycle(self, status):
        log.info(f"=== Cycle #{self.cycle_count} ===")
        log.info(f"RAM: {status.get('ram_free', '?')}MB | "
                f"Containers: {status.get('container_count', '?')} | "
                f"JARVIS: {'✅' if status.get('jarvis') else '❌'} | "
                f"ABE: {'✅' if status.get('abe_service') else '❌'} | "
                f"Bot: {'✅' if status.get('bot_ok') else '❌'}")

        # Auto-fix
        fixes = self.auto_fix(status)
        if fixes:
            log.info(f"Fixes applied: {', '.join(fixes)}")

        # 6h tasks: Spotify sync + report
        now = time.time()
        if now - self.last_6h > CYCLE_6H:
            self.spotify_sync()
            self.push_report()
            self.last_6h = now

        # 24h tasks
        if now - self.last_24h > CYCLE_24H:
            self.daily_tasks()
            self.last_24h = now

        self.cycle_count += 1

    def run(self):
        log.info("🚀 ABE Daemon started")
        self.send_alert("🚀 *ABE Daemon 24/7 activado*\n"
                       "Monitoreando JARVIS + Telegram cada 10 min")
        self.last_6h = time.time()
        self.last_24h = time.time()

        while True:
            try:
                status = self.healthcheck()
                self.run_cycle(status)
                time.sleep(CYCLE_10M)
            except KeyboardInterrupt:
                log.info("Daemon stopped by user")
                break
            except Exception as e:
                log.error(f"Cycle error: {e}")
                self.send_alert(f"⚠️ Daemon error: {str(e)[:100]}")
                time.sleep(CYCLE_10M)

if __name__ == '__main__':
    daemon = AbeDaemon()
    daemon.run()
