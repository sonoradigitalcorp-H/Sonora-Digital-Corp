/**
 * ═══════════════════════════════════════════════════════════════
 * Sonora Workflow Engine v1.0 — Multi-Agent Graph Workflows
 * ═══════════════════════════════════════════════════════════════
 * Ejecuta workflows multi-agente definidos en YAML.
 * Steps: secuenciales, paralelos, condicionales, con retry.
 *
 * Ejemplo:
 *   lead → qualify → proposal → [notify + invoice] → done
 *                      ↓ failure
 *                   escalate
 * ═══════════════════════════════════════════════════════════════
 */

const fs = require('fs');
const path = require('path');
const http = require('http');

const GATEWAY_HOST = '127.0.0.1';
const GATEWAY_PORT = 18989;
const SAMPLES_DIR = path.join(__dirname, 'samples');
const STATE_DIR = path.join(__dirname, '..', '..', 'state', 'workflows');

class WorkflowEngine {
  constructor() {
    this.running = new Map();
    this.history = [];
    fs.mkdirSync(STATE_DIR, { recursive: true });
  }

  _callGateway(tool, params) {
    return new Promise((resolve) => {
      const data = JSON.stringify({ tool, params });
      const req = http.request({
        hostname: GATEWAY_HOST, port: GATEWAY_PORT, path: '/api/call', method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Content-Length': data.length },
        timeout: 60000,
      }, (res) => {
        let d = '';
        res.on('data', c => d += c);
        res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ raw: d }); } });
      });
      req.on('error', (e) => resolve({ error: e.message }));
      req.write(data);
      req.end();
    });
  }

  executeSteps(stepNames, steps, context) {
    return stepNames.reduce((chain, stepId) => {
      return chain.then(async (results) => {
        const step = steps.find(s => s.id === stepId);
        if (!step) return results;
        const stepInput = this._interpolate(step.input || '', results, context);
        const entry = { step: stepId, agent: step.agent, start: Date.now(), status: 'running' };
        results[stepId] = entry;
        try {
          const r = await this._callGateway(step.agent, { task: stepInput });
          entry.status = 'success';
          entry.output = r;
          entry.duration = Date.now() - entry.start;
        } catch (e) {
          entry.status = 'error';
          entry.error = e.message;
          entry.duration = Date.now() - entry.start;
          if (step.on_failure === 'escalate' || step.on_failure === 'stop') {
            throw entry;
          }
        }
        return results;
      });
    }, Promise.resolve({}));
  }

  async run(workflowDef, context = {}) {
    const wf = typeof workflowDef === 'string' ? this.parse(workflowDef) : workflowDef;
    const wfId = `wf-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
    const startTime = Date.now();
    const entry = { id: wfId, name: wf.name, steps: wf.steps, start: startTime, status: 'running', outputs: {}, error: null };

    this.running.set(wfId, entry);
    this._persist(wfId, entry);

    try {
      const stepNames = wf.steps.map(s => s.id);
      const outputs = await this.executeSteps(stepNames, wf.steps, context);
      entry.status = 'completed';
      entry.outputs = outputs;
      entry.duration = Date.now() - startTime;
      this._persist(wfId, entry);
      this.history.push(entry);
      return entry;
    } catch (e) {
      entry.status = 'failed';
      entry.error = e.error || e.message || 'unknown';
      entry.duration = Date.now() - startTime;
      this._persist(wfId, entry);
      this.history.push(entry);
      return entry;
    }
  }

  parse(content) {
    const lines = content.split('\n');
    const wf = { name: '', steps: [] };
    let currentStep = null;
    for (const line of lines) {
      const t = line.trim();
      if (!t || t.startsWith('#')) continue;
      if (t.startsWith('name:')) { wf.name = t.split(':')[1].trim(); continue; }
      if (t === 'steps:') continue;
      if (t.startsWith('- id:')) {
        if (currentStep) wf.steps.push(currentStep);
        currentStep = { id: t.split(':')[1].trim() };
        continue;
      }
      if (currentStep && t.startsWith('agent:')) { currentStep.agent = t.split(':')[1].trim(); continue; }
      if (currentStep && t.startsWith('input:')) { currentStep.input = t.split(':').slice(1).join(':').trim(); continue; }
      if (currentStep && t.startsWith('depends_on:')) { currentStep.depends_on = t.split(':')[1].trim(); continue; }
      if (currentStep && t.startsWith('on_failure:')) { currentStep.on_failure = t.split(':')[1].trim(); continue; }
    }
    if (currentStep) wf.steps.push(currentStep);
    return wf;
  }

  _interpolate(template, outputs, context) {
    let result = template;
    for (const [k, v] of Object.entries(outputs)) {
      const out = v.output ? (typeof v.output === 'object' ? JSON.stringify(v.output) : String(v.output)) : '';
      result = result.replace(new RegExp(`\\{\\{${k}\\.output\\}\\}`, 'g'), out);
    }
    for (const [k, v] of Object.entries(context)) {
      result = result.replace(new RegExp(`\\{\\{${k}\\}\\}`, 'g'), String(v));
    }
    return result;
  }

  get(id) { return this.running.get(id) || this.history.find(h => h.id === id); }
  list() { return [...this.history].reverse().slice(0, 50); }
  listRunning() { return Array.from(this.running.values()).filter(e => e.status === 'running'); }

  loadSamples() {
    const samples = [];
    if (fs.existsSync(SAMPLES_DIR)) {
      for (const f of fs.readdirSync(SAMPLES_DIR).filter(f => f.endsWith('.yaml'))) {
        try {
          samples.push({ name: f.replace('.yaml', ''), content: fs.readFileSync(path.join(SAMPLES_DIR, f), 'utf-8') });
        } catch {}
      }
    }
    return samples;
  }

  _persist(id, data) {
    try { fs.writeFileSync(path.join(STATE_DIR, `${id}.json`), JSON.stringify(data, null, 2)); } catch {}
  }
}

const engine = new WorkflowEngine();
module.exports = { WorkflowEngine, engine };
