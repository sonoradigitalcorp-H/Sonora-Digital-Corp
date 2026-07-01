/**
 * ═══════════════════════════════════════════════════════════════
 * Sonora Provider Router v1.0 — Multi-Provider Abstraction
 * ═══════════════════════════════════════════════════════════════
 * Permite elegir modelo/proveedor por capability o por agente.
 * Soporta: opencode-go, openrouter, google-gemini
 * Fallback automático si un provider falla.
 * ═══════════════════════════════════════════════════════════════
 */

const http = require('http');
const https = require('https');
const { execSync } = require('child_process');

const PROVIDERS = {
  'opencode-go': {
    base_url: 'https://opencode.ai/zen/go/v1',
    api_key: () => process.env.OPENCODE_API_KEY || '',
    models: {
      'deepseek-v4-flash': { context: 32768, cost_per_1k: 0.0001, free: false },
      'deepseek-v4-flash-free': { context: 8192, cost_per_1k: 0.0, free: true },
    },
    default_model: 'deepseek-v4-flash',
    weight: 1,
  },
  'openrouter': {
    base_url: 'https://openrouter.ai/api/v1',
    api_key: () => process.env.OPENROUTER_API_KEY || '',
    models: {
      'opencode/deepseek-v4-flash-free': { context: 8192, cost_per_1k: 0.0, free: true },
      'openai/gpt-4o': { context: 128000, cost_per_1k: 0.0025, free: false },
      'anthropic/claude-3.5-sonnet': { context: 200000, cost_per_1k: 0.003, free: false },
      'google/gemini-2.5-flash': { context: 1000000, cost_per_1k: 0.00015, free: false },
      'meta-llama/llama-3.3-70b': { context: 128000, cost_per_1k: 0.0005, free: false },
    },
    default_model: 'opencode/deepseek-v4-flash-free',
    weight: 1,
  },
  'ollama': {
    base_url: 'http://127.0.0.1:11434',
    api_key: () => '',
    models: {
      'qwen2.5:1.5b': { context: 32768, cost_per_1k: 0.0, free: true, local: true },
      'qwen3:1.7b': { context: 16384, cost_per_1k: 0.0, free: true, local: true },
      'qwen3:4b': { context: 32768, cost_per_1k: 0.0, free: true, local: true },
      'llama3.2:3b': { context: 8192, cost_per_1k: 0.0, free: true, local: true },
      'deepseek-r1:7b': { context: 16384, cost_per_1k: 0.0, free: true, local: true },
      'nomic-embed-text': { context: 8192, cost_per_1k: 0.0, free: true, local: true, embedding: true },
    },
    default_model: 'qwen2.5:1.5b',
    weight: 10,
  },
};

const CAPABILITY_MODEL_MAP = {
  'routing': { provider: 'ollama', model: 'qwen2.5:1.5b' },
  'classification': { provider: 'ollama', model: 'qwen2.5:1.5b' },
  'research': { provider: 'ollama', model: 'llama3.2:3b' },
  'code': { provider: 'ollama', model: 'llama3.2:3b' },
  'sales': { provider: 'ollama', model: 'llama3.2:3b' },
  'content': { provider: 'ollama', model: 'llama3.2:3b' },
  'analysis': { provider: 'ollama', model: 'llama3.2:3b' },
  'deep_analysis': { provider: 'ollama', model: 'deepseek-r1:7b' },
  'embedding': { provider: 'ollama', model: 'nomic-embed-text' },
  'agent': { provider: 'opencode-go', model: 'deepseek-v4-flash' },
  'default': { provider: 'ollama', model: 'qwen2.5:1.5b' },
};

function getProvider(providerName) {
  const p = PROVIDERS[providerName];
  if (!p) throw new Error(`Provider no encontrado: ${providerName}`);
  return { ...p, api_key: p.api_key() };
}

function resolveForCapability(capability) {
  const mapping = CAPABILITY_MODEL_MAP[capability] || CAPABILITY_MODEL_MAP.default;
  const provider = getProvider(mapping.provider);
  const model = provider.models[mapping.model] ? mapping.model : provider.default_model;
  return { provider: mapping.provider, model, config: provider.models[model] || {} };
}

