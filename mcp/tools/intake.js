/**
 * Intake System — Abraham alimenta el sistema desde cualquier canal:
 * Email, archivos, voz, texto, fotos, videos → todo se procesa solo
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const INBOX_DIR = path.join(__dirname, '..', '..', 'state', 'inbox');
const PROCESSED_DIR = path.join(INBOX_DIR, 'processed');
const EVENTS_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'events.jsonl');
const KNOWLEDGE_FILE = path.join(__dirname, '..', '..', 'state', 'knowledge.json');

fs.mkdirSync(INBOX_DIR, { recursive: true });
fs.mkdirSync(PROCESSED_DIR, { recursive: true });

function _emit(event, detail) {
  try {
    const entry = JSON.stringify({ event, producer: 'intake', timestamp: new Date().toISOString(), payload: detail }) + '\n';
    fs.appendFileSync(EVENTS_FILE, entry);
  } catch {}
}

function _saveKnowledge(data) {
  let existing = [];
  try {
    if (fs.existsSync(KNOWLEDGE_FILE)) existing = JSON.parse(fs.readFileSync(KNOWLEDGE_FILE, 'utf-8'));
  } catch {}
  existing.push({ ...data, ingested_at: new Date().toISOString() });
  try { fs.writeFileSync(KNOWLEDGE_FILE, JSON.stringify(existing, null, 2)); } catch {}
}

function _classify(text) {
  const t = (text || '').toLowerCase();
  if (t.includes('stream') || t.includes('reproducci') || t.includes('oyente')) return 'streams';
  if (t.includes('revenue') || t.includes('ingreso') || t.includes('dinero') || t.includes('pago')) return 'revenue';
  if (t.includes('lanzamient') || t.includes('release') || t.includes('canci') || t.includes('tema')) return 'release';
  if (t.includes('artista') || t.includes('firm') || t.includes('nuevo')) return 'artist';
  if (t.includes('evento') || t.includes('concierto') || t.includes('show') || t.includes('tocar')) return 'event';
  if (t.includes('red') || t.includes('instagram') || t.includes('tiktok') || t.includes('youtube')) return 'social';
  if (t.includes('contrato') || t.includes('acuerdo') || t.includes('legal')) return 'contract';
  return 'general';
}

const tools = {
  // ── Text Intake ──
  intake_text: {
    description: 'Abraham envía texto y el sistema lo clasifica y almacena automáticamente',
    inputSchema: { type: 'object', properties: {
      text: { type: 'string', description: 'Texto libre: datos, ideas, updates, lo que sea' },
      source: { type: 'string', enum: ['voice', 'chat', 'telegram', 'email', 'manual'], description: 'Canal de entrada' },
      context: { type: 'string', description: 'Contexto opcional (artista, proyecto, etc.)' },
    }, required: ['text'] },
    handler: async (args) => {
      const category = _classify(args.text);
      const entry = {
        type: 'text', category, source: args.source || 'manual',
        text: args.text, context: args.context || null,
        context: args.text.substring(0, 200),
        summary: args.text.substring(0, 200),
      };
      _saveKnowledge(entry);
      _emit('intake_processed', { type: 'text', category, source: args.source || 'manual' });
      return {
        status: 'processed', category,
        message: `✅ Recibido y clasificado como: ${category}`,
        context: args.text.length > 100 ? args.text.substring(0, 100) + '...' : args.text,
      };
    },
  },

  // ── Voice Intake (texto desde voz) ──
  intake_voice: {
    description: 'Abraham dicta por voz y el sistema procesa la información',
    inputSchema: { type: 'object', properties: {
      transcript: { type: 'string', description: 'Texto transcrito desde voz' },
      context: { type: 'string' },
    }, required: ['transcript'] },
    handler: async (args) => {
      const category = _classify(args.transcript);
      const entry = { type: 'voice', category, transcript: args.transcript, context: args.context || null, summary: args.transcript.substring(0, 200) };
      _saveKnowledge(entry);
      _emit('intake_processed', { type: 'voice', category });
      return { status: 'processed', category, transcript: args.transcript.substring(0, 200) };
    },
  },

  // ── File Intake ──
  intake_file: {
    description: 'Abraham sube archivos (PDF, Excel, CSV, imágenes, audio, video) y el sistema los procesa',
    inputSchema: { type: 'object', properties: {
      filename: { type: 'string', description: 'Nombre del archivo' },
      content_base64: { type: 'string', description: 'Contenido del archivo en base64' },
      context: { type: 'string' },
    }, required: ['filename'] },
    handler: async (args) => {
      const ext = path.extname(args.filename).toLowerCase();
      const filePath = path.join(INBOX_DIR, args.filename);

      // Save file
      if (args.content_base64) {
        try { fs.writeFileSync(filePath, Buffer.from(args.content_base64, 'base64')); }
        catch { return { error: 'Error guardando archivo' }; }
      }

      let extracted = '';
      let category = 'general';

      // Process by type
      if (['.txt', '.csv', '.json', '.xml', '.md'].includes(ext)) {
        extracted = fs.readFileSync(filePath, 'utf-8').substring(0, 2000);
        category = _classify(extracted);
      } else if (['.jpg', '.jpeg', '.png', '.gif', '.webp'].includes(ext)) {
        const size = fs.statSync(filePath).size;
        extracted = `[Imagen: ${args.filename}, ${(size/1024).toFixed(1)}KB]`;
        category = 'media';
      } else if (['.mp3', '.wav', '.ogg', '.m4a'].includes(ext)) {
        extracted = `[Audio: ${args.filename}]`;
        category = 'media';
      } else if (['.mp4', '.mov', '.avi', '.mkv'].includes(ext)) {
        extracted = `[Video: ${args.filename}]`;
        category = 'media';
      } else if (['.pdf'].includes(ext)) {
        extracted = `[PDF: ${args.filename}]`;
        category = 'document';
      } else if (['.xlsx', '.xls'].includes(ext)) {
        extracted = `[Excel: ${args.filename}]`;
        category = 'data';
      }

      const entry = { type: 'file', category, filename: args.filename, ext, size: fs.existsSync(filePath) ? fs.statSync(filePath).size : 0, extracted: extracted.substring(0, 500), context: args.context || null };
      _saveKnowledge(entry);
      _emit('intake_processed', { type: 'file', category, filename: args.filename });

      return {
        status: 'processed', category, filename: args.filename, ext,
        size: entry.size, preview: extracted.substring(0, 300),
        message: `✅ Archivo recibido: ${args.filename} (${category})`,
      };
    },
  },

  // ── Email Intake ──
  intake_email: {
    description: 'Abraham reenvía emails y el sistema extrae datos automáticamente',
    inputSchema: { type: 'object', properties: {
      from: { type: 'string' }, subject: { type: 'string' }, body: { type: 'string' },
      attachments: { type: 'array', items: { type: 'object' } },
    }, required: ['from', 'subject', 'body'] },
    handler: async (args) => {
      const category = _classify(args.subject + ' ' + args.body);
      const entry = { type: 'email', category, from: args.from, subject: args.subject, body_preview: args.body.substring(0, 500), attachments: (args.attachments || []).length, context: args.subject };
      _saveKnowledge(entry);
      _emit('intake_processed', { type: 'email', category, from: args.from });
      return { status: 'processed', category, from: args.from, subject: args.subject };
    },
  },

  // ── Intake Stats ──
  intake_stats: {
    description: 'Resumen de toda la información que Abraham ha ingresado al sistema',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      let knowledge = [];
      try { if (fs.existsSync(KNOWLEDGE_FILE)) knowledge = JSON.parse(fs.readFileSync(KNOWLEDGE_FILE, 'utf-8')); } catch {}
      const byType = {}, byCategory = {};
      knowledge.forEach(k => {
        byType[k.type] = (byType[k.type] || 0) + 1;
        byCategory[k.category] = (byCategory[k.category] || 0) + 1;
      });
      const fileCount = fs.readdirSync(INBOX_DIR).filter(f => f !== 'processed').length;
      return {
        total_entries: knowledge.length, files_in_inbox: fileCount,
        by_type: byType, by_category: byCategory,
        recent: knowledge.slice(-10).map(k => ({ type: k.type, category: k.category, summary: (k.summary || k.text || k.transcript || '').substring(0, 100), ingested_at: k.ingested_at })),
      };
    },
  },

  // ── Query Abraham's Knowledge ──
  intake_query: {
    description: 'Abraham pregunta algo y el sistema busca en todo lo que ha ingresado',
    inputSchema: { type: 'object', properties: { query: { type: 'string' } }, required: ['query'] },
    handler: async (args) => {
      let knowledge = [];
      try { if (fs.existsSync(KNOWLEDGE_FILE)) knowledge = JSON.parse(fs.readFileSync(KNOWLEDGE_FILE, 'utf-8')); } catch {}
      const q = args.query.toLowerCase();
      const results = knowledge.filter(k => {
        const searchText = JSON.stringify(k).toLowerCase();
        return searchText.includes(q);
      }).slice(-10);
      return {
        query: args.query, results_count: results.length,
        results: results.map(k => ({ type: k.type, category: k.category, summary: (k.summary || k.text || k.transcript || k.subject || '').substring(0, 200), ingested_at: k.ingested_at })),
      };
    },
  },
};

module.exports = { tools };
