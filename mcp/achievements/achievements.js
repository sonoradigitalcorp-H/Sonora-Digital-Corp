/**
 * Achievements System — Track milestones, award XP, record in Engram
 */

const fs = require('fs');
const path = require('path');

const ACH_FILE = path.join(__dirname, '..', '..', 'state', 'achievements.json');

const ALL_ACHIEVEMENTS = {
  first_tool_call: { name: 'Primera Llamada', desc: 'Ejecutaste tu primer tool MCP', xp: 10, icon: '🔧' },
  ten_tools: { name: 'Tool Explorer', desc: 'Usaste 10 tools diferentes', xp: 50, icon: '🔧' },
  fifty_tools: { name: 'Power User', desc: 'Usaste 50 tools diferentes', xp: 200, icon: '⚡' },
  first_agent: { name: 'Agent Creator', desc: 'Creaste un agente ADK', xp: 100, icon: '🧠' },
  first_workflow: { name: 'Workflow Runner', desc: 'Ejecutaste un workflow', xp: 150, icon: '⚡' },
  first_swarm: { name: 'Swarm Lord', desc: 'Coordinaste un swarm de agentes', xp: 200, icon: '🐝' },
  first_plugin: { name: 'Plugin Master', desc: 'Instalaste un plugin', xp: 100, icon: '🧩' },
  security_audit: { name: 'Security First', desc: 'Ejecutaste auditoría de seguridad', xp: 100, icon: '🔐' },
  soul_audit: { name: 'Soul Seeker', desc: 'Ejecutaste auditoría del alma', xp: 100, icon: '💜' },
  perfect_score: { name: 'Enterprise Champ', desc: 'Score ≥ 80', xp: 300, icon: '🏆' },
  chaos_tested: { name: 'Chaos Engineer', desc: 'Ejecutaste Chaos Monkey', xp: 250, icon: '🐒' },
  first_automation: { name: 'Set & Forget', desc: 'Creaste una automatización programada', xp: 150, icon: '⏰' },
  all_agents: { name: 'Agent Fleet', desc: 'Los 6 agentes ADK registrados', xp: 500, icon: '🚀' },
  gateway_master: { name: 'Gateway Master', desc: 'El sistema completo funcionando 24/7', xp: 1000, icon: '👑' },
};

class Achievements {
  constructor() {
    this.data = { unlocked: {}, xp: 0, calls: {} };
    this._load();
  }

  _load() {
    try {
      if (fs.existsSync(ACH_FILE)) this.data = JSON.parse(fs.readFileSync(ACH_FILE, 'utf-8'));
    } catch {}
  }

  _save() {
    try { fs.writeFileSync(ACH_FILE, JSON.stringify(this.data, null, 2)); } catch {}
  }

  _emit(tool, success) {
    const cat = tool.split('_')[0] || 'other';
    this.data.calls[tool] = (this.data.calls[tool] || 0) + 1;
    this.data.calls['_total'] = (this.data.calls._total || 0) + 1;
    this.data.calls['_category_' + cat] = (this.data.calls['_category_' + cat] || 0) + 1;
    this._save();
    this._check();
  }

  _check() {
    const totalCalls = this.data.calls._total || 0;
    const uniqueTools = Object.keys(this.data.calls).filter(k => !k.startsWith('_')).length;
    const categories = Object.keys(this.data.calls).filter(k => k.startsWith('_category_')).length;

    this._unlockIf('first_tool_call', totalCalls >= 1);
    this._unlockIf('ten_tools', uniqueTools >= 10);
    this._unlockIf('fifty_tools', uniqueTools >= 50);
    this._unlockIf('gateway_master', totalCalls >= 100);
    this._save();
  }

  _unlockIf(id, condition) {
    if (condition && !this.data.unlocked[id] && ALL_ACHIEVEMENTS[id]) {
      this.data.unlocked[id] = { unlocked_at: new Date().toISOString(), ...ALL_ACHIEVEMENTS[id] };
      this.data.xp += ALL_ACHIEVEMENTS[id].xp;
    }
  }

  unlock(id) {
    this._unlockIf(id, true);
    this._save();
    return this.data.unlocked[id] || null;
  }

  getStats() {
    return {
      xp: this.data.xp,
      unlocked_count: Object.keys(this.data.unlocked).length,
      total_achievements: Object.keys(ALL_ACHIEVEMENTS).length,
      total_calls: this.data.calls._total || 0,
      unique_tools: Object.keys(this.data.calls).filter(k => !k.startsWith('_')).length,
      recent: Object.values(this.data.unlocked).slice(-5),
    };
  }

  listAll() {
    return Object.entries(ALL_ACHIEVEMENTS).map(([id, ach]) => ({
      id, ...ach, unlocked: !!this.data.unlocked[id],
      unlocked_at: this.data.unlocked[id]?.unlocked_at || null,
    }));
  }
}

const achievements = new Achievements();
module.exports = { Achievements, achievements, ALL_ACHIEVEMENTS };
