const fs = require('fs');
const path = require('path');
const http = require('http');

const PROVIDERS_FILE = path.join(__dirname, '..', '..', 'config', 'providers.json');
const EVENTS_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'events.jsonl');
const FALLOPS_FILE = path.join(__dirname, '..', '..', 'state', 'finops.jsonl');

const BUILTIN_PROVIDERS = {
  'opencode-go': {
    base_url: 'https://opencode.ai/zen/go/v1',
    models: {
      'deepseek-v4-flash': { context: 32768, cost_per_1k_input: 0.0001, cost_per_1k_output: 0.0001 },
      'deepseek-v4-flash-free': { context: 8192, cost_per_1k_input: 0, cost_per_1k_output: 0 },
    },
    status: 'active',
  },
  'openrouter': {
    base_url: 'https://openrouter.ai/api/v1',
    models: {
      'opencode/deepseek-v4-flash-free': { context: 8192, cost_per_1k_input: 0, cost_per_1k_output: 0 },
      'openai/gpt-4o': { context: 128000, cost_per_1k_input: 0.0025, cost_per_1k_output: 0.01 },
      'anthropic/claude-3.5-sonnet': { context: 200000, cost_per_1k_input: 0.003, cost_per_1k_output: 0.015 },
      'google/gemini-2.5-flash': { context: 1000000, cost_per_1k_input: 0.00015, cost_per_1k_output: 0.0004 },
      'meta-llama/llama-3.3-70b': { context: 128000, cost_per_1k_input: 0.00059, cost_per_1k_output: 0.00079 },
    },
    status: 'active',
  },
};

const FALLBACK_CHAINS = {
  routing: ['qwen2.5:1.5b', 'deepseek-v4-flash-free'],
  classification: ['qwen2.5:1.5b', 'deepseek-v4-flash-free'],
  research: ['deepseek-r1:7b', 'google/gemini-2.5-flash', 'deepseek-v4-flash'],
  code: ['deepseek-r1:7b', 'deepseek-v4-flash', 'anthropic/claude-3.5-sonnet'],
  sales: ['llama3.2:3b', 'openai/gpt-4o', 'deepseek-v4-flash'],
  content: ['llama3.2:3b', 'openai/gpt-4o', 'google/gemini-2.5-flash'],
  analysis: ['deepseek-r1:7b', 'google/gemini-2.5-flash', 'deepseek-v4-flash'],
  embedding: ['nomic-embed-text', 'deepseek-v4-flash-free'],
  agent: ['deepseek-v4-flash', 'deepseek-r1:7b'],
  default: ['qwen2.5:1.5b', 'deepseek-v4-flash-free'],
};

class ProviderManager {
  constructor() {
    this.providers = { ...BUILTIN_PROVIDERS };
    this._load();
  }

  _load() {
    try {
      if (fs.existsSync(PROVIDERS_FILE)) {
        const data = JSON.parse(fs.readFileSync(PROVIDERS_FILE, 'utf-8'));
        if (data.providers) Object.assign(this.providers, data.providers);
        if (data.fallback_chains) Object.assign(FALLBACK_CHAINS, data.fallback_chains);
      }
    } catch {}
  }

  _save() {
    try {
      fs.writeFileSync(PROVIDERS_FILE, JSON.stringify({
        providers: this.providers,
        fallback_chains: FALLBACK_CHAINS,
      }, null, 2));
    } catch {}
  }

  list() {
    return Object.entries(this.providers).map(([name, p]) => ({
      name,
      status: p.status || 'active',
      models: Object.keys(p.models || {}).length,
      base_url: p.base_url,
      models_list: Object.entries(p.models || {}).map(([m, c]) => ({ model: m, ...c })),
    }));
  }

  add(name, config) {
    if (this.providers[name]) return { error: `Provider ${name} ya existe` };
    this.providers[name] = { ...config, status: 'active', added_at: new Date().toISOString() };
    this._save();
    return { success: true, provider: name };
  }

  remove(name) {
    if (BUILTIN_PROVIDERS[name]) return { error: `No se puede eliminar provider built-in: ${name}` };
    if (!this.providers[name]) return { error: `Provider ${name} no encontrado` };
    delete this.providers[name];
    this._save();
    return { success: true, provider: name };
  }

  test(name) {
    const p = this.providers[name];
    if (!p) return { error: `Provider ${name} no encontrado` };
    const models = Object.keys(p.models || {});
    return { provider: name, status: 'configured', models: models.length, first_model: models[0] || 'none' };
  }

  getFallbackChain(capability) {
    return FALLBACK_CHAINS[capability] || FALLBACK_CHAINS.default;
  }

  setFallbackChain(capability, chain) {
    FALLBACK_CHAINS[capability] = chain;
    this._save();
    return { capability, chain };
  }

  resolveModel(capability) {
    const chain = this.getFallbackChain(capability);
    for (const model of chain) {
      for (const [pName, p] of Object.entries(this.providers)) {
        if (p.models && p.models[model] && p.status === 'active') {
          return { provider: pName, model };
        }
      }
    }
    return { provider: 'opencode-go', model: 'deepseek-v4-flash-free' };
  }
}

const manager = new ProviderManager();
module.exports = { ProviderManager, manager };
