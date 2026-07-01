/**
 * POWER TEST — Prueba real del sistema completo
 * Simula escenarios reales de ABE Music
 * node tests/mcp/test-power.js
 */

const http = require('http');
const { spawn } = require('child_process');
const path = require('path');

const GATEWAY = 'http://127.0.0.1:18989';
const LOG_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'power-test.log');

let passed = 0, failed = 0, total = 0;

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}\n`;
  try { require('fs').appendFileSync(LOG_FILE, line); } catch {}
}

function assert(label, condition, detail) {
  total++;
  if (condition) { passed++; log(`✅ ${label}`); }
  else { failed++; log(`❌ ${label}: ${detail || ''}`); }
}

async function fetch(path, opts) {
  return new Promise(r => {
    const u = new URL(GATEWAY + path);
    const req = http.request({hostname: u.hostname, port: u.port, path: u.pathname, method: (opts && opts.method) || 'GET', headers: { 'Content-Type': 'application/json', ...((opts && opts.headers) || {}) }, timeout: 30000}, res => {
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

async function abeCall(tool, params) {
  const r = await fetch('/api/auth/token', { method: 'POST', body: { client_id: 'abe-fenix', client_secret: 'abe_f3n1x_pr0_k3y_2026' } });
  const token = r.data?.access_token || '';
  return fetch('/api/call', { method: 'POST', headers: { 'Authorization': 'Bearer ' + token }, body: { tool, params: params || {} } });
}

async function main() {
  console.log('\n🔥 POWER TEST — Native Agent OS\n');
  log('=== POWER TEST START ===');

  // ─── SCENARIO 1: GATEWAY BASICS ───
  console.log('\n📋 1. GATEWAY FUNDAMENTALS\n');
  
  const h = await fetch('/api/health');
  assert('Gateway responde', h.status === 200 && h.data?.status === 'ok', JSON.stringify(h.data));
  
  const t = await fetch('/api/auth/token', { method: 'POST', body: { client_id: 'sdc-core', client_secret: 'sdc_secret_ent3rpr1s3_k3y_2026' } });
  assert('Auth JWT funciona', !!t.data?.access_token, 'No token received');
  const token = t.data?.access_token || '';
  
  const tl = await fetch('/api/tools', { headers: { 'Authorization': 'Bearer ' + token } });
  const toolCount = tl.data?.tools?.length || 0;
  assert(`Tools count >= 179`, toolCount >= 179, `Only ${toolCount} tools`);
  console.log(`   📊 ${toolCount} tools registradas`);

  // ─── SCENARIO 2: ABE MUSIC DATA ───
  console.log('\n🎵 2. ABE MUSIC — DATOS REALES\n');
  
  // 2a. List artists
  const artists = await abeCall('abe_list_artists', {});
  const aList = artists.data?.artists || [];
  assert('ABE artists load', aList.length >= 3, `Found ${aList.length} artists`);
  aList.forEach(a => console.log(`   🎤 ${a.name}: ${(a.streams||0).toLocaleString()} streams | $${(a.revenue||0).toLocaleString()}`));
  
  // 2b. CEO Dashboard
  const ceo = await abeCall('abe_ceo_dashboard', {});
  assert('CEO dashboard returns data', ceo.data?.total_streams > 0, `Streams: ${ceo.data?.total_streams}`);
  console.log(`   📊 Total streams: ${(ceo.data?.total_streams || 0).toLocaleString()}`);
  console.log(`   💰 Total revenue: $${(ceo.data?.total_revenue || 0).toLocaleString()}`);
  console.log(`   🏆 Top artist: ${ceo.data?.top_artist}`);
  console.log(`   📊 Split: Artist $${(ceo.data?.artist_revenue_share || 0).toLocaleString()} | Label $${(ceo.data?.label_revenue_share || 0).toLocaleString()} | Dist $${(ceo.data?.distributor_revenue_share || 0).toLocaleString()}`);
  
  // 2c. Artist KPI
  const kpi = await abeCall('abe_artist_kpi', { artist_id: 'Hector Rubio' });
  assert('Artist KPI works', kpi.data?.total_streams > 0, `Hector: ${kpi.data?.total_streams} streams`);
  console.log(`   🎤 Hector Rubio KPI: ${(kpi.data?.total_streams || 0).toLocaleString()} streams, $${(kpi.data?.total_revenue || 0).toLocaleString()}`);
  
  // 2d. Enterprise Score
  const score = await call('enterprise_score', {});
  assert('Enterprise Score returns value', typeof score.data?.score === 'number', `Score: ${score.data?.score}`);
  console.log(`   🏆 Enterprise Score: ${score.data?.score}/100`);
  if (score.data?.metrics) Object.entries(score.data.metrics).slice(0, 5).forEach(([k, v]) => console.log(`      ${k}: ${v}/10`));

  // ─── SCENARIO 3: AGENTS ───
  console.log('\n🧠 3. ADK AGENTS\n');
  
  const agents = await call('adk_list_agents', {});
  const agentList = agents.data?.agents || [];
  assert(`ADK agents >= 12`, agentList.length >= 12, `Only ${agentList.length} agents`);
  console.log(`   🧠 ${agentList.length} agents registrados:`);
  agentList.forEach(a => console.log(`      ${a.name} (${a.capability || '?'})`));
  
  // Verify ABE agents specifically
  const abeAgents = ['abe-agent', 'abe-crm-agent', 'abe-revenue-agent', 'abe-marketing-agent', 'abe-analytics-agent', 'abe-scheduler-agent'];
  abeAgents.forEach(name => {
    assert(`   ${name} exists`, agentList.some(a => a.name === name), 'Not found');
  });

  // ─── SCENARIO 4: WORKFLOWS ───
  console.log('\n⚡ 4. WORKFLOWS\n');
  
  const wf = await call('workflow_list_samples', {});
  const wfList = wf.data?.samples || [];
  assert(`Workflows >= 7`, wfList.length >= 7, `Only ${wfList.length} workflows`);
  wfList.forEach(w => console.log(`   ⚡ ${w.name}`));
  
  // Execute research-report workflow
  const wfRun = await call('workflow_run', { name: 'research-report', context: { topic: 'ABE Music performance' } });
  assert('Workflow executes', wfRun.data?.status === 'completed' || wfRun.data?.status === 'running', JSON.stringify(wfRun.data));
  console.log(`   ⚡ Workflow executed: ${wfRun.data?.status} (${wfRun.data?.duration || '?'}ms)`);

  // ─── SCENARIO 5: INTAKE ───
  console.log('\n📥 5. INTAKE SYSTEM\n');
  
  // Text intake
  const intake1 = await call('intake_text', { text: 'Hector Rubio acaba de lanzar nuevo sencillo "Corazón de Oro" en todas las plataformas', source: 'voice', context: 'Hector Rubio' });
  assert('Intake text classifies', intake1.data?.category !== 'general', `Category: ${intake1.data?.category}`);
  console.log(`   📥 Text classified as: ${intake1.data?.category}`);
  
  // Email intake
  const intake2 = await call('intake_email', { from: 'distributor@distrokid.com', subject: 'Nuevas streams - Jesus Urquijo', body: 'Jesus Urquijo tuvo 15,000 streams esta semana en Spotify. Revenue generado: $750.' });
  assert('Intake email processes', intake2.data?.status === 'processed', JSON.stringify(intake2.data));
  console.log(`   📥 Email processed: ${intake2.data?.category}`);
  
  // Intake stats
  const stats = await call('intake_stats', {});
  assert('Intake stats', stats.data?.total_entries > 0, `Entries: ${stats.data?.total_entries}`);
  console.log(`   📊 Total intake entries: ${stats.data?.total_entries}`);

  // ─── SCENARIO 6: MEDIA ───
  console.log('\n🎬 6. MEDIA GENERATION\n');
  
  const mediaLib = await call('media_library', { limit: 5 });
  assert('Media library accessible', typeof mediaLib.data?.media !== 'undefined', JSON.stringify(mediaLib.data));
  console.log(`   🎬 Media library: ${mediaLib.data?.media?.length || 0} files`);

  // ─── SCENARIO 7: DESIGN SYSTEMS ───
  console.log('\n🎨 7. DESIGN SYSTEMS\n');
  
  const ds = await call('design_list', {});
  assert(`Design systems >= 150`, ds.data?.total >= 150, `Only ${ds.data?.total}`);
  console.log(`   🎨 ${ds.data?.total} design systems disponibles`);
  
  const rec = await call('design_recommend', { client: 'ABE Music', purpose: 'music artist dashboard' });
  assert('Design recommend works', rec.data?.recommendations?.length > 0, JSON.stringify(rec.data));
  console.log(`   🎨 Recommended: ${rec.data?.recommendations?.map(r => r.name).join(', ')}`);
  
  const gen = await call('design_generate', { system: 'energy', title: 'ABE Music Dashboard', type: 'dashboard' });
  assert('Design generate page', gen.data?.html_preview?.length > 500, 'HTML too short');
  console.log(`   🎨 Page generated with ${gen.data?.variables?.length || 0} design tokens`);

  // ─── SCENARIO 8: PROVIDERS ───
  console.log('\n🌐 8. PROVIDERS\n');
  
  const prov = await call('provider_manager_list', {});
  assert('Providers listed', (prov.data?.providers || []).length >= 3, JSON.stringify(prov.data));
  (prov.data?.providers || []).forEach(p => console.log(`   🌐 ${p.name}: ${p.models} models`));

  // ─── SCENARIO 9: SECURITY ───
  console.log('\n🔐 9. SECURITY\n');
  
  const audit = await call('audit_run', {});
  assert('Security audit runs', typeof audit.data?.score === 'number', JSON.stringify(audit.data));
  console.log(`   🔐 Security Score: ${audit.data?.score}% (${audit.data?.passed}/${audit.data?.total} checks)`);
  
  const soul = await call('audit_soul', {});
  assert('Soul audit', typeof soul.data?.soul_score === 'number', JSON.stringify(soul.data));
  console.log(`   💜 Soul Score: ${soul.data?.soul_score}%`);

  // ─── SCENARIO 10: LEARNING ───
  console.log('\n🧠 10. SELF-LEARNING\n');
  
  const learn = await call('learning_stats', {});
  assert('Learning system active', typeof learn.data?.total_calls === 'number', JSON.stringify(learn.data));
  console.log(`   🧠 Learning: ${learn.data?.total_calls} calls tracked, ${learn.data?.capabilities_tracked} capabilities`);

  // ─── SCENARIO 11: BILLING ───
  console.log('\n💰 11. BILLING\n');
  
  const bill = await call('billing_plan', { tenant_id: 'abe-fenix' });
  assert('Billing returns data', typeof bill.data?.calls === 'number', JSON.stringify(bill.data));
  console.log(`   💰 ABE Fenix: ${bill.data?.calls} calls, $${bill.data?.cost} cost, ${bill.data?.plan} plan`);

  // ─── SCENARIO 12: SCHEDULER ───
  console.log('\n⏰ 12. SCHEDULER\n');
  
  const sched = await call('scheduler_list', {});
  assert('Scheduler active', Array.isArray(sched.data?.tasks), JSON.stringify(sched.data));
  console.log(`   ⏰ ${sched.data?.tasks?.length || 0} scheduled tasks`);

  // ─── SCENARIO 13: SWARM ───
  console.log('\n🐝 13. SWARM\n');
  
  const swarm = await call('swarm_run', { name: 'research-swarm', task: 'analyze ABE Music performance', agents: ['abe_list_artists', 'abe_ceo_dashboard', 'enterprise_score'] });
  assert('Swarm executes', swarm.data?.status === 'completed' || swarm.data?.status === 'running', JSON.stringify(swarm.data));
  console.log(`   🐝 Swarm: ${swarm.data?.status} (${swarm.data?.duration || '?'}ms)`);

  // ─── SCENARIO 14: ALERTS ───
  console.log('\n🚨 14. ALERTS\n');
  
  const alerts = await call('alerts_check', {});
  assert('Alert system active', typeof alerts.data?.count === 'number', JSON.stringify(alerts.data));
  console.log(`   🚨 ${alerts.data?.count} active alerts`);

  // ─── SCENARIO 15: SELF-HEAL ───
  console.log('\n🛠️ 15. SELF-HEAL\n');
  
  const heal = await call('auto_heal', {});
  assert('Auto-heal executes', Array.isArray(heal.data?.actions), JSON.stringify(heal.data));
  console.log(`   🛠️ Auto-heal: ${heal.data?.actions?.length || 0} actions taken`);

  // ─── SCENARIO 16: DASHBOARDS ───
  console.log('\n🖥️ 16. DASHBOARDS\n');
  
  const pages = ['/dashboard', '/adk', '/abe', '/abe-saas', '/abe-services', '/abraham', '/cheatsheet', '/workflow-editor'];
  for (const page of pages) {
    const r = await new Promise(r => http.get({ hostname: '127.0.0.1', port: 18989, path: page, timeout: 5000 }, res => { let d = ''; res.on('data', c => d += c); res.on('end', () => r({ status: res.statusCode, size: d.length })); }).on('error', e => r({ status: 0, size: 0, error: e.message })));
    assert(`Page ${page} responds`, r.status === 200 && r.size > 100, `Status: ${r.status}, Size: ${r.size}`);
  }
  console.log(`   🖥️ ${pages.length} dashboards serving`);

  // ─── SUMMARY ───
  console.log('\n' + '='.repeat(60));
  console.log(`📊 POWER TEST RESULTS:`);
  console.log(`   ✅ ${passed} passed`);
  console.log(`   ❌ ${failed} failed`);
  console.log(`   📊 ${total} total tests`);
  console.log(`   🛠️  ${toolCount} tools MCP`);
  console.log(`   🧠 ${agentList.length} ADK agents`);
  console.log(`   ⚡ ${wfList.length} workflows`);
  console.log('='.repeat(60) + '\n');

  log(`=== POWER TEST END: ${passed}/${total} passed ===`);
  
  if (failed > 0) {
    console.log('\n⚠️  Some tests failed. Check state/logs/power-test.log for details.\n');
    process.exit(1);
  } else {
    console.log('\n✅ ALL TESTS PASSED — SYSTEM IS POWERFUL\n');
    process.exit(0);
  }
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
