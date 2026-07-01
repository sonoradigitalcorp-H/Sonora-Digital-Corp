/**
 * OpenClaw MCP Tools — 55 specialized skills via MCP Gateway
 * Proxea llamadas al OpenClaw Gateway de la laptop
 */

const http = require('http');

const OC_HOST = process.env.OPENCLAW_HOST || '127.0.0.1';
const OC_PORT = parseInt(process.env.OPENCLAW_PORT || '18789');

function ocGet(path) {
  return new Promise((resolve) => {
    const req = http.get({ hostname: OC_HOST, port: OC_PORT, path, timeout: 10000 }, (res) => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ raw: d }); } });
    });
    req.on('error', e => resolve({ error: e.message }));
    req.end();
  });
}

function ocPost(path, body) {
  return new Promise((resolve) => {
    const data = JSON.stringify(body || {});
    const req = http.request({ hostname: OC_HOST, port: OC_PORT, path, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) }, timeout: 15000 }, (res) => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ raw: d }); } });
    });
    req.on('error', e => resolve({ error: e.message }));
    req.write(data); req.end();
  });
}

const tools = {
  openclaw_health: {
    description: 'Estado del gateway OpenClaw',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => await ocGet('/health'),
  },
  openclaw_skills: {
    description: 'Lista skills disponibles en OpenClaw',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => await ocGet('/skills'),
  },
  openclaw_execute: {
    description: 'Ejecuta una skill de OpenClaw',
    inputSchema: { type: 'object', properties: {
      skill: { type: 'string', description: 'Nombre de la skill' },
      params: { type: 'object', description: 'Parámetros' },
    }, required: ['skill'] },
    handler: async (args) => await ocPost(`/skill/${args.skill}/execute`, args.params || {}),
  },
  openclaw_browser: {
    description: 'Abre navegador y navega a URL via OpenClaw',
    inputSchema: { type: 'object', properties: {
      url: { type: 'string', description: 'URL a navegar' },
    }, required: ['url'] },
    handler: async (args) => await ocPost('/skill/browser/navigate', { url: args.url }),
  },
  openclaw_agents: {
    description: 'Lista agentes disponibles en OpenClaw',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => await ocGet('/agents'),
  },
};

module.exports = { tools };
