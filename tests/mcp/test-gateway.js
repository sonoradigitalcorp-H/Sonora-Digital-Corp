/**
 * MCP Gateway Tests — Unit + Integration
 * Correr: node tests/mcp/test-gateway.js
 */

const http = require('http');
const { spawn } = require('child_process');
const path = require('path');

const GATEWAY_SCRIPT = path.join(__dirname, '..', '..', 'mcp', 'gateway', 'mcp-server-http.js');
const GATEWAY_PORT = 18989;
const BASE = `http://127.0.0.1:${GATEWAY_PORT}`;

let passed = 0, failed = 0, gateway = null;

function assert(label, condition) {
  if (condition) { passed++; console.log(`  ✅ ${label}`); }
  else { failed++; console.log(`  ❌ ${label}`); }
}

async function fetch(path, opts = {}) {
  return new Promise((resolve) => {
    const u = new URL(BASE + path);
    const req = http.request({
      hostname: u.hostname, port: u.port, path: u.pathname,
      method: opts.method || 'GET',
      headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) },
      timeout: 10000,
    }, (res) => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(d) }); }
        catch { resolve({ status: res.statusCode, data: null, raw: d }); }
      });
    });
    req.on('error', e => resolve({ error: e.message }));
    if (opts.body) req.write(JSON.stringify(opts.body));
    req.end();
  });
}

async function getToken() {
  const r = await fetch('/api/auth/token', {
    method: 'POST',
    body: { client_id: 'sdc-core', client_secret: 'sdc_secret_ent3rpr1s3_k3y_2026' },
  });
  return r.data?.access_token || '';
}

async function call(tool, params = {}) {
  const token = await getToken();
  return fetch('/api/call', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + token },
    body: { tool, params },
  });
}

