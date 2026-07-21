const http = require('http');
const GATEWAY_HOST = '127.0.0.1';
const GATEWAY_PORT = 18989;

class SwarmEngine {
  constructor() {
    this.swarms = new Map();
    this.history = [];
  }

  _call(tool, params) {
    return new Promise((resolve) => {
      const data = JSON.stringify({ tool, params });
      const req = http.request({ hostname: GATEWAY_HOST, port: GATEWAY_PORT, path: '/api/call', method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Content-Length': data.length }, timeout: 60000 }, (res) => {
        let d = ''; res.on('data', c => d += c); res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ raw: d }); } });
      });
      req.on('error', e => resolve({ error: e.message }));
      req.write(data); req.end();
    });
  }

  async run(name, agents, task, context = {}) {
    const swarmId = `swarm-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
    const entry = { id: swarmId, name, agents, task, start: Date.now(), status: 'running', results: {} };

    const results = {};
    const promises = agents.map(async (agent) => {
      const agentTask = context[agent] ? `${task}. Contexto específico: ${context[agent]}` : task;
      const result = await this._call(agent, { task: agentTask });
      results[agent] = result;
      return { agent, result };
    });

    const completed = await Promise.allSettled(promises);
    completed.forEach((c, i) => {
      if (c.status === 'fulfilled') {
        results[agents[i]] = c.value.result;
      } else {
        results[agents[i]] = { status: 'error', error: c.reason?.message || 'unknown' };
      }
    });

    entry.status = 'completed';
    entry.results = results;
    entry.duration = Date.now() - entry.start;
    this.history.push(entry);
    this.swarms.set(swarmId, entry);
    return entry;
  }

  list() { return [...this.history].reverse().slice(0, 50); }
  get(id) { return this.swarms.get(id); }

  parseDef(content) {
    const lines = content.split('\n');
    const def = { name: '', topology: 'mesh', agents: [] };
    let inAgents = false;
    for (const line of lines) {
      const t = line.trim();
      if (!t || t.startsWith('#')) continue;
      if (t.startsWith('name:')) { def.name = t.split(':')[1].trim(); continue; }
      if (t.startsWith('topology:')) { def.topology = t.split(':')[1].trim(); continue; }
      if (t === 'agents:') { inAgents = true; continue; }
      if (inAgents && t.startsWith('- ')) { def.agents.push(t.slice(2).trim()); continue; }
      if (inAgents && !t.startsWith('-')) inAgents = false;
    }
    return def;
  }
}

const engine = new SwarmEngine();
module.exports = { SwarmEngine, engine };
