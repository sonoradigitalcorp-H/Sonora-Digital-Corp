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

function apiPost(path, body) {
  return new Promise((resolve) => {
    const data = JSON.stringify(body);
    const req = http.request({
      hostname: FASTAPI_HOST, port: FASTAPI_PORT, path, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': data.length },
      timeout: 10000,
    }, (res) => {
      let result = '';
      res.on('data', c => result += c);
      res.on('end', () => {
        try { resolve(JSON.parse(result)); }
        catch { resolve({ raw: result }); }
      });
    });
    req.on('error', (e) => resolve({ error: e.message }));
    req.on('timeout', () => { req.destroy(); resolve({ error: 'Timeout' }); });
    req.write(data);
    req.end();
  });
}

const tools = {
  'sales_capture_lead': {
    description: 'Captura un nuevo lead en el pipeline de ventas',
    inputSchema: {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'Nombre del lead' },
        email: { type: 'string', description: 'Email del lead' },
        phone: { type: 'string', description: 'Teléfono del lead' },
        source: { type: 'string', description: 'Fuente del lead (web_form, whatsapp, telegram, referral)' },
        niche: { type: 'string', description: 'Nicho de negocio' },
        plan_interest: { type: 'string', description: 'Plan de interés' },
      },
      required: ['name', 'email'],
    },
    handler: async (args) => {
      return await apiPost('/api/sales/leads', args);
    },
  },

  'sales_get_lead': {
    description: 'Obtiene un lead por ID',
    inputSchema: {
      type: 'object',
      properties: {
        lead_id: { type: 'string', description: 'ID del lead' },
      },
      required: ['lead_id'],
    },
    handler: async (args) => {
      return await apiGet(`/api/sales/leads/${args.lead_id}`);
    },
  },

  'sales_list_leads': {
    description: 'Lista leads, opcionalmente filtrados por etapa',
    inputSchema: {
      type: 'object',
      properties: {
        stage: { type: 'string', description: 'Filtrar por etapa (lead, qualified, proposal, negotiation, won, lost)' },
      },
    },
    handler: async (args) => {
      const qs = args.stage ? `?stage=${args.stage}` : '';
      return await apiGet(`/api/sales/leads${qs}`);
    },
  },

  'sales_qualify_lead': {
    description: 'Califica un lead (evaluación BANT)',
    inputSchema: {
      type: 'object',
      properties: {
        lead_id: { type: 'string', description: 'ID del lead' },
      },
      required: ['lead_id'],
    },
    handler: async (args) => {
      return await apiPost(`/api/sales/leads/${args.lead_id}/qualify`, {});
    },
  },

  'sales_generate_proposal': {
    description: 'Genera una propuesta para un lead',
    inputSchema: {
      type: 'object',
      properties: {
        lead_id: { type: 'string', description: 'ID del lead' },
      },
      required: ['lead_id'],
    },
    handler: async (args) => {
      return await apiGet(`/api/sales/leads/${args.lead_id}/proposal`);
    },
  },

  'sales_accept_proposal': {
    description: 'Marca propuesta como aceptada por el lead',
    inputSchema: {
      type: 'object',
      properties: {
        lead_id: { type: 'string', description: 'ID del lead' },
      },
      required: ['lead_id'],
    },
    handler: async (args) => {
      return await apiPost(`/api/sales/leads/${args.lead_id}/accept`, {});
    },
  },

  'sales_close_won': {
    description: 'Cierra un deal como ganado',
    inputSchema: {
      type: 'object',
      properties: {
        lead_id: { type: 'string', description: 'ID del lead' },
        payment_ref: { type: 'string', description: 'Referencia de pago' },
        amount: { type: 'number', description: 'Monto del deal' },
      },
      required: ['lead_id'],
    },
    handler: async (args) => {
      return await apiPost(`/api/sales/leads/${args.lead_id}/won`, {
        payment_ref: args.payment_ref || '',
        amount: args.amount || 0,
      });
    },
  },

  'sales_close_lost': {
    description: 'Cierra un deal como perdido',
    inputSchema: {
      type: 'object',
      properties: {
        lead_id: { type: 'string', description: 'ID del lead' },
        reason: { type: 'string', description: 'Razón de pérdida' },
      },
      required: ['lead_id'],
    },
    handler: async (args) => {
      return await apiPost(`/api/sales/leads/${args.lead_id}/lost`, {
        reason: args.reason || '',
      });
    },
  },

  'sales_dashboard': {
    description: 'Obtiene el dashboard del pipeline de ventas',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      return await apiGet('/api/sales/dashboard');
    },
  },
};

module.exports = { tools };
