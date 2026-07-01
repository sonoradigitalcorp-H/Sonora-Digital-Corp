const http = require('http');

const FASTAPI_HOST = '127.0.0.1';
const FASTAPI_PORT = 8000;

function apiGet(path) {
  return new Promise((resolve) => {
    const req = http.get({ hostname: FASTAPI_HOST, port: FASTAPI_PORT, path, timeout: 10000 }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch { resolve({ raw: data }); }
      });
    });
    req.on('error', (e) => resolve({ error: e.message }));
    req.on('timeout', () => { req.destroy(); resolve({ error: 'Timeout' }); });
  });
}

const tools = {
  'enterprise_score': {
    description: 'Obtiene el Enterprise Score actual (10 métricas, max 100)',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      return await apiGet('/api/enterprise-score');
    },
  },

  'enterprise_score_history': {
    description: 'Obtiene el historial del Enterprise Score (últimos 100 registros)',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      return await apiGet('/api/enterprise-score/history');
    },
  },
};

module.exports = { tools };
