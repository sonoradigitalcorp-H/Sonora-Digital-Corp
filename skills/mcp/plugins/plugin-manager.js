const fs = require('fs');
const path = require('path');
const http = require('http');

const PLUGINS_DIR = path.join(__dirname, 'store');
const REGISTRY_FILE = path.join(__dirname, '..', '..', 'config', 'plugins.json');
const GATEWAY_HOST = '127.0.0.1';
const GATEWAY_PORT = 18989;

class PluginManager {
  constructor() {
    this.plugins = new Map();
    this._loadRegistry();
    this._scanLocal();
  }

  _loadRegistry() {
    try {
      if (fs.existsSync(REGISTRY_FILE)) {
        const data = JSON.parse(fs.readFileSync(REGISTRY_FILE, 'utf-8'));
        if (data.plugins) {
          for (const [name, p] of Object.entries(data.plugins)) {
            this.plugins.set(name, { ...p, name, source: 'registry' });
          }
        }
      }
    } catch {}
  }

  _saveRegistry() {
    try {
      const plugins = {};
      for (const [name, p] of this.plugins) {
        if (p.source === 'registry') plugins[name] = { version: p.version, description: p.description, tools: p.tools, capabilities: p.capabilities };
      }
      fs.mkdirSync(path.dirname(REGISTRY_FILE), { recursive: true });
      fs.writeFileSync(REGISTRY_FILE, JSON.stringify({ version: '1.0.0', plugins }, null, 2));
    } catch {}
  }

  _scanLocal() {
    if (!fs.existsSync(PLUGINS_DIR)) return;
    for (const dir of fs.readdirSync(PLUGINS_DIR)) {
      const pluginFile = path.join(PLUGINS_DIR, dir, 'plugin.json');
      if (fs.existsSync(pluginFile)) {
        try {
          const p = JSON.parse(fs.readFileSync(pluginFile, 'utf-8'));
          this.plugins.set(p.name, { ...p, name: p.name, source: 'local' });
        } catch {}
      }
    }
  }

  install(name, source) {
    if (this.plugins.has(name)) return { error: `Plugin ${name} ya instalado` };
    const plugin = { name, version: source.version || '1.0.0', description: source.description || '', tools: source.tools || [], capabilities: source.capabilities || [], source: 'registry' };
    this.plugins.set(name, plugin);
    this._saveRegistry();
    return { success: true, plugin: name, tools: plugin.tools.length, capabilities: plugin.capabilities.length };
  }

  remove(name) {
    if (!this.plugins.has(name)) return { error: `Plugin ${name} no encontrado` };
    this.plugins.delete(name);
    this._saveRegistry();
    return { success: true, plugin: name };
  }

  list() {
    return Array.from(this.plugins.values()).map(p => ({
      name: p.name, version: p.version, description: p.description?.substring(0, 100),
      tools: (p.tools || []).length, capabilities: (p.capabilities || []).length, source: p.source || 'registry',
    }));
  }

  get(name) { return this.plugins.get(name) || null; }

  search(query) {
    const q = query.toLowerCase();
    return Array.from(this.plugins.values()).filter(p =>
      p.name.toLowerCase().includes(q) || (p.description || '').toLowerCase().includes(q)
    ).map(p => ({ name: p.name, version: p.version, description: p.description?.substring(0, 100) }));
  }

  createScaffold(name) {
    const dir = path.join(PLUGINS_DIR, name);
    fs.mkdirSync(dir, { recursive: true });
    const plugin = {
      name, version: '1.0.0', description: 'Descripción del plugin',
      tools: [], capabilities: [], webhook: null,
    };
    fs.writeFileSync(path.join(dir, 'plugin.json'), JSON.stringify(plugin, null, 2));
    return { success: true, path: dir };
  }

  getDefaultPlugins() {
    return [
      { name: 'github-mcp', version: '1.0.0', description: 'GitHub API — PRs, issues, repos, code search', tools: ['github_pr_list', 'github_issue_create', 'github_repo_search'], capabilities: ['code-management'] },
      { name: 'browser-debug', version: '1.0.0', description: 'Chrome DevTools MCP — debug de browsers desde agents', tools: ['browser_debug', 'browser_screenshot'], capabilities: ['browser-automation'] },
      { name: 'deep-research', version: '1.0.0', description: 'Investigación profunda multi-fuente con síntesis', tools: ['research_deep', 'research_synthesize'], capabilities: ['strategic-intelligence'] },
      { name: 'content-pipeline', version: '1.0.0', description: 'Pipeline completo de contenido: generar, revisar, publicar', tools: ['content_generate', 'content_review', 'content_publish'], capabilities: ['content-production'] },
      { name: 'data-analyst', version: '1.0.0', description: 'Análisis de datos: SQL, grafos, vectores, reportes', tools: ['postgres_query', 'neo4j_query', 'qdrant_search'], capabilities: ['business-intelligence'] },
      { name: 'social-publisher', version: '1.0.0', description: 'Publicación automática en redes sociales', tools: ['social_post', 'social_schedule'], capabilities: ['content-production'] },
    ];
  }
}

const manager = new PluginManager();
module.exports = { PluginManager, manager };
