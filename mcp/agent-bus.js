/**
 * Agent Bus — Redis-based inter-agent communication
 * 
 * Patrón pub/sub para que agentes se comuniquen via Redis:
 * - Agent publica evento en Redis Stream o Pub/Sub
 * - Otros agentes (o el mismo Mystik AI) consumen y reaccionan
 * 
 * Canales:
 *   agent:messages     — Mensajes entre agentes (stream)
 *   agent:context      — Contexto compartido entre agentes
 *   agent:events       — Eventos del sistema
 *   agent:commands     — Comandos de un agente a otro
 */

const REDIS_HOST = process.env.REDIS_HOST || '127.0.0.1';
const REDIS_PORT = parseInt(process.env.REDIS_PORT || '6379');
const REDIS_PASS = process.env.REDIS_PASSWORD || '';

let redis = null;

async function connect() {
  if (redis) return redis;
  try {
    const Redis = require('redis');
    const client = Redis.createClient({
      url: `redis://${REDIS_PASS ? ':' + REDIS_PASS + '@' : ''}${REDIS_HOST}:${REDIS_PORT}`,
    });
    await client.connect();
    redis = client;
    console.log('[agent-bus] Connected to Redis');
    return redis;
  } catch (e) {
    console.error('[agent-bus] Redis unavailable:', e.message);
    return null;
  }
}

// ── Publish a message to the agent bus ──
async function publish(channel, message) {
  const client = await connect();
  if (!client) return { error: 'Redis unavailable' };
  try {
    const msg = typeof message === 'string' ? message : JSON.stringify(message);
    await client.publish(channel, msg);
    return { status: 'published', channel, timestamp: new Date().toISOString() };
  } catch (e) {
    return { error: e.message };
  }
}

// ── Send a command to a specific agent ──
async function sendCommand(targetAgent, command, payload) {
  return await publish('agent:commands', {
    target: targetAgent,
    command,
    payload,
    sender: 'mystik',
    timestamp: new Date().toISOString(),
  });
}

// ── Share context between agents ──
async function shareContext(key, value, ttl = 3600) {
  const client = await connect();
  if (!client) return { error: 'Redis unavailable' };
  try {
    const val = typeof value === 'string' ? value : JSON.stringify(value);
    await client.set(`agent:ctx:${key}`, val, { EX: ttl });
    await publish('agent:context', { key, updated_at: new Date().toISOString() });
    return { status: 'context_shared', key };
  } catch (e) {
    return { error: e.message };
  }
}

// ── Get shared context ──
async function getContext(key) {
  const client = await connect();
  if (!client) return null;
  try {
    const val = await client.get(`agent:ctx:${key}`);
    return val ? JSON.parse(val) : null;
  } catch {
    return null;
  }
}

// ── List all shared context keys ──
async function listContext(pattern = 'agent:ctx:*') {
  const client = await connect();
  if (!client) return [];
  try {
    const keys = await client.keys(pattern);
    const values = [];
    for (const key of keys) {
      const val = await client.get(key);
      values.push({ key: key.replace('agent:ctx:', ''), value: val ? JSON.parse(val) : null });
    }
    return values;
  } catch {
    return [];
  }
}

module.exports = { publish, sendCommand, shareContext, getContext, listContext, connect };