function listModels() {
  const models = [];
  for (const [pName, pConfig] of Object.entries(PROVIDERS)) {
    for (const [mName, mConfig] of Object.entries(pConfig.models)) {
      models.push({ provider: pName, model: mName, ...mConfig });
    }
  }
  return models;
}

const FINOPS_FILE = require('path').join(__dirname, '..', '..', 'state', 'finops.jsonl');

function _getInputCost(model) {
  const costs = {
    'deepseek-v4-flash-free': 0, 'deepseek-v4-flash': 0.0001,
    'gpt-4o': 0.0025, 'gpt-4o-mini': 0.00015,
    'claude-3.5-sonnet': 0.003, 'claude-3-haiku': 0.00025,
    'gemini-2.5-flash': 0.00015, 'gemini-2.0-pro': 0.002,
    'llama-3.3-70b': 0.00059, 'llama-3.1-8b': 0.00005,
    'deepseek-v3': 0.0007, 'deepseek-r1': 0.00055,
    'qwen2.5:1.5b': 0, 'qwen3:1.7b': 0, 'qwen3:4b': 0, 'llama3.2:3b': 0, 'deepseek-r1:7b': 0, 'nomic-embed-text': 0,
  };
  return costs[model] || 0.001;
}

function _getOutputCost(model) {
  const costs = {
    'deepseek-v4-flash-free': 0, 'deepseek-v4-flash': 0.0001,
    'gpt-4o': 0.01, 'gpt-4o-mini': 0.0006,
    'claude-3.5-sonnet': 0.015, 'claude-3-haiku': 0.00125,
    'gemini-2.5-flash': 0.0004, 'gemini-2.0-pro': 0.005,
    'llama-3.3-70b': 0.00079, 'llama-3.1-8b': 0.00008,
    'deepseek-v3': 0.0028, 'deepseek-r1': 0.00219,
  };
  return costs[model] || 0.002;
}

function _logFinOps({ provider, model, capability, input_tokens, output_tokens, cost, latency_ms, status }) {
  try {
    const ts = new Date().toISOString();
    const entry = JSON.stringify({
      event: 'ai_call',
      timestamp: ts,
      provider,
      model,
      capability: capability || 'unknown',
      input_tokens: input_tokens || 0,
      output_tokens: output_tokens || 0,
      total_tokens: (input_tokens || 0) + (output_tokens || 0),
      cost: cost || 0,
      latency_ms: latency_ms || 0,
      status: status || 'success',
    });
    require('fs').appendFileSync(FINOPS_FILE, entry + '\n');
  } catch (e) { /* finops file not available */ }
}

async function _ollamaChat(model, messages, timeout) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ model, messages, stream: false });
    const req = http.request({
      hostname: '127.0.0.1', port: 11434, path: '/api/chat', method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
      timeout,
    }, (res) => {
      let data = ''; res.on('data', c => data += c);
      res.on('end', () => {
        const latency = Date.now() - start;
        try {
          const parsed = JSON.parse(data);
          const content = parsed.message?.content || '';
          const usage = { prompt_tokens: parsed.prompt_eval_count || 0, completion_tokens: parsed.eval_count || 0 };
          _logFinOps({ provider: 'ollama', model, capability: 'local', input_tokens: usage.prompt_tokens, output_tokens: usage.completion_tokens, cost: 0, latency_ms: latency, status: 'success' });
          resolve({ choices: [{ message: { content }, finish_reason: 'stop' }], usage, model });
        } catch { reject(new Error(`Ollama: respuesta inválida`)); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error(`Ollama timeout: ${model}`)); });
    req.write(body); req.end();
  });
}

