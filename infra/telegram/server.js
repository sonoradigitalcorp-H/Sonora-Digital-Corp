// Forzar IPv4 — Docker no routea IPv6, Telegram se cae en silencio
const dns = require('dns');
dns.setDefaultResultOrder('ipv4first');

const { Telegraf } = require('telegraf');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });
const express = require('express');
const { startAlertScheduler } = require('./sat-alerts');
const log = require('./logger');

const API_BASE = process.env.API_BASE || 'http://api:8000';
const DEFAULT_BOT_TOKEN = process.env.DEFAULT_BOT_TOKEN || process.env.SONORA_BOT_TOKEN;

// ── LangFuse tracing ──────────────────────────────────────────────────────────
const LANGFUSE_HOST = process.env.LANGFUSE_HOST || 'http://localhost:3000';
const LF_PUBLIC_KEY = process.env.LANGFUSE_PUBLIC_KEY || 'pk-lf-sdc-2026';

async function traceLangFuse(name, input, output, metadata = {}) {
  try {
    await axios.post(`${LANGFUSE_HOST}/api/public/traces`, {
      name,
      input: typeof input === 'string' ? { text: input.slice(0, 200) } : input,
      output: typeof output === 'string' ? { text: output.slice(0, 200) } : output,
      metadata,
      tags: ['sdc-core', 'telegram'],
    }, {
      headers: { 'Authorization': `Bearer ${LF_PUBLIC_KEY}`, 'Content-Type': 'application/json' },
      timeout: 3000,
    });
  } catch (e) {
    log.warn(`[LangFuse] trace error: ${e.message}`);
  }
}

// ── Ollama Local (modelo potente local) ─────────────────────────────────────────
const OLLAMA_BASE = process.env.OLLAMA_BASE || 'http://localhost:11434';
const OLLAMA_MODEL = process.env.OLLAMA_MODEL || 'qwen3:4b';
const OLLAMA_SYSTEM = `Eres HERMES, asistente de IA de Sonora Digital Corp.
Ayudas a Luis Daniel (CEO) con contabilidad, automatización, código y estrategia de negocio para PYMEs mexicanas.
Responde siempre en español, de forma directa y práctica. Sin rodeos.`;

async function askOllama(message, history = []) {
  const startTime = Date.now();
  const messages = [
    { role: 'system', content: OLLAMA_SYSTEM },
    ...history.slice(-6),
    { role: 'user', content: message },
  ];
  const res = await axios.post(`${OLLAMA_BASE}/api/chat`, {
    model: OLLAMA_MODEL,
    messages,
    stream: false,
    options: { num_predict: 800 },
  }, {
    timeout: 120000,
  });
  const reply = res.data?.message?.content || res.data?.response || 'Sin respuesta.';
  const duration = Date.now() - startTime;
  traceLangFuse('telegram.askOllama', { message, history_length: history.length },
    { reply_length: reply.length },
    { duration_ms: duration, cost_usd: 0, model: OLLAMA_MODEL, agent: 'telegram.ollama', tenant: 'sdc-core' }
  );
  return reply;
}

// Historial de conversación por usuario (en memoria, se limpia al reiniciar)
const clawdHistory = new Map();

// ── OpenClaw Skills ────────────────────────────────────────────────────────────
const SKILLS_DIR = path.join(__dirname, 'skills');
let skills = [];

// Los skills ABE (abe-*) solo aplican a 'abe-fenix'.
// Skills brain-ask y ayuda-menu aplican a todos los tenants.
// Todo lo demas (fiscal, SAT, CEO) solo aplica a 'default'.
function skillTenants(skill) {
  if (skill.tenants) return skill.tenants;
  const name = skill.name || '';
  if (name.startsWith('abe-') || name === 'musica-derechos-info' || name === 'musica-evento-cotizar') return ['abe-fenix'];
  if (name === 'brain-ask' || name === 'ayuda-menu') return ['default', 'abe-fenix'];
  return ['default'];
}

function loadSkills() {
  if (!fs.existsSync(SKILLS_DIR)) return;
  skills = fs.readdirSync(SKILLS_DIR)
    .filter(f => f.endsWith('.json'))
    .map(f => { try { return JSON.parse(fs.readFileSync(path.join(SKILLS_DIR, f))); } catch { return null; } })
    .filter(Boolean)
    .sort((a, b) => (b.priority || 0) - (a.priority || 0));
  const byTenant = {};
  for (const s of skills) {
    for (const t of skillTenants(s)) {
      (byTenant[t] = byTenant[t] || []).push(s.name);
    }
  }
  log.info(`[Skills] ${skills.length} cargados — default:${(byTenant.default||[]).length} abe-fenix:${(byTenant['abe-fenix']||[]).length}`);
}

