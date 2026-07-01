/**
 * ADK Agents + Workflows Integration Tests
 * node tests/mcp/test-agents.js
 */

const http = require('http');
const { spawn } = require('child_process');
const path = require('path');

const GATEWAY_SCRIPT = path.join(__dirname, '..', '..', 'mcp', 'gateway', 'mcp-server-http.js');
const BASE = 'http://127.0.0.1:18989';
let passed = 0, failed = 0, skipped = 0;

function assert(label, condition) { condition ? passed++ : failed++; console.log((condition ? '  ✅' : '  ❌') + ' ' + label); }

async function fetch(path, opts) {
  return new Promise(r => {
    const u = new URL(BASE + path);
    const req = http.request({hostname: u.hostname, port: u.port, path: u.pathname, method: (opts && opts.method) || 'GET', headers: { 'Content-Type': 'application/json', ...((opts && opts.headers) || {}) }, timeout: 15000}, res => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => { try { r({ status: res.statusCode, data: JSON.parse(d) }); } catch { r({ status: res.statusCode, data: null, raw: d }); } });
    }); req.on('error', e => r({ error: e.message })); if (opts && opts.body) req.write(JSON.stringify(opts.body)); req.end();
  });
}

async function getToken() {
  const r = await fetch('/api/auth/token', { method: 'POST', body: { client_id: 'sdc-core', client_secret: 'sdc_secret_ent3rpr1s3_k3y_2026' } });
  return r.data?.access_token || '';
}

async function call(tool, params) {
  const token = await getToken();
  return fetch('/api/call', { method: 'POST', headers: { 'Authorization': 'Bearer ' + token }, body: { tool, params } });
}

async function main() {
  console.log('\n🧪 ADK Agents + Workflows Integration Tests\n');

  // === ADK AGENTS ===
  console.log('📋 ADK Agents:');
  const agents = await call('adk_list_agents');
  const agentList = agents.data?.agents || [];
  assert('adk_list_agents returns agents', agentList.length >= 6);
  
  // Check each agent exists
  const expected = ['sales-agent', 'research-agent', 'content-agent', 'booking-agent', 'onboarding-agent', 'support-agent'];
  expected.forEach(name => {
    assert('  ' + name + ' registered', agentList.some(a => a.name === name));
  });

  // Verify agent schema
  agentList.forEach(a => {
    assert('  ' + a.name + ' has capability', !!a.capability);
    assert('  ' + a.name + ' has model', !!a.model);
    assert('  ' + a.name + ' has provider', !!a.provider);
  });

  // === WORKFLOWS ===
  console.log('\n⚡ Workflows:');
  const wfSamples = await call('workflow_list_samples');
  const samples = wfSamples.data?.samples || [];
  assert('workflow_list_samples returns samples', samples.length >= 5);

  const expectedWF = ['lead-to-cash', 'research-report', 'lead-to-cash-real', 'content-pipeline', 'client-onboarding', 'sdc-lead-to-cash'];
  expectedWF.forEach(name => {
    assert('  ' + name + ' available', samples.some(s => s.name === name));
  });

  // Run a simple workflow
  const wfRun = await call('workflow_run', { name: 'research-report', context: { topic: 'AI agents' } });
  assert('workflow_run executes', wfRun.data?.status === 'completed' || wfRun.data?.status === 'running');
  assert('workflow returns steps', Array.isArray(wfRun.data?.steps));

  const wfList = await call('workflow_list');
  assert('workflow_list returns history', Array.isArray(wfList.data?.workflows));

  // === PLUGIN MARKETPLACE ===
  console.log('\n🧩 Plugin Marketplace:');
  const plugins = await call('plugin_list');
  const pluginList = plugins.data?.plugins || [];
  assert('plugin_list returns plugins', pluginList.length >= 5);

  const defaults = await call('plugin_defaults');
  assert('plugin_defaults returns defaults', Array.isArray(defaults.data?.plugins));

  const search = await call('plugin_search', { query: 'github' });
  assert('plugin_search finds results', (search.data?.results || []).length > 0);

  // === SWARM ===
  console.log('\n🐝 Swarm:');
  const swarm = await call('swarm_run', { name: 'research-swarm', task: 'research AI agents', agents: ['capability_resolve', 'enterprise_score'] });
  assert('swarm_run executes', swarm.data?.status === 'completed' || swarm.data?.status === 'running');
  assert('swarm returns results', swarm.data?.results && Object.keys(swarm.data.results).length > 0);

  // === SELF-LEARNING ===
  console.log('\n🧠 Self-Learning:');
  const learn = await call('learning_stats');
  assert('learning_stats returns data', typeof learn.data?.total_calls === 'number');

  const record = await call('learning_record', { tool: 'test_tool', capability: 'test-capability', success: true, duration: 100 });
  assert('learning_record works', record.data?.recorded === true);

  // === SECURITY AUDIT ===
  console.log('\n🔐 Security:');
  const audit = await call('audit_run');
  assert('audit_run returns score', typeof audit.data?.score === 'number');
  assert('  Score >= 70%', (audit.data?.score || 0) >= 70);

  const soul = await call('audit_soul');
  assert('audit_soul returns soul_score', typeof soul.data?.soul_score === 'number');
  assert('  Soul Score >= 80%', (soul.data?.soul_score || 0) >= 80);

  // === INCIDENT RESPONSE ===
  console.log('\n🚨 Incident Response:');
  const inc = await call('incident_report', { severity: 'P3', description: 'integration test incident' });
  assert('incident_report works', inc.data?.reported === true);

  const incList = await call('incident_list');
  assert('incident_list returns incidents', Array.isArray(incList.data?.incidents));

  // === WORKFLOW EDITOR ===
  console.log('\n🖥️  Workflow Editor:');
  try {
    const wfEditor = await new Promise(r => http.get({ hostname: '127.0.0.1', port: 18989, path: '/workflow-editor' }, res => { let d = ''; res.on('data', c => d += c); res.on('end', () => r({ s: res.statusCode, l: d.length })); }));
    assert('GET /workflow-editor returns HTML', wfEditor.s === 200 && wfEditor.l > 1000);
  } catch { assert('GET /workflow-editor', false); }

  // === SUMMARY ===
  const total = passed + failed + skipped;
  console.log(`\n${'='.repeat(50)}`);
  console.log(`Resultados: ${passed} pasaron, ${failed} fallaron, ${skipped} saltados de ${total}`);
  console.log(`${'='.repeat(50)}`);
  process.exit(failed > 0 ? 1 : 0);
}

async function run() {
  const h = await fetch('/api/health');
  if (h.status === 200) { await main(); return; }
  console.log('Starting MCP Gateway...');
  const gw = spawn('node', [GATEWAY_SCRIPT], { stdio: 'pipe' });
  await new Promise(r => setTimeout(r, 2000));
  await main();
}

run().catch(e => { console.error('Fatal:', e.message); process.exit(1); });
