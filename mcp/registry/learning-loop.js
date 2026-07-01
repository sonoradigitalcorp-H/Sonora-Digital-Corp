const fs = require('fs');
const path = require('path');

const LEARN_FILE = path.join(__dirname, '..', '..', 'state', 'learning.json');
const EVENTS_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'events.jsonl');

class LearningLoop {
  constructor() {
    this.data = { calls: [], capability_scores: {} };
    this._load();
  }

  _load() {
    try {
      if (fs.existsSync(LEARN_FILE)) this.data = JSON.parse(fs.readFileSync(LEARN_FILE, 'utf-8'));
    } catch {}
  }

  _save() {
    try {
      fs.writeFileSync(LEARN_FILE, JSON.stringify(this.data, null, 2));
    } catch {}
  }

  record(tool, capability, success, duration) {
    this.data.calls.push({ tool, capability, success, duration, timestamp: Date.now() });
    if (this.data.calls.length > 10000) this.data.calls = this.data.calls.slice(-5000);
    if (capability) {
      if (!this.data.capability_scores[capability]) this.data.capability_scores[capability] = { attempts: 0, successes: 0, total_duration: 0 };
      this.data.capability_scores[capability].attempts++;
      if (success) this.data.capability_scores[capability].successes++;
      this.data.capability_scores[capability].total_duration += duration;
    }
    this._save();
  }

  getScore(capability) {
    const s = this.data.capability_scores[capability];
    if (!s || s.attempts < 3) return 0.5;
    return s.successes / s.attempts;
  }

  getStats() {
    const scores = {};
    for (const [cap, s] of Object.entries(this.data.capability_scores)) {
      scores[cap] = { confidence: Math.round((s.successes / Math.max(1, s.attempts)) * 100), attempts: s.attempts, avg_duration_ms: Math.round(s.total_duration / s.attempts) };
    }
    return { total_calls: this.data.calls.length, capabilities_tracked: Object.keys(scores).length, scores };
  }

  getRecommendation(task) {
    const all = Object.entries(this.data.capability_scores)
      .filter(([_, s]) => s.attempts >= 3)
      .sort((a, b) => (b[1].successes / b[1].attempts) - (a[1].successes / a[1].attempts));
    return all.length > 0 ? all[0][0] : null;
  }
}

const loop = new LearningLoop();
module.exports = { LearningLoop, loop };
