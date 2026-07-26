const http = require('http');
const FASTAPI = { host: '127.0.0.1', port: 8000 };

function api(method, path, body) {
  return new Promise((resolve) => {
    const data = body ? JSON.stringify(body) : null;
    const req = http.request({ hostname: FASTAPI.host, port: FASTAPI.port, path, method,
      headers: { 'Content-Type': 'application/json', ...(data ? { 'Content-Length': data.length } : {}) }, timeout: 10000 }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ raw: d }); } });
    });
    req.on('error', (e) => resolve({ error: e.message }));
    if (data) req.write(data);
    req.end();
  });
}

const tools = {
  sessions_list: {
    description: 'Lista sesiones del sistema',
    inputSchema: { type: 'object', properties: { pinned: { type: 'boolean' }, project: { type: 'string' }, tag: { type: 'string' }, limit: { type: 'number' } } },
    handler: async (args) => {
      const qs = new URLSearchParams();
      if (args.pinned !== undefined) qs.set('pinned', args.pinned);
      if (args.project) qs.set('project', args.project);
      if (args.tag) qs.set('tag', args.tag);
      if (args.limit) qs.set('limit', args.limit);
      return await api('GET', '/api/sessions?' + qs.toString());
    },
  },
  sessions_search: {
    description: 'Busca sesiones por query',
    inputSchema: { type: 'object', properties: { q: { type: 'string' } }, required: ['q'] },
    handler: async (args) => await api('GET', '/api/sessions/search?q=' + encodeURIComponent(args.q)),
  },
  sessions_get: {
    description: 'Obtiene una sesión por ID',
    inputSchema: { type: 'object', properties: { session_id: { type: 'string' } }, required: ['session_id'] },
    handler: async (args) => await api('GET', '/api/sessions/' + args.session_id),
  },
  sessions_create: {
    description: 'Crea una nueva sesión',
    inputSchema: { type: 'object', properties: { title: { type: 'string' }, project: { type: 'string' }, tags: { type: 'array', items: { type: 'string' } } } },
    handler: async (args) => await api('POST', '/api/sessions', args),
  },
  sessions_delete: {
    description: 'Elimina una sesión',
    inputSchema: { type: 'object', properties: { session_id: { type: 'string' } }, required: ['session_id'] },
    handler: async (args) => await api('DELETE', '/api/sessions/' + args.session_id),
  },
};

module.exports = { tools };
