const http = require('http'); const FASTAPI = { host: '127.0.0.1', port: 8000 };
function api(method, path, body) { return new Promise((resolve) => { const data = body ? JSON.stringify(body) : null; const req = http.request({ hostname: FASTAPI.host, port: FASTAPI.port, path, method, headers: { 'Content-Type': 'application/json' }, timeout: 15000 }, (res) => { let d = ''; res.on('data', c => d += c); res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ raw: d }); } }); }); req.on('error', (e) => resolve({ error: e.message })); if (data) req.write(data); req.end(); }); }
const tools = {
  sdc_plans: { description: 'Lista planes de SDC', inputSchema: { type: 'object', properties: {} }, handler: async () => await api('GET', '/api/sdc/plans') },
  sdc_plan: { description: 'Obtiene detalle de un plan', inputSchema: { type: 'object', properties: { plan_id: { type: 'string' }, nicho: { type: 'string' } }, required: ['plan_id'] }, handler: async (args) => await api('GET', `/api/sdc/plan/${args.plan_id}?nicho=${args.nicho || 'general'}`) },
  sdc_nicho: { description: 'Obtiene perfil de un nicho', inputSchema: { type: 'object', properties: { nicho: { type: 'string' } }, required: ['nicho'] }, handler: async (args) => await api('GET', `/api/sdc/nicho/${args.nicho}`) },
  sdc_onboarding: { description: 'Procesa onboarding de SDC', inputSchema: { type: 'object', properties: {} }, handler: async (args) => await api('POST', '/api/sdc/onboarding', args) },
  sdc_onboarding_mystic: { description: 'Onboarding interactivo con Mystic', inputSchema: { type: 'object', properties: { message: { type: 'string' }, step: { type: 'number' }, tipo: { type: 'string' }, nicho: { type: 'string' } } }, handler: async (args) => await api('POST', '/api/sdc/onboarding/mystic', args) },
};
module.exports = { tools };
