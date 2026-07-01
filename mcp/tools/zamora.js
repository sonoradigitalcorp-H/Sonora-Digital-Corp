const http = require('http'); const FASTAPI = { host: '127.0.0.1', port: 8000 };
function api(method, path, body) { return new Promise((resolve) => { const data = body ? JSON.stringify(body) : null; const req = http.request({ hostname: FASTAPI.host, port: FASTAPI.port, path, method, headers: { 'Content-Type': 'application/json' }, timeout: 10000 }, (res) => { let d = ''; res.on('data', c => d += c); res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ raw: d }); } }); }); req.on('error', (e) => resolve({ error: e.message })); if (data) req.write(data); req.end(); }); }
const tools = {
  zamora_services: { description: 'Lista servicios de Zamora Brand Studio', inputSchema: { type: 'object', properties: {} }, handler: async () => await api('GET', '/api/zamora/services') },
  zamora_pricing: { description: 'Precios de Zamora Brand Studio', inputSchema: { type: 'object', properties: {} }, handler: async () => await api('GET', '/api/zamora/pricing') },
  zamora_portfolio: { description: 'Portfolio de Zamora Brand Studio', inputSchema: { type: 'object', properties: {} }, handler: async () => await api('GET', '/api/zamora/portfolio') },
};
module.exports = { tools };