async function chatCompletion({ provider: providerName, model, messages, stream = false, timeout = 30000, capability }) {
  if (providerName === 'ollama') {
    return await _ollamaChat(model, messages, timeout);
  }
  const provider = getProvider(providerName);
  const baseUrl = provider.base_url;
  const apiKey = provider.api_key;

  const body = JSON.stringify({
    model,
    messages,
    stream,
    ...(stream ? { stream_options: { include_usage: true } } : {}),
  });

  const start = Date.now();
  return new Promise((resolve, reject) => {
    const url = new URL(baseUrl + '/chat/completions');
    const transport = url.protocol === 'https:' ? https : http;

    const req = transport.request({
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'Content-Length': Buffer.byteLength(body),
      },
      timeout,
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const latency = Date.now() - start;
        try {
          const parsed = JSON.parse(data);
          if (res.statusCode !== 200) {
            _logFinOps({ provider: providerName, model, capability, input_tokens: 0, output_tokens: 0, cost: 0, latency_ms: latency, status: 'error' });
            reject(new Error(`Provider ${providerName}: ${res.statusCode} ${parsed.error?.message || data}`));
          } else {
            const usage = parsed.usage || {};
            const inTok = usage.prompt_tokens || 0;
            const outTok = usage.completion_tokens || 0;
            const cost = (inTok / 1000 * _getInputCost(model)) + (outTok / 1000 * _getOutputCost(model));
            _logFinOps({ provider: providerName, model, capability, input_tokens: inTok, output_tokens: outTok, cost, latency_ms: latency, status: 'success' });
            resolve(parsed);
          }
        } catch {
          _logFinOps({ provider: providerName, model, capability, input_tokens: 0, output_tokens: 0, cost: 0, latency_ms: latency, status: 'error' });
          reject(new Error(`Provider ${providerName}: respuesta inválida`));
        }
      });
    });

    req.on('error', (e) => {
      _logFinOps({ provider: providerName, model, capability, input_tokens: 0, output_tokens: 0, cost: 0, latency_ms: Date.now() - start, status: 'error' });
      reject(e);
    });
    req.on('timeout', () => {
      _logFinOps({ provider: providerName, model, capability, input_tokens: 0, output_tokens: 0, cost: 0, latency_ms: Date.now() - start, status: 'timeout' });
      req.destroy(); reject(new Error(`Timeout: ${providerName}`));
    });
    req.write(body);
    req.end();
  });
}

async function chatCompletionWithFallback({ capability, messages, stream = false }) {
  const primary = resolveForCapability(capability);
  try {
    return await chatCompletion({ ...primary, messages, stream, capability });
  } catch (e) {
    const fallback = resolveForCapability('default');
    console.error(`⚠️ Provider ${primary.provider} falló (${e.message}), fallback a ${fallback.provider}/${fallback.model}`);
    return await chatCompletion({ ...fallback, messages, stream, capability });
  }
}

function getFinOpsSummary() {
  try {
    if (!require('fs').existsSync(FINOPS_FILE)) return { total_calls: 0, total_cost: 0, by_capability: {}, by_model: {} };
    const lines = require('fs').readFileSync(FINOPS_FILE, 'utf-8').trim().split('\n').filter(Boolean);
    let totalCost = 0;
    const byCap = {}, byModel = {};
    for (const line of lines) {
      try {
        const e = JSON.parse(line);
        if (e.event === 'ai_call') {
          totalCost += e.cost || 0;
          const cap = e.capability || 'unknown';
          const mod = e.model || 'unknown';
          byCap[cap] = (byCap[cap] || 0) + (e.cost || 0);
          byModel[mod] = (byModel[mod] || 0) + (e.cost || 0);
        }
      } catch {}
    }
    return { total_calls: lines.filter(l => l.includes('ai_call')).length, total_cost: Math.round(totalCost * 1000000) / 1000000, by_capability: byCap, by_model: byModel };
  } catch { return { total_calls: 0, total_cost: 0, by_capability: {}, by_model: {} }; }
}

module.exports = {
  PROVIDERS,
  CAPABILITY_MODEL_MAP,
  getProvider,
  resolveForCapability,
  listModels,
  chatCompletion,
  chatCompletionWithFallback,
  getFinOpsSummary,
};