function matchSkill(message, tenantId) {
  const lower = message.toLowerCase();
  for (const skill of skills) {
    if (!skill.triggers || skill.triggers.includes('*')) continue;
    if (!skillTenants(skill).includes(tenantId)) continue;
    if (skill.triggers.some(t => lower.includes(t.toLowerCase()))) return skill;
  }
  const fallback = skills.find(s => s.triggers?.includes('*') && skillTenants(s).includes(tenantId)) || null;
  return fallback;
}

async function invokeSkill(skill, message, tenantId) {
  // STATIC — respuesta fija sin llamada API (cero costo de IA)
  if (skill.method === 'STATIC') {
    return skill.response_text || 'Consulta el portal del SAT para más información.';
  }
  // BRAIN — reenvía al Brain IA con contexto específico del skill
  if (skill.method === 'BRAIN') {
    const question = (skill.question_template || '{{message}}')
      .replace('{{message}}', message);
    const res = await axios.post(`${API_BASE}/api/brain/ask`, {
      question, tenant_id: tenantId, channel: 'telegram'
    }, { timeout: 25000 });
    return res.data?.answer || res.data?.respuesta || 'No pude procesar tu consulta.';
  }
  const url = skill.endpoint.replace('http://api:8000', API_BASE);
  if (skill.method === 'GET') {
    const res = await axios.get(url, { timeout: 15000 });
    return skill.response_template
      ? skill.response_template.replace(/\{\{(\w+)\}\}/g, (_, k) => res.data[k] ?? '')
      : JSON.stringify(res.data);
  }
  // Interpolar template con JSON.stringify para escapar correctamente los valores
  const payload = JSON.parse(
    JSON.stringify(skill.payload || {})
      .replace(/"\{\{message\}\}"/g, JSON.stringify(message))
      .replace(/"\{\{tenant_id\}\}"/g, JSON.stringify(tenantId))
  );
  const res = await axios.post(url, payload, { timeout: 20000 });
  return res.data?.[skill.response_field || 'answer'] || 'Procesado.';
}

loadSkills();

// ── Bot Manager (singleton por tenant) ────────────────────────────────────────
const botInstances = new Map(); // tenantId → Telegraf instance

