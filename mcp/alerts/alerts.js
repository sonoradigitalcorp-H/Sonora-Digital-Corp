/**
 * Alerts System — Proactive health monitoring + notifications
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const { execSync } = require('child_process');

const ALERTS_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'alerts.jsonl');
const GATEWAY = { host: '127.0.0.1', port: 18989 };
const EVENTS_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'events.jsonl');

class AlertSystem {
  constructor() {
    this.rules = [
      { id: 'gateway_down', check: async () => {
        try { const r = await fetch('http://127.0.0.1:18989/api/health'); return r.ok ? null : 'Gateway no responde'; }
        catch { return 'Gateway no accesible'; }
      }},
      { id: 'ollama_down', check: async () => {
        try { const r = await fetch('http://127.0.0.1:11434/api/tags'); return r.ok ? null : 'Ollama no responde'; }
        catch { return 'Ollama no accesible'; }
      }},
      { id: 'disk_space', check: async () => {
        try {
          const r = execSync('df / | tail -1 | awk \'{print $5}\'', { encoding: 'utf-8', timeout: 3000 }).trim();
          const pct = parseInt(r);
          return pct > 85 ? `Disco al ${pct}%` : null;
        } catch { return null; }
      }},
      { id: 'memory', check: async () => {
        try {
          const r = execSync('free -m | grep Mem | awk \'{print $7}\'', { encoding: 'utf-8', timeout: 3000 }).trim();
          const mem = parseInt(r);
          return mem < 500 ? `Solo ${mem}MB RAM libre` : null;
        } catch { return null; }
      }},
    ];
  }

  _log(alert) {
    const entry = JSON.stringify({ ...alert, timestamp: new Date().toISOString() }) + '\n';
    try { fs.appendFileSync(ALERTS_FILE, entry); } catch {}
    try { fs.appendFileSync(EVENTS_FILE, entry.replace('alerts', 'alert_triggered')); } catch {}
  }

  async checkAll() {
    const alerts = [];
    for (const rule of this.rules) {
      try {
        const msg = await rule.check();
        if (msg) {
          const alert = { rule: rule.id, message: msg, severity: 'warning' };
          alerts.push(alert);
          this._log(alert);
        }
      } catch {}
    }
    return { timestamp: new Date().toISOString(), alerts, count: alerts.length };
  }

  getHistory() {
    try {
      if (!fs.existsSync(ALERTS_FILE)) return [];
      return fs.readFileSync(ALERTS_FILE, 'utf-8').trim().split('\n').filter(Boolean).slice(-50).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
    } catch { return []; }
  }
}

// Polyfill for node fetch if needed
global.fetch = global.fetch || ((url) => new Promise((resolve, reject) => {
  const u = new URL(url);
  const req = http.get({ hostname: u.hostname, port: u.port, path: u.pathname, timeout: 5000 }, res => {
    let d = ''; res.on('data', c => d += c);
    res.on('end', () => resolve({ ok: res.statusCode < 400, status: res.statusCode, json: () => Promise.resolve(JSON.parse(d)) }));
  });
  req.on('error', reject);
}));

const alerts = new AlertSystem();
module.exports = { AlertSystem, alerts };
