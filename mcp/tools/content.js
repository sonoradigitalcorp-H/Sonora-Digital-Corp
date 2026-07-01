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
  content_generate: {
    description: 'Genera contenido desde una plantilla',
    inputSchema: { type: 'object', properties: {
      template: { type: 'string' }, topic: { type: 'string' }, text: { type: 'string' },
      research: { type: 'string' }, script: { type: 'string' }, voice: { type: 'string' },
      formats: { type: 'array', items: { type: 'string' } }, data: { type: 'object' },
    }, required: ['template'] },
    handler: async (args) => await api('POST', '/api/content/generate', args),
  },
  content_deliver: {
    description: 'Entrega contenido a un canal (YouTube, Instagram, TikTok)',
    inputSchema: { type: 'object', properties: { channel: { type: 'string' }, content_id: { type: 'string' } }, required: ['channel'] },
    handler: async (args) => await api('POST', '/api/content/deliver', args),
  },
  content_list: {
    description: 'Lista contenido generado',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => await api('GET', '/api/content/list'),
  },
};

module.exports = { tools };