function createTelegrafInstance(tenantId, token) {
  const bot = new Telegraf(token);

  const greetings = {
    'abe-fenix': '🎵 *ABE Fenix* — Música que transforma.\n\nSoy el asistente de Abraham. Aquí puedes:\n• Saber sobre mi música\n• Ver próximos lanzamientos\n• Conectar con mi equipo\n\n_¿En qué te ayudo hoy?_',
  };
  bot.start(async ctx => {
    try {
      const greeting = greetings[tenantId] ||
        `✨ *Hola, soy HERMES*\n\nTu asistente contable inteligente, disponible las 24 horas.\n\n` +
        `Cuéntame lo que necesitas — facturas, impuestos, nómina, importaciones o cualquier duda fiscal.\n\n` +
        `_Solo escríbeme como le escribirías a un contador de confianza._`;
      await ctx.reply(greeting, { parse_mode: 'Markdown' });
    } catch (err) {
      log.error('[bot.start] error:', { err: err.message });
    }
  });

  bot.command('menu', async ctx => {
    try {
      await ctx.reply('¿Qué necesitas hoy?', {
        parse_mode: 'Markdown',
        reply_markup: { inline_keyboard: [
          [{ text: '📄 Necesito una factura',    callback_data: 'action_mve' }],
          [{ text: '🔍 Verificar comprobante',   callback_data: 'action_cfdi' }],
          [{ text: '📊 ¿Cómo voy con el SAT?',  callback_data: 'action_status' }],
          [{ text: '💵 Precio del dólar hoy',   callback_data: 'action_tc' }],
          [{ text: '💬 Tengo una pregunta',      callback_data: 'action_help' }],
        ]}
      });
    } catch (err) {
      log.error('[bot.command/menu] error:', { err: err.message });
    }
  });

  // /ai — Chat directo con Ollama local
  bot.command('ai', async (ctx) => {
    try {
      const question = ctx.message.text.replace(/^\/ai\s*/i, '').trim();
      if (!question) { await ctx.reply('Escríbeme algo después de /ai\nEjemplo: /ai ¿cómo está el sistema?'); return; }
      await ctx.sendChatAction('typing');
      const userId = String(ctx.from.id);
      const history = clawdHistory.get(userId) || [];
      const answer = await askOllama(question, history);
      history.push({ role: 'user', content: question });
      history.push({ role: 'assistant', content: answer });
      clawdHistory.set(userId, history.slice(-12));
      await ctx.reply(answer, { parse_mode: 'Markdown' });
    } catch (err) {
      log.error('[bot.command/ai] error:', { err: err.message });
      await ctx.reply('Ollama no disponible en este momento.');
    }
  });

  // /reset — limpia historial de conversación
  bot.command('reset', async (ctx) => {
    try {
      clawdHistory.delete(String(ctx.from.id));
      await ctx.reply('Historial limpiado. ¿En qué te ayudo?');
    } catch (err) {
      log.error('[bot.command/reset] error:', { err: err.message });
    }
  });

  bot.command('alertas', async (ctx) => {
    try {
      const { getMonthAlerts } = require('./sat-alerts');
      const alerts = getMonthAlerts ? getMonthAlerts() : [];
      if (!alerts || alerts.length === 0) {
        await ctx.reply('✅ Sin alertas fiscales pendientes este mes.');
        return;
      }
      const text = alerts.map(a => `📅 *${a.date}* — ${a.description}`).join('\n');
      await ctx.reply(`*Alertas SAT este mes:*\n\n${text}`, { parse_mode: 'Markdown' });
    } catch (e) {
      log.error('[bot.command/alertas] error:', { err: e.message });
      await ctx.reply('No pude cargar las alertas. Intenta más tarde.');
    }
  });

  bot.command('estado', async (ctx) => {
    try {
      const res = await axios.get(`${API_BASE}/status`, { timeout: 10000 });
      const s = res.data;
      const lines = [
        `*Estado HERMES* — ${new Date().toLocaleString('es-MX')}`,
        `API: ${s?.status === 'ok' ? '✅' : '⚠️'} ${s?.status ?? 'unknown'}`,
        s?.qdrant ? `Qdrant: ${s.qdrant?.status === 'ok' ? '✅' : '⚠️'}` : '',
      ].filter(Boolean);
      await ctx.reply(lines.join('\n'), { parse_mode: 'Markdown' });
    } catch (e) {
      log.error('[bot.command/estado] error:', { err: e.message });
      await ctx.reply('⚠️ No se pudo conectar con la API.');
    }
  });

  bot.on('text', async ctx => {
    await ctx.sendChatAction('typing');
    const msg = ctx.message.text;
    const userId = String(ctx.from.id);
    const CEO_CHAT_ID = process.env.HERMES_ADMIN_CHAT_ID || '';

    try {
      // Modo CEO: si el mensaje viene del dueño, va directo a Ollama
      if (CEO_CHAT_ID && userId === CEO_CHAT_ID) {
        const history = clawdHistory.get(userId) || [];
        const answer = await askOllama(msg, history);
        history.push({ role: 'user', content: msg });
        history.push({ role: 'assistant', content: answer });
        clawdHistory.set(userId, history.slice(-12));
        await ctx.reply(answer, { parse_mode: 'Markdown' });
        return;
      }

      const skill = matchSkill(msg, tenantId);
      let text, actions = [];
      if (skill) {
        text = await invokeSkill(skill, msg, tenantId);
        actions = skill.actions || [];
      } else {
        text = await askOllama(msg);
      }
      if (actions.length > 0) {
        const kb = actions.map(a => [{ text: a.label || a.text, callback_data: a.callback || `action_${a.action}` }]);
        await ctx.reply(text, { parse_mode: 'Markdown', reply_markup: { inline_keyboard: kb } });
      } else {
        await ctx.reply(text, { parse_mode: 'Markdown' });
      }
    } catch (err) {
      log.error(`[${tenantId}] msg error:`, { err: err.message });
      await ctx.reply('Algo salió mal al procesar tu consulta. Por favor intenta de nuevo en un momento.');
    }
  });

  bot.on('callback_query', async ctx => {
    try {
      const action = ctx.callbackQuery.data;
      const replies = {
        action_mve:    '📄 Perfecto. Cuéntame:\n• ¿Qué mercancía o servicio vas a facturar?\n• ¿A qué país va destinado?\n• Valor aproximado en pesos o dólares',
        action_cfdi:   '🔍 Compárteme el folio fiscal (UUID) del comprobante y lo verifico de inmediato.',
        action_status: '📊 Un momento, estoy revisando tu situación con el SAT...',
        action_tc:     '💵 Consultando el tipo de cambio oficial de hoy...',
        action_help:   '💬 Pregúntame lo que necesites: impuestos, nómina, facturas, importaciones o cualquier duda contable. Estoy aquí para ayudarte.',
      };
      if (replies[action]) await ctx.reply(replies[action]);
      await ctx.answerCbQuery();
    } catch (err) {
      log.error('[bot.on/callback_query] error:', { err: err.message });
      try { await ctx.answerCbQuery(); } catch {}
    }
  });

  return bot;
}

