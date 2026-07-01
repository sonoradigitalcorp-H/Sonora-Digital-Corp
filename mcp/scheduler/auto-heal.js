/**
 * Auto-Heal System — Self-healing real
 * Cuando detecta un problema → lo fixea solo
 * Sin esperar a que un humano lo haga
 */

const http = require('http');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const GATEWAY = { host: '127.0.0.1', port: 18989 };
const LOG_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'auto-heal.log');

class AutoHeal {
  constructor() {
    this.actions = [];
    this.last_heal = null;
  }

  _log(msg) {
    const line = '[' + new Date().toISOString() + '] ' + msg + '\n';
    try { fs.appendFileSync(LOG_FILE, line); } catch {}
  }

  _call(tool, params) {
    return new Promise(r => {
      const data = JSON.stringify({ tool, params });
      const req = http.request({ hostname: GATEWAY.host, port: GATEWAY.port, path: '/api/call', method: 'POST',
        headers: { 'Content-Type': 'application/json' }, timeout: 30000 }, res => {
        let d = ''; res.on('data', c => d += c); res.on('end', () => { try { r(JSON.parse(d)); } catch { r({ raw: d }); } });
      });
      req.on('error', e => r({ error: e.message }));
      req.write(data); req.end();
    });
  }

  async heal() {
    this._log('=== Auto-Heal Run ===');
    this.actions = [];

    // 1. Check gateway
    try {
      const h = await this._call('health_all', {});
      if (!h || h.error) {
        this._log('Gateway down, attempting restart...');
        try {
          execSync('sudo systemctl restart sonora-mcp-gateway.service', { timeout: 10000 });
          this.actions.push({ action: 'restart_gateway', status: 'done' });
          this._log('Gateway restarted');
        } catch (e) {
          this.actions.push({ action: 'restart_gateway', status: 'failed', error: e.message });
        }
      }
    } catch {}

    // 2. Check Ollama
    try {
      const r = await new Promise((resolve) => {
        const req = http.get({ hostname: '127.0.0.1', port: 11434, path: '/api/tags', timeout: 5000 }, res => {
          let d = ''; res.on('data', c => d += c); res.on('end', () => resolve(res.statusCode === 200));
        });
        req.on('error', () => resolve(false));
      });
      if (!r) {
        this._log('Ollama down, attempting restart...');
        try {
          execSync('ollama serve &', { timeout: 5000 });
          this.actions.push({ action: 'restart_ollama', status: 'done' });
        } catch (e) {
          this.actions.push({ action: 'restart_ollama', status: 'failed' });
        }
      }
    } catch {}

    // 3. Check disk
    try {
      const disk = execSync('df / | tail -1 | awk \'{print $5}\'', { encoding: 'utf-8', timeout: 3000 }).trim();
      const pct = parseInt(disk);
      if (pct > 85) {
        this._log('Disk at ' + pct + '%, cleaning old logs...');
        try {
          execSync('find /home/ubuntu/sonora-digital-corp/state/logs -name "*.log" -mtime +3 -delete', { timeout: 5000 });
          this.actions.push({ action: 'clean_logs', status: 'done' });
        } catch (e) {
          this.actions.push({ action: 'clean_logs', status: 'failed' });
        }
      }
    } catch {}

    // 4. Send alert to Telegram if heal happened
    if (this.actions.length > 0) {
      try {
        const msg = '🛠️ Auto-Heal: ' + this.actions.map(a => a.action + '=' + a.status).join(', ');
        await this._call('hermes_telegram_send', { chat_id: '5738935134', text: msg });
      } catch {}
    }

    this.last_heal = new Date().toISOString();
    this._log('Heal done: ' + this.actions.length + ' actions');
    return { timestamp: this.last_heal, actions: this.actions };
  }

  getHistory() {
    try {
      if (!fs.existsSync(LOG_FILE)) return [];
      return fs.readFileSync(LOG_FILE, 'utf-8').trim().split('\n').filter(Boolean).slice(-30);
    } catch { return []; }
  }
}

const healer = new AutoHeal();
module.exports = { AutoHeal, healer };
