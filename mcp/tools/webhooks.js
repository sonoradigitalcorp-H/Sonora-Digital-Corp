const http = require('http');
const FASTAPI = { host: '127.0.0.1', port: 8000 };

function api(method, path, body) {
  return new Promise((resolve) => {
    const data = body ? JSON.stringify(body) : null;
    const req = http.request({ hostname: FASTAPI.host, port: FASTAPI.port, path, method,
      headers: { 'Content-Type': 'application/json' }, timeout: 30000 }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ raw: d }); } });
    });
    req.on('error', (e) => resolve({ error: e.message }));
    if (data) req.write(data);
    req.end();
  });
}

const tools = {
  webhook_backup: {
    description: 'Trigger backup via webhook',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => await api('POST', '/api/webhook/n8n-backup'),
  },
  webhook_healthcheck: {
    description: 'Trigger healthcheck via webhook',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => await api('POST', '/api/webhook/n8n-healthcheck'),
  },
  webhook_incoming: {
    description: 'Webhook de entrada desde n8n',
    inputSchema: { type: 'object', properties: { data: { type: 'object' } } },
    handler: async (args) => await api('POST', '/api/webhook/n8n-incoming', args.data || args),
  },
  webhook_status: {
    description: 'Estado de los webhooks configurados',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => await api('GET', '/api/webhook/n8n-status'),
  },
};

module.exports = { tools };
