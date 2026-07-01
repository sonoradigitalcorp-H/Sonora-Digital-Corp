const fs = require('fs');
const path = require('path');

const EVENTS_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'events.jsonl');
const SCORE_LOG = path.join(__dirname, '..', '..', 'state', 'logs', 'enterprise-score.log');

function _readEvents() {
  try {
    if (!fs.existsSync(EVENTS_FILE)) return [];
    return fs.readFileSync(EVENTS_FILE, 'utf-8').trim().split('\n').filter(Boolean).map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch { return []; }
}

function _readScoreHistory() {
  try {
    if (!fs.existsSync(SCORE_LOG)) return [];
    const lines = fs.readFileSync(SCORE_LOG, 'utf-8').split('\n').filter(Boolean);
    return lines.filter(l => l.includes('Enterprise Score:')).map(l => {
      try {
        const ts = l.substring(1, 20);
        const score = parseInt(l.split(':').pop().trim().split('/')[0]);
        return { timestamp: ts, score };
      } catch { return null; }
    }).filter(Boolean).slice(-100);
  } catch { return []; }
}

function _calcScore() {
  const events = _readEvents();
  const finopsCalls = events.filter(e => e.event === 'ai_call');

  const count = (etype) => events.filter(e => e.event === etype).length;

  const revenue_score = Math.min(10, count('revenue_recorded')) || 1;
  const scalability_score = Math.min(10, count('deal_won') + 3);
  const reusability_score = Math.min(10, Math.floor(count('skill_execution') / 5));
  const automation_score = events.length > 0 ? Math.min(10, Math.round(count('skill_execution') / Math.max(1, events.length) * 10)) : 1;
  const knowledge_score = Math.min(10, count('knowledge_stored'));
  const reliability_score = 7;
  const founder_score = Math.min(10, count('service_recovered'));
  const simplicity_score = Math.max(0, 10 - Math.floor(new Set(events.map(e => e.event)).size / 10));
  const customer_score = Math.min(10, count('customer_onboarded')) || 1;

  const totalCost = finopsCalls.reduce((s, c) => s + (c.cost || 0), 0);
  const totalCalls = finopsCalls.length;
  const costPerCall = totalCost / Math.max(1, totalCalls);
  const finops_score = totalCalls > 0 ? Math.max(0, 10 - Math.round(costPerCall / 0.001)) : 1;

  const metrics = {
    'Revenue Impact': revenue_score,
    'Scalability': scalability_score,
    'Reusability': reusability_score,
    'Automation Impact': automation_score,
    'Knowledge Impact': knowledge_score,
    'Reliability': reliability_score,
    'Founder Independence': founder_score,
    'Operational Simplicity': simplicity_score,
    'Customer Value': customer_score,
    'FinOps Efficiency': finops_score,
  };

  const total = Object.values(metrics).reduce((s, v) => s + v, 0);
  return { total, metrics };
}

const tools = {
  enterprise_score: {
    description: 'Enterprise Score actual desde eventos reales (10 métricas, max 100)',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      const score = _calcScore();
      const history = _readScoreHistory();
      return { score: score.total, metrics: score.metrics, history: history.slice(-30) };
    },
  },

  enterprise_score_history: {
    description: 'Historial del Enterprise Score (últimos 100)',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      return { history: _readScoreHistory().slice(-100) };
    },
  },
};

module.exports = { tools };
