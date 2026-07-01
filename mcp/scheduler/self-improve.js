/**
 * Self-Improvement Loop — Auto-fix + Auto-optimize
 * Corre cada hora. Analiza logs, detecta problemas, aplica fixes.
 */

const fs = require('fs');
const path = require('path');

const LOG_DIR = path.join(__dirname, '..', '..', 'state', 'logs');
const EVENTS_FILE = path.join(LOG_DIR, 'events.jsonl');
const LEARN_FILE = path.join(__dirname, '..', '..', 'state', 'learning.json');

class SelfImprove {
  constructor() { this.fixes = []; }

  _readLogs(file) {
    try {
      if (!fs.existsSync(file)) return [];
      return fs.readFileSync(file, 'utf-8').trim().split('\n').filter(Boolean).slice(-100);
    } catch { return []; }
  }

  analyze() {
    this.fixes = [];
    const events = this._readLogs(EVENTS_FILE);
    const errors = events.filter(e => e.includes('error') || e.includes('fail') || e.includes('timeout'));
    
    // Detect rate limit issues
    const rateLimits = errors.filter(e => e.includes('rate_limit') || e.includes('429'));
    if (rateLimits.length > 3) {
      this.fixes.push({ type: 'rate_limit', severity: 'high', detail: `${rateLimits.length} rate limit errors. Sugerencia: aumentar ventana o reducir concurrencia.` });
    }

    // Detect gateway errors
    const gwErrors = errors.filter(e => e.includes('gateway') || e.includes('18989'));
    if (gwErrors.length > 0) {
      this.fixes.push({ type: 'gateway', severity: 'high', detail: `Gateway tuvo ${gwErrors.length} errores` });
    }

    // Detect auth failures
    const authErrors = errors.filter(e => e.includes('auth') || e.includes('401') || e.includes('token'));
    if (authErrors.length > 3) {
      this.fixes.push({ type: 'auth', severity: 'medium', detail: `${authErrors.length} auth failures. Posible token expirado.` });
    }

    // Check learning data
    try {
      if (fs.existsSync(LEARN_FILE)) {
        const learn = JSON.parse(fs.readFileSync(LEARN_FILE, 'utf-8'));
        const lowConfidence = Object.entries(learn.capability_scores || {})
          .filter(([_, s]) => s.attempts >= 5 && (s.successes / s.attempts) < 0.5);
        lowConfidence.forEach(([cap, s]) => {
          this.fixes.push({ type: 'low_confidence', severity: 'low', detail: `${cap}: solo ${Math.round(s.successes/s.attempts*100)}% éxito. Sugerencia: cambiar modelo o provider.` });
        });
      }
    } catch {}

    return {
      timestamp: new Date().toISOString(),
      total_events: events.length,
      errors_found: errors.length,
      fixes_proposed: this.fixes.length,
      fixes: this.fixes,
    };
  }

  getFixes() { return this.fixes; }
}

const improver = new SelfImprove();
module.exports = { SelfImprove, improver };
