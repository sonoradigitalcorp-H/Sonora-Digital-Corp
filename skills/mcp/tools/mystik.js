/**
 * Mystik AI — MCP Tools
 * Expone Mystik API como tools MCP para que cualquier agente pueda usarlo.
 */
const http = require('http');
const MYSTIK_HOST = process.env.MYSTIK_HOST || '127.0.0.1';
const MYSTIK_PORT = parseInt(process.env.MYSTIK_PORT || '5200');
const OPENROUTER_KEY = process.env.OPENROUTER_API_KEY || '';

function mystikPost(path, data) {
  return new Promise((resolve) => {
    const body = JSON.stringify(data);
    const req = http.request({
      hostname: MYSTIK_HOST, port: MYSTIK_PORT,
      path, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
      timeout: 30000,
    }, (res) => {
      let r = '';
      res.on('data', c => r += c);
      res.on('end', () => { try { resolve(JSON.parse(r)); } catch { resolve({ error: r }); } });
    });
    req.on('timeout', () => { req.destroy(); resolve({ error: 'timeout' }); });
    req.on('error', (e) => resolve({ error: e.message }));
    req.write(body);
    req.end();
  });
}

function mystikGet(path) {
  return new Promise((resolve) => {
    http.get({ hostname: MYSTIK_HOST, port: MYSTIK_PORT, path, timeout: 10000 }, (res) => {
      let r = '';
      res.on('data', c => r += c);
      res.on('end', () => { try { resolve(JSON.parse(r)); } catch { resolve({ error: r }); } });
    }).on('error', (e) => resolve({ error: e.message }));
  });
}

module.exports = [
  // ── Mystik Chat ──
  {
    name: 'mystik_chat',
    description: 'Chatea con Mystik AI. Recibe un mensaje y devuelve respuesta de ventas.',
    input_schema: {
      type: 'object',
      properties: {
        message: { type: 'string', description: 'Mensaje del usuario' },
        tenant: { type: 'string', description: 'Tenant (opcional, default: sonora)' },
      },
      required: ['message'],
    },
    handler: async (args) => {
      const result = await mystikPost('/api/chat', { message: args.message, tenant: args.tenant || 'sonora' });
      return result.response || JSON.stringify(result);
    },
  },

  // ── Mystik Product Catalog ──
  {
    name: 'mystik_products',
    description: 'Lista el catálogo de productos de Sonora Digital Corp.',
    input_schema: { type: 'object', properties: {} },
    handler: async () => {
      const result = await mystikGet('/api/products');
      return result.products || [];
    },
  },

  // ── Mystik Create Lead ──
  {
    name: 'mystik_create_lead',
    description: 'Crea un lead en el CRM desde Mystik.',
    input_schema: {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'Nombre del contacto' },
        email: { type: 'string', description: 'Email del contacto' },
        company: { type: 'string', description: 'Empresa (opcional)' },
        phone: { type: 'string', description: 'Teléfono (opcional)' },
        tenant: { type: 'string', description: 'Tenant (opcional)' },
      },
      required: ['name', 'email'],
    },
    handler: async (args) => {
      const result = await mystikPost('/api/leads', args);
      return result;
    },
  },

  // ── Mystik List Leads ──
  {
    name: 'mystik_list_leads',
    description: 'Lista los leads del CRM filtrados por tenant.',
    input_schema: {
      type: 'object',
      properties: {
        tenant: { type: 'string', description: 'Tenant (opcional)' },
      },
    },
    handler: async (args) => {
      const result = await mystikGet(`/api/leads?tenant=${args.tenant || 'sonora'}`);
      return result.leads || [];
    },
  },

  // ── Mystik Knowledge Search ──
  {
    name: 'mystik_search_knowledge',
    description: 'Busca en la knowledge base de productos SDC.',
    input_schema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Consulta' },
        tenant: { type: 'string', description: 'Tenant (opcional)' },
      },
      required: ['query'],
    },
    handler: async (args) => {
      const result = await mystikPost(`/api/knowledge?query=${encodeURIComponent(args.query)}&tenant=${args.tenant || 'sonora'}`, {});
      return result.results || [];
    },
  },

  // ── Mystik Voice ──
  {
    name: 'mystik_speak',
    description: 'Genera audio TTS con la voz de Mystik.',
    input_schema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Texto a decir' },
      },
      required: ['text'],
    },
    handler: async (args) => {
      const result = await mystikGet(`/api/voice/speak?text=${encodeURIComponent(args.text)}`);
      return { status: 'ok', size: JSON.stringify(result).length, note: 'Audio generado (binario, devuelto en response)' };
    },
  },
];
