/**
 * ═══════════════════════════════════════════════════════════════
 * Sonora ADK v1.0 — Agent Development Kit Runtime
 * ═══════════════════════════════════════════════════════════════
 * Lee definiciones YAML de agentes, las valida, y las registra
 * en el CapabilityRegistry y MCP Gateway.
 *
 * Un agente ADK es un archivo YAML con:
 *   name, version, description, model, provider, capability,
 *   tools, policies, events, lifecycle
 * ═══════════════════════════════════════════════════════════════
 */

const fs = require('fs');
const path = require('path');

const AGENTS_DIR = path.join(__dirname, 'agents');
const REGISTRY_FILE = path.join(__dirname, '..', '..', 'config', 'registry.json');

class ADKRuntime {
  constructor() {
    this.agents = new Map();
  }

  loadAll() {
    if (!fs.existsSync(AGENTS_DIR)) return [];
    const files = fs.readdirSync(AGENTS_DIR).filter(f => f.endsWith('.yaml') || f.endsWith('.yml'));
    const loaded = [];
    for (const file of files) {
      try {
        const agent = this.parseFile(path.join(AGENTS_DIR, file));
        this.agents.set(agent.name, agent);
        loaded.push(agent);
      } catch (e) {
        console.error(`❌ ADK: Error cargando ${file}: ${e.message}`);
      }
    }
    return loaded;
  }

  parseFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf-8');
    return this.parse(content);
  }

  parse(content) {
    const lines = content.split('\n');
    const agent = {
      name: '',
      version: '1.0.0',
      description: '',
      model: 'deepseek-v4-flash',
      provider: 'opencode-go',
      capability: '',
      maturity: '1-Manual',
      tools: [],
      policies: {},
      events: { emits: [], listens: [] },
      lifecycle: { spawn: 'on-demand', max_idle: '30m', max_concurrent: 1 },
      _raw: content,
    };

    let section = null;
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('#') || trimmed === '') continue;

      const sectionMatch = trimmed.match(/^(\w+):$/);
      if (sectionMatch) { section = sectionMatch[1]; continue; }

      const kvMatch = trimmed.match(/^(\w[\w_]*):\s*(.*)$/);
      if (kvMatch && !section) {
        const key = kvMatch[1];
        const val = kvMatch[2].replace(/^"|"$/g, '');
        if (key in agent && typeof agent[key] === 'string') {
          agent[key] = val;
        }
      }

      if (section === 'tools' && trimmed.startsWith('- ')) {
        agent.tools.push(trimmed.slice(2).trim());
      }
      if (section === 'policies' && trimmed.includes(':')) {
        const [k, ...v] = trimmed.split(':');
        agent.policies[k.trim()] = v.join(':').trim();
      }
      if (section === 'lifecycle' && trimmed.includes(':')) {
        const [k, ...v] = trimmed.split(':');
        agent.lifecycle[k.trim()] = v.join(':').trim();
      }
      if (section === 'events') {
        if (trimmed.startsWith('emits:') || trimmed.startsWith('listens:')) {
          section = `events_${trimmed.split(':')[0]}`;
        }
      }
      if (section?.startsWith('events_') && trimmed.startsWith('- ')) {
        const key = section.replace('events_', '');
        agent.events[key].push(trimmed.slice(2).trim());
      }
    }

    if (!agent.name) throw new Error('ADK: agent name es requerido');
    agent.keywords = agent.name.replace(/-/g, ' ').split(/\s+/);
    if (agent.capability) {
      const parts = agent.capability.replace(/-/g, ' ').split(/\s+/);
      agent.keywords = [...new Set([...agent.keywords, ...parts])];
    }

    return agent;
  }

  validate(agent) {
    const errors = [];
    if (!agent.name) errors.push('name es requerido');
    if (!agent.capability) errors.push('capability es requerido');
    if (!Array.isArray(agent.tools)) errors.push('tools debe ser un array');
    if (agent.lifecycle.max_concurrent && typeof agent.lifecycle.max_concurrent === 'string') {
      agent.lifecycle.max_concurrent = parseInt(agent.lifecycle.max_concurrent);
    }
    return { valid: errors.length === 0, errors };
  }

  get(name) {
    return this.agents.get(name);
  }

  list() {
    return Array.from(this.agents.values());
  }

  toRegistryEntries() {
    const entries = [];
    for (const agent of this.agents.values()) {
      entries.push({
        name: agent.name,
        capability: agent.capability,
        model: agent.model,
        provider: agent.provider,
        tools: agent.tools,
        maturity: agent.maturity,
        lifecycle: agent.lifecycle,
      });
    }
    return entries;
  }
}

const runtime = new ADKRuntime();
runtime.loadAll();

module.exports = { ADKRuntime, runtime };
