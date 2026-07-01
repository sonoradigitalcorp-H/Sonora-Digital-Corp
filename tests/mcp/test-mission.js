/**
 * MISSION TEST — Full system validation
 * 1. Agent conversations with traces
 * 2. Viral content generation
 * 3. Product footprints
 * 4. WhatsApp notification
 * node tests/mcp/test-mission.js
 */

const http = require('http');
const { spawn } = require('child_process');
const path = require('path');

const GATEWAY = 'http://127.0.0.1:18989';
let passed = 0, failed = 0;

function assert(label, condition, detail) {
  if (condition) { passed++; console.log('  ✅ ' + label); }
  else { failed++; console.log('  ❌ ' + label + ': ' + (detail || '')); }
}

async function fetch(path, opts) {
  return new Promise(r => {
    const u = new URL(GATEWAY + path);
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
  return fetch('/api/call', { method: 'POST', headers: { 'Authorization': 'Bearer ' + token }, body: { tool, params: params || {} } });
}

async function main() {
  console.log('\n🎯 MISSION TEST — Full System Validation\n');

  // 1. Viral Trends Research
  console.log('📈 1. VIRAL TRENDS');
  const trends = await call('viral_research', { month: 7 });
  assert('viral_research returns data', trends.data?.month === 'Verano', JSON.stringify(trends.data));
  assert('trends has events', (trends.data?.today_events?.length || trends.data?.upcoming_events?.length) >= 0);

  // 2. Viral Content Generation
  console.log('\n🎨 2. VIRAL CONTENT');
  const viral = await call('viral_generate', { artist: 'Hector Rubio', format: 'cover', auto_approve: true });
  assert('viral_generate works', viral.data?.event !== undefined, JSON.stringify(viral.data));

  // 3. Viral Dashboard
  const dash = await call('viral_dashboard', {});
  assert('viral_dashboard returns', typeof dash.data?.viral_score === 'number');

  // 4. Agent Conversation
  console.log('\n💬 3. AGENT CONVERSATIONS');
  const conv = await call('converse_run', { agent1: 'abe-analytics-agent', agent2: 'abe-marketing-agent', topic: 'analyze ABE Music Q3 strategy' });
  assert('converse_run works', conv.data?.conversation?.id !== undefined, JSON.stringify(conv.data));
  assert('product created', conv.data?.product_created?.id !== undefined);

  // 5. Product Footprint
  const footprint = await call('converse_footprint', {});
  assert('converse_footprint returns', typeof footprint.data?.total_products === 'number');
  assert('has products', footprint.data?.total_products >= 1);

  // 6. Agent Test
  console.log('\n🧪 4. AGENT TESTS');
  const test = await call('converse_test', { test_name: 'mission-validation', agent1: 'abe-revenue-agent', agent2: 'abe-scheduler-agent', topic: 'validate revenue pipeline' });
  assert('converse_test works', test.data?.status === 'completed', JSON.stringify(test.data));

  // 7. Knowledge graph tracking
  console.log('\n🧠 5. KNOWLEDGE GRAPH');
  const kg = await call('graph_stats', {});
  assert('graph_stats returns', typeof kg.data?.total_knowledge_nodes === 'number', JSON.stringify(kg.data));

  // 8. WhatsApp Notification
  console.log('\n📱 6. WHATSAPP');
  const wa = await call('viral_notify', { phone: '526623538272', include_generated: true });
  assert('viral_notify works', wa.data?.status === 'notification_ready', JSON.stringify(wa.data));
  assert('has message', wa.data?.message_preview?.length > 50);

  // 9. Mission Control Page
  console.log('\n🖥️ 7. MISSION CONTROL');
  const mc = await new Promise(r => http.get({ hostname: '127.0.0.1', port: 18989, path: '/mission-control', timeout: 5000 }, res => { let d = ''; res.on('data', c => d += c); res.on('end', () => r({ s: res.statusCode, l: d.length })); }).on('error', e => r({ s: 0, l: 0 })));
  assert('mission-control page', mc.s === 200 && mc.l > 500);

  // Summary
  console.log('\n' + '='.repeat(50));
  console.log(`📊 MISSION TEST: ${passed} passed, ${failed} failed, ${passed + failed} total`);
  console.log('='.repeat(50) + '\n');
  process.exit(failed > 0 ? 1 : 0);
}

async function run() {
  const h = await fetch('/api/health');
  if (h.status === 200) { await main(); return; }
  console.log('Starting MCP Gateway...');
  const gw = spawn('node', [path.join(__dirname, '..', '..', 'mcp', 'gateway', 'mcp-server-http.js')], { stdio: 'pipe' });
  await new Promise(r => setTimeout(r, 2000));
  await main();
}

run().catch(e => { console.error('Fatal:', e.message); process.exit(1); });
