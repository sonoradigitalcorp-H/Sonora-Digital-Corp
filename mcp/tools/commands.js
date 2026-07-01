const http = require('http'); const FASTAPI = { host: '127.0.0.1', port: 8000 };
function api(method, path, body) { return new Promise((resolve) => { const data = body ? JSON.stringify(body) : null; const req = http.request({ hostname: FASTAPI.host, port: FASTAPI.port, path, method, headers: { 'Content-Type': 'application/json' }, timeout: 10000 }, (res) => { let d = ''; res.on('data', c => d += c); res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ raw: d }); } }); }); req.on('error', (e) => resolve({ error: e.message })); if (data) req.write(data); req.end(); }); }
const tools = {
  commands_execute: { description: 'Ejecuta un comando del sistema (/help, /clear, /status, /skills, /voice, /theme, /gsd, /wrap-up, /reflect, /learn)', inputSchema: { type: 'object', properties: { command: { type: 'string' }, session_id: { type: 'string' } }, required: ['command'] }, handler: async (args) => await api('POST', '/api/commands', args) },
};
module.exports = { tools };
