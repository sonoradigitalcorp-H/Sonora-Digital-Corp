const http = require('http'); const FASTAPI = { host: '127.0.0.1', port: 8000 };
function api(method, path, body) { return new Promise((resolve) => { const data = body ? JSON.stringify(body) : null; const req = http.request({ hostname: FASTAPI.host, port: FASTAPI.port, path, method, headers: { 'Content-Type': 'application/json' }, timeout: 15000 }, (res) => { let d = ''; res.on('data', c => d += c); res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ raw: d }); } }); }); req.on('error', (e) => resolve({ error: e.message })); if (data) req.write(data); req.end(); }); }
const tools = {
  payments_spei: { description: 'Información SPEI', inputSchema: { type: 'object', properties: {} }, handler: async () => await api('GET', '/api/payments/spei') },
  payments_spei_notify: { description: 'Notifica pago SPEI', inputSchema: { type: 'object', properties: { plan: { type: 'string' }, nicho: { type: 'string' }, reference: { type: 'string' } } }, handler: async (args) => await api('POST', '/api/payments/spei/notify', args) },
  payments_plans: { description: 'Lista planes de pago', inputSchema: { type: 'object', properties: {} }, handler: async () => await api('GET', '/api/payments/plans') },
  payments_create: { description: 'Crea un pago', inputSchema: { type: 'object', properties: { plan: { type: 'string' }, provider: { type: 'string' }, nicho: { type: 'string' } } }, handler: async (args) => await api('POST', '/api/payments/create', args) },
  payments_transaction: { description: 'Obtiene transacción', inputSchema: { type: 'object', properties: { tx_id: { type: 'string' } }, required: ['tx_id'] }, handler: async (args) => await api('GET', `/api/payments/transaction/${args.tx_id}`) },
  payments_webhook: { description: 'Webhook de pagos', inputSchema: { type: 'object', properties: { provider: { type: 'string' } }, required: ['provider'] }, handler: async (args) => await api('POST', `/api/payments/webhook/${args.provider}`, args) },
};
module.exports = { tools };
