/**
 * Sandbox — Pre-deploy validation environment
 * Tests ALL tools, workflows, agents, and data flows before production deploy
 */

const http = require('http');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const GATEWAY = { host: '127.0.0.1', port: 18989 };
const RESULTS_FILE = path.join(__dirname, '..', '..', 'state', 'sandbox-results.json');

class Sandbox {
  constructor() { this.results = []; }

  async call(tool, params) {
    return new Promise(r => {
      const data = JSON.stringify({ tool, params: params || {} });
      const req = http.request({ hostname: GATEWAY.host, port: GATEWAY.port, path: '/api/call', method: 'POST',
        headers: { 'Content-Type': 'application/json' }, timeout: 30000 }, res => {
        let d = ''; res.on('data', c => d += c); res.on('end', () => { try { r(JSON.parse(d)); } catch { r({ raw: d }); } });
      });
      req.on('error', e => r({ error: e.message }));
      req.write(data); req.end();
    });
  }

  async test(name, fn) {
    try {
      const result = await fn();
      const passed = !result.error && !result?.raw?.includes('error');
      this.results.push({ name, passed, result: passed ? '✅' : '❌', detail: passed ? 'OK' : (result.error || JSON.stringify(result).substring(0, 100)) });
    } catch (e) {
      this.results.push({ name, passed: false, result: '❌', detail: e.message });
    }
  }

  async runAll() {
    this.results = [];
    console.log('\n🧪 SANDBOX — Full System Validation\n');

    // 1. Gateway Health
    await this.test('Gateway Health', async () => {
      return new Promise(r => { http.get({ hostname: '127.0.0.1', port: 18989, path: '/api/health', timeout: 5000 }, res => { let d = ''; res.on('data', c => d += c); res.on('end', () => r(JSON.parse(d))); }).on('error', e => r({ error: e.message })); });
    });

    // 2. Auth
    await this.test('Auth JWT', async () => {
      return new Promise(r => {
        const data = JSON.stringify({ client_id: 'sdc-core', client_secret: 'sdc_secret_ent3rpr1s3_k3y_2026' });
        const req = http.request({ hostname: '127.0.0.1', port: 18989, path: '/api/auth/token', method: 'POST', headers: { 'Content-Type': 'application/json' } }, res => { let d = ''; res.on('data', c => d += c); res.on('end', () => { try { const j = JSON.parse(d); r(j.access_token ? { ok: true } : { error: 'No token' }); } catch { r({ error: 'Parse error' }); } }); });
        req.write(data); req.end();
      });
    });

    // 3. Tool Count
    await this.test('Tool Count >= 166', async () => {
      const r = await this.call('health_all', {});
      const tools = await fetch('http://127.0.0.1:18989/api/tools').then(r => r.json());
      return tools.tools && tools.tools.length >= 166 ? { ok: true } : { error: 'Only ' + tools.tools?.length + ' tools' };
    });

    // 4. ABE Artists Data
    await this.test('ABE Artists Data', async () => {
      const t = await this._getToken();
      const r = await this._callAuth(t, 'abe_list_artists', {});
      return r.artists && r.artists.length >= 3 ? { ok: true } : { error: 'Only ' + r.artists?.length + ' artists' };
    });

    // 5. ABE CEO Dashboard
    await this.test('ABE CEO Dashboard', async () => {
      const t = await this._getToken();
      const r = await this._callAuth(t, 'abe_ceo_dashboard', {});
      return r.total_streams > 0 ? { ok: true } : { error: 'No streams data' };
    });

    // 6. Enterprise Score
    await this.test('Enterprise Score', async () => {
      const t = await this._getToken();
      const r = await this._callAuth(t, 'enterprise_score', {});
      return typeof r.score === 'number' ? { ok: true } : { error: 'No score' };
    });

    // 7. ADK Agents
    await this.test('ADK Agents >= 12', async () => {
      const t = await this._getToken();
      const r = await this._callAuth(t, 'adk_list_agents', {});
      return r.agents && r.agents.length >= 12 ? { ok: true } : { error: 'Only ' + r.agents?.length + ' agents' };
    });

    // 8. Workflow Samples
    await this.test('Workflows >= 7', async () => {
      const t = await this._getToken();
      const r = await this._callAuth(t, 'workflow_list_samples', {});
      return r.samples && r.samples.length >= 7 ? { ok: true } : { error: 'Only ' + r.samples?.length };
    });

    // 9. Intake System
    await this.test('Intake System', async () => {
      const t = await this._getToken();
      const r = await this._callAuth(t, 'intake_text', { text: 'test intake', source: 'manual' });
      return r.status === 'processed' ? { ok: true } : { error: 'Intake failed' };
    });

    // 10. Security Audit
    await this.test('Security Audit', async () => {
      const t = await this._getToken();
      const r = await this._callAuth(t, 'audit_run', {});
      return typeof r.score === 'number' && r.score >= 70 ? { ok: true } : { error: 'Score: ' + r.score };
    });

    // 11. Dashboard Pages
    const pages = ['/dashboard', '/adk', '/abe', '/abe-saas', '/abraham', '/cheatsheet', '/workflow-editor'];
    for (const page of pages) {
      await this.test('Page ' + page, async () => {
        return new Promise(r => { http.get({ hostname: '127.0.0.1', port: 18989, path: page, timeout: 5000 }, res => { let d = ''; res.on('data', c => d += c); res.on('end', () => r(res.statusCode === 200 && d.length > 100 ? { ok: true } : { error: res.statusCode })); }).on('error', e => r({ error: e.message })); });
      });
    }

    // Summary
    const passed = this.results.filter(r => r.passed).length;
    const failed = this.results.filter(r => !r.passed).length;
    
    console.log('\n' + '='.repeat(50));
    console.log(`📊 SANDBOX RESULTS: ${passed} passed, ${failed} failed, ${this.results.length} total`);
    console.log('='.repeat(50) + '\n');
    
    this.results.forEach(r => console.log(` ${r.result} ${r.name}${r.passed ? '' : ' — ' + r.detail}`));
    
    // Save results
    try { fs.writeFileSync(RESULTS_FILE, JSON.stringify({ timestamp: new Date().toISOString(), passed, failed, total: this.results.length, results: this.results }, null, 2)); } catch {}
    
    return { passed, failed, total: this.results.length, results: this.results };
  }

  async _getToken() {
    const r = await new Promise(r => {
      const data = JSON.stringify({ client_id: 'sdc-core', client_secret: 'sdc_secret_ent3rpr1s3_k3y_2026' });
      const req = http.request({ hostname: '127.0.0.1', port: 18989, path: '/api/auth/token', method: 'POST', headers: { 'Content-Type': 'application/json' } }, res => { let d = ''; res.on('data', c => d += c); res.on('end', () => { try { r(JSON.parse(d)); } catch { r({}); } }); });
      req.write(data); req.end();
    });
    return r.access_token || '';
  }

  async _callAuth(token, tool, params) {
    return new Promise(r => {
      const data = JSON.stringify({ tool, params: params || {} });
      const req = http.request({ hostname: '127.0.0.1', port: 18989, path: '/api/call', method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token } }, res => {
        let d = ''; res.on('data', c => d += c); res.on('end', () => { try { r(JSON.parse(d)); } catch { r({}); } });
      });
      req.write(data); req.end();
    });
  }
}

const sandbox = new Sandbox();
module.exports = { Sandbox, sandbox };
