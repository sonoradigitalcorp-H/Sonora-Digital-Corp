/**
 * ═══════════════════════════════════════════════════════════════
 * Sonora Skill Registry v1.0 — Unified Skill Marketplace
 * ═══════════════════════════════════════════════════════════════
 * Unifica 4 silos de skills en un solo registry MCP.
 * Skills como MCP resources: discoverables, instalables, versionables.
 *
 * Silo 1: Telegram (98 skills, JSON, platforms/telegram/skills/)
 * Silo 2: Enterprise OS (10 skills, .skill.md, sonora-enterprise-os/skills/)
 * Silo 3: opencode (9 skills, SKILL.md, .opencode/skills/)
 * Silo 4: Registry (11 entries, JSON, config/registry.json)
 * ═══════════════════════════════════════════════════════════════
 */

const fs = require('fs');
const path = require('path');

const SDC_DIR = path.join(__dirname, '..', '..');
const TELEGRAM_SKILLS_DIR = path.join(SDC_DIR, 'platforms', 'telegram', 'skills');
const ENTERPRISE_SKILLS_DIR = path.join(SDC_DIR, 'sonora-enterprise-os', 'skills');
const OPENCODE_SKILLS_DIR = path.join(SDC_DIR, '.opencode', 'skills');
const REGISTRY_FILE = path.join(SDC_DIR, 'config', 'registry.json');
const SKILLS_DB = path.join(SDC_DIR, 'state', 'skill-registry.json');

const CACHE_TTL = 30000;
let _cache = null;
let _cacheTime = 0;

class SkillRegistry {
  constructor() {
    this.skills = new Map();
  }