async function runTests() {
  console.log('\n🔮 MCP Gateway Tests\n');

  // === UNIT TESTS (module resolution) ===
  console.log('📦 Module Resolution:');
  try {
    require('../../mcp/auth/jwt');
    assert('auth/jwt.js loads', true);
  } catch (e) { assert('auth/jwt.js loads', false); console.error('  ', e.message); }

  try {
    require('../../mcp/auth/middleware');
    assert('auth/middleware.js loads', true);
  } catch (e) { assert('auth/middleware.js loads', false); }

  try {
    require('../../mcp/registry/capability-registry');
    assert('capability-registry.js loads', true);
  } catch (e) { assert('capability-registry.js loads', false); }

  try {
    require('../../mcp/registry/skill-registry');
    assert('skill-registry.js loads', true);
  } catch (e) { assert('skill-registry.js loads', false); }

  try {
    require('../../mcp/adk/adk');
    assert('adk.js loads', true);
  } catch (e) { assert('adk.js loads', false); }

  try {
    require('../../mcp/providers/provider-router');
    assert('provider-router.js loads', true);
  } catch (e) { assert('provider-router.js loads', false); }

  try {
    require('../../mcp/providers/provider-manager');
    assert('provider-manager.js loads', true);
  } catch (e) { assert('provider-manager.js loads', false); }

  try {
    require('../../mcp/workflow/engine');
    assert('workflow/engine.js loads', true);
  } catch (e) { assert('workflow/engine.js loads', false); }

  // === Capability Registry Unit Tests ===
  console.log('\n📋 Capability Registry:');
  const capReg = require('../../mcp/registry/capability-registry');
  const caps = capReg.getRegistered();
  assert('getRegistered() returns array', Array.isArray(caps));
  assert(`  ${caps.length} capabilities registered`, caps.length >= 14);

  const r1 = capReg.resolve('generate a sales proposal for a new client');
  assert('resolve sales task → Sales Execution', r1.capability.includes('Sales') && r1.confidence >= 0.3);

  const r2 = capReg.resolve('implement a python function for data processing');
  assert('resolve code task → has agent', r2.agent && r2.confidence >= 0.3);

  const r3 = capReg.resolve('xyz123 random noise');
  assert('resolve random task → fallback research', r3.fallback === true);

  // === ADK Unit Tests ===
  console.log('\n🧠 ADK Runtime:');
  const adk = require('../../mcp/adk/adk');
  const agents = adk.runtime.list();
  assert('list() returns array', Array.isArray(agents));
  assert(`  ${agents.length} ADK agents`, agents.length >= 1);
  if (agents.length > 0) {
    const v = adk.runtime.validate(agents[0]);
    assert(`  ${agents[0].name} valid`, v.valid);
  }

  // === Provider Router Unit Tests ===
  console.log('\n🌐 Provider Router:');
  const pr = require('../../mcp/providers/provider-router');
  const models = pr.listModels();
  assert('listModels() returns array', Array.isArray(models));
  assert(`  ${models.length} models`, models.length >= 5);

  const res = pr.resolveForCapability('research');
  assert('research → has provider and model', res.provider && res.model);

  const finops = pr.getFinOpsSummary();
  assert('getFinOpsSummary() returns object', typeof finops === 'object');
  assert('  total_calls is number', typeof finops.total_calls === 'number');

  // === Skill Registry Unit Tests ===
  console.log('\n📦 Skill Registry:');
  const sr = require('../../mcp/registry/skill-registry');
  const stats = sr.registry.getStats();
  assert(`  ${stats.total} total skills`, stats.total >= 100);
  assert('  4 sources present', Object.keys(stats.bySource).length === 4);

  const search = sr.registry.search('sat fiscal');
  assert('search finds results', search.length > 0);

  // === Workflow Engine Unit Tests ===
  console.log('\n⚡ Workflow Engine:');
  const wf = require('../../mcp/workflow/engine');
  const samples = wf.engine.loadSamples();
  assert(`  ${samples.length} workflow samples`, samples.length >= 1);

  if (samples.length > 0) {
    const def = wf.engine.parse(samples[0].content);
    assert(`  ${def.name} parsed with ${def.steps.length} steps`, def.name && def.steps.length > 0);
  }

  // === Provider Manager Unit Tests ===
  console.log('\n📋 Provider Manager:');
  const pm = require('../../mcp/providers/provider-manager');
  const provs = pm.manager.list();
  assert('list() returns array', Array.isArray(provs));

  // === INTEGRATION TESTS ===
  console.log('\n🔌 Integration (requires gateway on :18989):');

  const h = await fetch('/api/health');
  assert('GET /api/health returns 200', h.status === 200);
  assert('  status is ok', h.data?.status === 'ok');

  const t = await fetch('/api/auth/token', {
    method: 'POST',
    body: { client_id: 'sdc-core', client_secret: 'sdc_secret_ent3rpr1s3_k3y_2026' },
  });
  assert('POST /api/auth/token returns token', !!t.data?.access_token);
  const token = t.data.access_token;

  const tl = await fetch('/api/tools', { headers: { 'Authorization': 'Bearer ' + token } });
  assert('GET /api/tools returns list', Array.isArray(tl.data?.tools));
  assert(`  ${tl.data?.tools?.length || 0} tools`, (tl.data?.tools?.length || 0) >= 100);

  const cl = await fetch('/api/capability/list', { headers: { 'Authorization': 'Bearer ' + token } });
  assert('GET /api/capability/list returns capabilities', Array.isArray(cl.data?.capabilities));
  assert(`  ${cl.data?.capabilities?.length || 0} capabilities`, (cl.data?.capabilities?.length || 0) >= 14);

  const cr = await fetch('/api/capability/resolve', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + token },
    body: { task: 'generate a sales proposal' },
  });
  assert('POST /api/capability/resolve works', cr.data?.capability && cr.data?.confidence >= 0.3);

  const skills = await call('skills_list');
  assert('skills_list returns skills', Array.isArray(skills.data?.skills));

  const adkList = await call('adk_list_agents');
  assert('adk_list_agents returns agents', Array.isArray(adkList.data?.agents));

  const provList = await call('provider_manager_list');
  assert('provider_manager_list returns providers', Array.isArray(provList.data?.providers));

  const wfSamples = await call('workflow_list_samples');
  assert('workflow_list_samples returns samples', Array.isArray(wfSamples.data?.samples));

  const finopsCall = await call('finops_summary');
  assert('finops_summary returns data', typeof finopsCall.data?.total_calls === 'number');

  // Auth failure tests
  const noAuth = await fetch('/api/tools');
  assert('No auth → 401', noAuth.status === 401);

  const badToken = await fetch('/api/tools', { headers: { 'Authorization': 'Bearer invalid_token' } });
  assert('Bad token → 401', badToken.status === 401);

  // Dashboard/ADK Web
  const dash = await new Promise(r => http.get({ hostname: '127.0.0.1', port: 18989, path: '/dashboard' }, res => { let d = ''; res.on('data', c => d += c); res.on('end', () => r({ s: res.statusCode, l: d.length })); }));
  assert('GET /dashboard returns HTML', dash.s === 200 && dash.l > 1000);

  const adkUI = await new Promise(r => http.get({ hostname: '127.0.0.1', port: 18989, path: '/adk' }, res => { let d = ''; res.on('data', c => d += c); res.on('end', () => r({ s: res.statusCode, l: d.length })); }));
  assert('GET /adk returns HTML', adkUI.s === 200 && adkUI.l > 1000);

  // === SUMMARY ===
  const total = passed + failed;
  console.log(`\n${'='.repeat(50)}`);
  console.log(`Resultados: ${passed} pasaron, ${failed} fallaron de ${total}`);
  console.log(`${'='.repeat(50)}`);
  process.exit(failed > 0 ? 1 : 0);
}

// Start gateway if not already running
async function main() {
  // Check if gateway is already up
  const h = await fetch('/api/health');
  if (h.status === 200) {
    await runTests();
    return;
  }

  // Start gateway
  console.log('Starting MCP Gateway...');
  gateway = spawn('node', [GATEWAY_SCRIPT], { stdio: 'pipe' });
  
  await new Promise(r => setTimeout(r, 2000));
  await runTests();
}

main().catch(e => { console.error('Fatal:', e.message); process.exit(1); });
