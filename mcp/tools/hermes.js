/**
 * Hermes MCP Tools — Telegram, WhatsApp, Desktop messaging via MCP Gateway
 * Proxea llamadas al Hermes Desktop/API de la laptop
 */

const http = require('http');

// Hermes corre en la laptop (o donde esté)
const HERMES_HOST = process.env.HERMES_HOST || '127.0.0.1';
const HERMES_PORT = parseInt(process.env.HERMES_PORT || '8000');
const HERMES_API_KEY = process.env.HERMES_API_KEY || '';

function hermesPost(path, body) {
  return new Promise((resolve) => {
    const data = JSON.stringify(body);
    const req = http.request({
      hostname: HERMES_HOST, port: HERMES_PORT, path, method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
        ...(HERMES_API_KEY ? { 'x-api-key': HERMES_API_KEY } : {}),
      },
      timeout: 15000,
    }, (res) => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ raw: d }); } });
    });
    req.on('error', e => resolve({ error: e.message }));
    req.write(data); req.end();
  });
}

function hermesGet(path) {
  return new Promise((resolve) => {
    const req = http.get({
      hostname: HERMES_HOST, port: HERMES_PORT, path, timeout: 10000,
      headers: HERMES_API_KEY ? { 'x-api-key': HERMES_API_KEY } : {},
    }, (res) => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({ raw: d }); } });
    });
    req.on('error', e => resolve({ error: e.message }));
    req.end();
  });
}

const tools = {
  // ── Telegram ──
  hermes_telegram_send: {
    description: 'Envía mensaje a Telegram via Hermes',
    inputSchema: {
      type: 'object',
      properties: {
        chat_id: { type: 'string', description: 'ID del chat de Telegram' },
        text: { type: 'string', description: 'Texto del mensaje' },
        parse_mode: { type: 'string', enum: ['HTML', 'Markdown'], description: 'Formato' },
      },
      required: ['chat_id', 'text'],
    },
    handler: async (args) => {
      return await hermesPost('/api/hermes/telegram/send', {
        chat_id: args.chat_id,
        text: args.text,
        parse_mode: args.parse_mode || 'HTML',
      });
    },
  },

  // ── WhatsApp ──
  hermes_whatsapp_send: {
    description: 'Envía mensaje a WhatsApp via Hermes',
    inputSchema: {
      type: 'object',
      properties: {
        to: { type: 'string', description: 'Número de teléfono' },
        text: { type: 'string', description: 'Texto del mensaje' },
      },
      required: ['to', 'text'],
    },
    handler: async (args) => {
      return await hermesPost('/api/hermes/whatsapp/send', {
        to: args.to,
        text: args.text,
      });
    },
  },

  // ── Hermes Health ──
  hermes_health: {
    description: 'Estado del agente Hermes',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      return await hermesGet('/health');
    },
  },

  // ── Hermes Bridge Status ──
  hermes_bridge: {
    description: 'Estado del bridge Hermes-JARVIS',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      return await hermesGet('/api/hermes/bridge');
    },
  },
};

module.exports = { tools };