// Registrar señales una sola vez al inicio del proceso
let _activeBot = null;
process.on('SIGINT',  () => { if (_activeBot) _activeBot.stop('SIGINT');  process.exit(0); });
process.on('SIGTERM', () => { if (_activeBot) _activeBot.stop('SIGTERM'); process.exit(0); });

const MAX_RETRIES = 20; // máximo 20 intentos antes de rendirse

async function launchBot(tenantId, token, attempt = 1) {
  if (attempt > MAX_RETRIES) {
    log.error(`[${tenantId}] Max reintentos (${MAX_RETRIES}) alcanzado. Bot detenido.`);
    return;
  }

  // Detener instancia anterior y esperar a que cierre su conexión HTTP con Telegram
  const prev = botInstances.get(tenantId);
  if (prev) {
    try { await prev.stop(); } catch {}
    botInstances.delete(tenantId);
    // Esperar 35s para que Telegram libere la sesión de polling
    await new Promise(r => setTimeout(r, 35000));
  }

  const bot = createTelegrafInstance(tenantId, token);
  botInstances.set(tenantId, bot);
  _activeBot = bot;

  try {
    await bot.telegram.getMe();
    bot.startPolling();
    log.info(`[${tenantId}] Bot conectado a Telegram ✅`);
    startAlertScheduler(bot, process.env.HERMES_ALERT_CHANNEL_ID || null);
  } catch (err) {
    const is409 = err.response?.error_code === 409;
    const isNet = err.code === 'ETIMEDOUT' || err.code === 'ECONNREFUSED' || err.type === 'system';
    if (is409 || isNet) {
      const wait = 35000;
      log.warn(`[${tenantId}] ${is409 ? '409 Conflict' : 'Red timeout'} → retry en ${wait/1000}s (intento ${attempt}/${MAX_RETRIES})`);
      setTimeout(() => launchBot(tenantId, token, attempt + 1), wait);
    } else {
      log.error(`[${tenantId}] Error fatal:`, { err: err.message });
    }
  }
}

// ── REST API ───────────────────────────────────────────────────────────────────
const app = express();
app.use(express.json());

// Middleware: autenticación por API key en endpoints de gestión
const MGMT_API_KEY = process.env.MGMT_API_KEY || '';
function requireApiKey(req, res, next) {
  if (!MGMT_API_KEY) return next(); // sin env var → solo accesible desde red interna
  const key = req.headers['x-api-key'] || req.query.apiKey;
  if (key !== MGMT_API_KEY) return res.status(401).json({ error: 'Unauthorized' });
  next();
}

app.post('/:tenantId/start', requireApiKey, (req, res) => {
  const { tenantId } = req.params;
  const token = req.body.token || DEFAULT_BOT_TOKEN;
  if (!token) return res.status(400).json({ error: 'Token requerido' });
  launchBot(tenantId, token);
  res.json({ success: true, message: `Bot ${tenantId} iniciando` });
});

app.post('/:tenantId/stop', requireApiKey, (req, res) => {
  const bot = botInstances.get(req.params.tenantId);
  if (bot) { try { bot.stop(); } catch {} botInstances.delete(req.params.tenantId); }
  res.json({ success: true });
});

app.get('/:tenantId/status', requireApiKey, (req, res) => {
  res.json({ tenantId: req.params.tenantId, active: botInstances.has(req.params.tenantId) });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', activeBots: botInstances.size, skills: skills.length });
});

// ── Multi-tenant bots ──────────────────────────────────────────────────────────
const BOT_TOKENS = [
  { id: 'default',        token: process.env.DEFAULT_BOT_TOKEN,      delay: 40000 },
  { id: 'aurea',          token: process.env.AUREA_BOT_TOKEN,        delay: 50000 },
  { id: 'clawd',          token: process.env.DEEPSEEK_BOT_TOKEN,     delay: 60000 },
  { id: 'abe-fenix',      token: process.env.ABE_FENIX_BOT_TOKEN,    delay: 70000 },
  { id: 'sonora-digital', token: process.env.SONORA_BOT_TOKEN,       delay: 75000 },
  { id: 'aztrotech',      token: process.env.AZTROTECH_BOT_TOKEN,    delay: 80000 },
  { id: 'abe-personal',   token: process.env.ABE_BOT_TOKEN,          delay: 85000 },
  { id: 'mystika',        token: process.env.MYSTIKA_BOT_TOKEN,      delay: 90000 },
];
for (const bot of BOT_TOKENS) {
  if (bot.token) {
    log.info(`[${bot.id}] Bot iniciando...`);
    setTimeout(() => launchBot(bot.id, bot.token), bot.delay);
  }
}

const PORT = process.env.PORT || 3003;
app.listen(PORT, () => log.info(`🤖 Telegram Bot Manager en puerto ${PORT}`));