  loadAll() {
    const skills = [];

    // Silo 1: Telegram skills
    if (fs.existsSync(TELEGRAM_SKILLS_DIR)) {
      const files = fs.readdirSync(TELEGRAM_SKILLS_DIR).filter(f => f.endsWith('.json'));
      for (const file of files) {
        try {
          const content = JSON.parse(fs.readFileSync(path.join(TELEGRAM_SKILLS_DIR, file), 'utf-8'));
          skills.push({
            id: `telegram:${file.replace('.json', '')}`,
            name: content.name || file.replace('.json', ''),
            source: 'telegram',
            type: content.method === 'STATIC' ? 'static' : 'api',
            description: content.description || '',
            triggers: content.triggers || [],
            priority: content.priority !== undefined ? content.priority : 5,
            version: content.version || '1.0.0',
            category: this._categorizeTelegram(content.name || file),
            endpoint: content.endpoint || null,
            method: content.method || 'STATIC',
          });
        } catch (e) { /* skip invalid */ }
      }
    }

    // Silo 2: Enterprise OS skills
    if (fs.existsSync(ENTERPRISE_SKILLS_DIR)) {
      const files = fs.readdirSync(ENTERPRISE_SKILLS_DIR).filter(f => f.endsWith('.skill.md'));
      for (const file of files) {
        try {
          const content = fs.readFileSync(path.join(ENTERPRISE_SKILLS_DIR, file), 'utf-8');
          const name = file.replace('.skill.md', '');
          const descMatch = content.match(/Business Objective[^]*?(?:\n##|\n$)/);
          const osMatch = content.match(/Parent OS[^]*?(?:\n##|\n$)/);
          skills.push({
            id: `enterprise:${name}`,
            name,
            source: 'enterprise',
            type: 'spec',
            description: descMatch ? descMatch[0].replace(/Business Objective\n/g, '').trim().slice(0, 200) : '',
            triggers: [],
            priority: 5,
            version: '1.0.0',
            category: osMatch ? osMatch[0].replace('Parent OS\n', '').trim() : 'enterprise',
            format: '.skill.md',
            path: `sonora-enterprise-os/skills/${file}`,
          });
        } catch (e) { /* skip */ }
      }
    }

    // Silo 3: opencode skills
    if (fs.existsSync(OPENCODE_SKILLS_DIR)) {
      const dirs = fs.readdirSync(OPENCODE_SKILLS_DIR).filter(d => {
        return fs.statSync(path.join(OPENCODE_SKILLS_DIR, d)).isDirectory();
      });
      for (const dir of dirs) {
        try {
          const skillFile = path.join(OPENCODE_SKILLS_DIR, dir, 'SKILL.md');
          if (fs.existsSync(skillFile)) {
            const content = fs.readFileSync(skillFile, 'utf-8');
            const descMatch = content.match(/description:\s*["'](.+?)["']/);
            skills.push({
              id: `opencode:${dir}`,
              name: dir,
              source: 'opencode',
              type: 'skill',
              description: descMatch ? descMatch[1] : '',
              triggers: [],
              priority: 5,
              version: '1.0.0',
              category: 'opencode',
              path: `.opencode/skills/${dir}/SKILL.md`,
            });
          }
        } catch (e) { /* skip */ }
      }
    }

    // Silo 4: config/registry.json
    if (fs.existsSync(REGISTRY_FILE)) {
      try {
        const registry = JSON.parse(fs.readFileSync(REGISTRY_FILE, 'utf-8'));
        for (const [name, def] of Object.entries(registry.skills || {})) {
          skills.push({
            id: `registry:${name}`,
            name,
            source: 'registry',
            type: def.mcp_server ? 'mcp' : 'core',
            description: def.description || '',
            triggers: def.command ? [def.command] : [],
            priority: 5,
            version: registry.version || '1.0.0',
            category: def.category || 'core',
            mcp_server: def.mcp_server || null,
            command: def.command || null,
          });
        }
      } catch (e) { /* skip */ }
    }

    // Build index
    for (const s of skills) {
      this.skills.set(s.id, s);
    }

    // Persist to state
    try {
      fs.mkdirSync(path.dirname(SKILLS_DB), { recursive: true });
      fs.writeFileSync(SKILLS_DB, JSON.stringify(skills, null, 2));
    } catch (e) { /* skip */ }

    return skills;
  }

  _categorizeTelegram(name) {
    if (!name) return 'general';
    const prefixes = {
      'abe': 'music',
      'ceo': 'admin',
      'hermes': 'ai',
      'sat': 'fiscal',
      'cfdi': 'fiscal',
      'resico': 'fiscal',
      'nomina': 'payroll',
      'brain': 'ai',
      'ayuda': 'help',
      'n8n': 'automation',
      'ventas': 'sales',
      'soporte': 'support',
      'musica': 'music',
      'mve': 'fiscal',
      'fiscal': 'fiscal',
    };
    for (const [prefix, cat] of Object.entries(prefixes)) {
      if (name.startsWith(prefix)) return cat;
    }
    return 'general';
  }

  list() {
    return Array.from(this.skills.values());
  }

  get(id) {
    return this.skills.get(id);
  }

  search(query) {
    const q = query.toLowerCase();
    const qWords = q.split(/\s+/).filter(Boolean);
    const results = [];
    for (const skill of this.skills.values()) {
      let score = 0;
      const fields = [
        { val: skill.name.toLowerCase(), weight: 10 },
        { val: skill.description.toLowerCase(), weight: 5 },
        { val: (skill.category || '').toLowerCase(), weight: 3 },
        ...(skill.triggers || []).map(t => ({ val: t.toLowerCase(), weight: 2 })),
      ];
      for (const word of qWords) {
        for (const f of fields) {
          if (f.val.includes(word)) score += f.weight;
        }
      }
      if (qWords.every(w => fields.some(f => f.val.includes(w)))) score += 5;
      if (score > 0) results.push({ ...skill, score });
    }
    results.sort((a, b) => b.score - a.score);
    return results.slice(0, 50);
  }

  getByCategory(category) {
    return Array.from(this.skills.values()).filter(s =>
      s.category && s.category.toLowerCase() === category.toLowerCase()
    );
  }

  getStats() {
    const bySource = {};
    const byCategory = {};
    for (const s of this.skills.values()) {
      bySource[s.source] = (bySource[s.source] || 0) + 1;
      byCategory[s.category || 'other'] = (byCategory[s.category || 'other'] || 0) + 1;
    }
    return {
      total: this.skills.size,
      bySource,
      byCategory,
    };
  }
}

const registry = new SkillRegistry();
registry.loadAll();

module.exports = { SkillRegistry, registry };
