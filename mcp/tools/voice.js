const http = require('http');

const FASTAPI_HOST = '127.0.0.1';
const FASTAPI_PORT = 8000;

function apiPost(path, body) {
  return new Promise((resolve) => {
    const data = JSON.stringify(body);
    const req = http.request({
      hostname: FASTAPI_HOST, port: FASTAPI_PORT, path, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': data.length },
      timeout: 30000,
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
  'voice_transcribe': {
    description: 'Transcribe audio a texto usando Whisper',
    inputSchema: {
      type: 'object',
      properties: {
        audio: { type: 'string', description: 'Audio en base64' },
        sample_rate: { type: 'number', description: 'Sample rate del audio (default 16000)' },
      },
      required: ['audio'],
    },
    handler: async (args) => {
      return await apiPost('/api/voice/transcribe', args);
    },
  },

  'voice_speak': {
    description: 'Convierte texto a voz (TTS)',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Texto a convertir en voz' },
        lang: { type: 'string', description: 'Idioma (es, en, etc.)' },
      },
      required: ['text'],
    },
    handler: async (args) => {
      return await apiPost('/api/voice/speak', args);
    },
  },

  'voice_detect_wake': {
    description: 'Detecta si un texto contiene una palabra de activación (wake word)',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Texto a analizar' },
      },
      required: ['text'],
    },
    handler: async (args) => {
      return await apiPost('/api/voice/detect-wake', args);
    },
  },

  'voice_status': {
    description: 'Obtiene el estado del módulo de voz (Whisper, TTS, Wake Word)',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      return await apiGet('/api/voice/status');
    },
  },
};

module.exports = { tools };
