const fs = require('fs');
const path = require('path');
const http = require('http');

const GATEWAY = { host: '127.0.0.1', port: 18989 };
const SCHEDULE_FILE = path.join(__dirname, '..', '..', 'config', 'schedule.json');
const LOG_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'scheduler.log');

class Scheduler {
  constructor() { this.tasks = []; this._load(); }

  _load() {
    try {
      if (fs.existsSync(SCHEDULE_FILE)) {
        const data = JSON.parse(fs.readFileSync(SCHEDULE_FILE, 'utf-8'));
        this.tasks = data.tasks || [];
      }
    } catch {}
  }

  _save() {
    try { fs.writeFileSync(SCHEDULE_FILE, JSON.stringify({ version: '1.0.0', tasks: this.tasks }, null, 2)); } catch {}
  }

  _log(msg) {
    const line = '[' + new Date().toISOString() + '] ' + msg + '\n';
    try { fs.appendFileSync(LOG_FILE, line); } catch {}
  }

  _call(tool, params) {
    return new Promise(r => {
      const data = JSON.stringify({ tool, params });
      const req = http.request({ hostname: GATEWAY.host, port: GATEWAY.port, path: '/api/call', method: 'POST',
        headers: { 'Content-Type': 'application/json' }, timeout: 60000 }, res => {
        let d = ''; res.on('data', c => d += c); res.on('end', () => { try { r(JSON.parse(d)); } catch { r({ raw: d }); } });
      });
      req.on('error', e => r({ error: e.message }));
      req.write(data); req.end();
    });
  }

  add(task) {
    this.tasks.push({
      id: 'task-' + Date.now() + '-' + Math.random().toString(36).slice(2, 6),
      name: task.name, schedule: task.schedule || null,
      trigger_event: task.trigger_event || null,
      workflow: task.workflow || null, tool: task.tool || null,
      params: task.params || {}, enabled: true,
      created_at: new Date().toISOString(), last_run: null,
    });
    this._save();
    return this.tasks[this.tasks.length - 1];
  }

  remove(id) { this.tasks = this.tasks.filter(t => t.id !== id); this._save(); }
  list() { return this.tasks; }

  async tick() {
    const now = new Date();
    for (const task of this.tasks) {
      if (!task.enabled) continue;
      if (task.schedule && this._matches(now, task.schedule)) {
        this._log('Running scheduled: ' + task.name);
        const result = task.workflow
          ? await this._call('workflow_run', { name: task.workflow, context: task.params })
          : task.tool
            ? await this._call(task.tool, task.params)
            : null;
        task.last_run = now.toISOString();
        task.last_result = result && result.status ? result.status : 'error';
        this._log('  Result: ' + task.last_result);
        this._save();
      }
    }
  }

  async onEvent(eventType, payload) {
    for (const task of this.tasks) {
      if (!task.enabled) continue;
      if (task.trigger_event === eventType) {
        this._log('Event triggered: ' + task.name + ' (' + eventType + ')');
        const ctx = Object.assign({}, task.params, payload);
        const result = task.workflow
          ? await this._call('workflow_run', { name: task.workflow, context: ctx })
          : task.tool
            ? await this._call(task.tool, ctx)
            : null;
        task.last_run = new Date().toISOString();
        task.last_result = result && result.status ? result.status : 'error';
        this._save();
      }
    }
  }

  _matches(now, cronExpr) {
    const parts = cronExpr.split(' ');
    if (parts.length !== 5) return false;
    const [min, hour, dom, mon, dow] = parts;
    if (min.includes('/')) { const parts = min.split('/'); const n = parseInt(parts[1]); if (now.getMinutes() % n !== 0) return false; }
    else if (min !== '*' && parseInt(min) !== now.getMinutes()) return false;
    if (hour.includes('/')) { const parts = hour.split('/'); const n = parseInt(parts[1]); if (now.getHours() % n !== 0) return false; }
    else if (hour !== '*' && parseInt(hour) !== now.getHours()) return false;
    if (dom !== '*' && parseInt(dom) !== now.getDate()) return false;
    if (mon !== '*' && parseInt(mon) !== now.getMonth() + 1) return false;
    if (dow !== '*' && parseInt(dow) !== now.getDay()) return false;
    return true;
  }
}

const scheduler = new Scheduler();
module.exports = { Scheduler, scheduler };
