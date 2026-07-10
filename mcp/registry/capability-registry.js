const fs = require('fs');
const path = require('path');
const http = require('http');

const REGISTRY_PATH = path.join(__dirname, '..', '..', 'capabilities', 'REGISTRY.md');
const QDRANT_HOST = '127.0.0.1';
const QDRANT_PORT = 6333;
const CACHE_TTL = 60000;

let _cache = null;
let _cacheTime = 0;

function parseRegistry() {
  if (_cache && Date.now() - _cacheTime < CACHE_TTL) return _cache;

  try {
    const content = fs.readFileSync(REGISTRY_PATH, 'utf-8');
    const capabilities = [];
    const lines = content.split('\n');
    let inTable = false;

    for (const line of lines) {
      if (line.includes('| Capability |')) { inTable = true; continue; }
      if (line.includes('| ---')) continue;
      if (inTable && line.startsWith('|') && line.endsWith('|')) {
        const parts = line.split('|').map(p => p.trim()).filter(Boolean);
        if (parts.length >= 3) {
          capabilities.push({
            capability: parts[0],
            maturity: parts[1],
            owner: parts[2],
            keywords: parts[0].toLowerCase().split(/[\s/]+/),
          });
        }
      }
      if (inTable && !line.startsWith('|')) inTable = false;
    }

    _cache = capabilities;
    _cacheTime = Date.now();
    return capabilities;
  } catch (e) {
    return _cache || [];
  }
}

function queryQdrant(collection, vector, limit = 5) {
  return new Promise((resolve) => {
    const body = JSON.stringify({
      vector,
      limit,
      with_payload: true,
      with_vector: false,
    });
    const req = http.request({
      hostname: QDRANT_HOST, port: QDRANT_PORT,
      path: `/collections/${collection}/points/search`,
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      timeout: 5000,
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch { resolve(null); }
      });
    });
    req.on('error', () => resolve(null));
    req.on('timeout', () => { req.destroy(); resolve(null); });
    req.write(body);
    req.end();
  });
}

function resolve(task) {
  const capabilities = parseRegistry();
  const taskLower = task.toLowerCase();
  const taskWords = taskLower.split(/\s+/);

  const scored = capabilities.map(c => {
    let score = 0;
    for (const kw of c.keywords) {
      if (taskLower.includes(kw)) score += 2;
      if (taskWords.some(w => w === kw)) score += 3;
    }
    const actionWords = ['create', 'generate', 'make', 'build', 'find', 'search', 'analyze', 'review', 'sell', 'qualify'];
    for (const aw of actionWords) {
      if (taskLower.includes(aw)) score += 0.5;
    }
    return { ...c, score: Math.min(score, 10) };
  });

  scored.sort((a, b) => b.score - a.score);
  const best = scored[0];

  if (!best || best.score < 1) {
    return { capability: 'research', agent: 'ResearchAgent', confidence: 0.3, fallback: true };
  }

  const confidence = Math.min(best.score / 10, 1.0);
  return {
    capability: best.capability,
    agent: mapToAgent(best.capability),
    confidence,
    maturity: best.maturity,
  };
}

function mapToAgent(capability) {
  const map = {
    'Lead Acquisition': 'SalesAgent',
    'Lead Qualification': 'SalesAgent',
    'Sales Execution': 'SalesAgent',
    'Client Onboarding': 'SupportAgent',
    'Product Deployment': 'DevOpsAgent',
    'Support Operations': 'SupportAgent',
    'Knowledge Management': 'KnowledgeAgent',
    'Content Production': 'ContentAgent',
    'Infrastructure Operations': 'OpsAgent',
    'Financial Operations': 'FinanceAgent',
    'Agent Operations': 'HermesAgent',
    'Customer Success': 'SalesAgent',
    'Strategic Intelligence': 'ResearchAgent',
    'Business Intelligence': 'ResearchAgent',
  };
  return map[capability] || 'ResearchAgent';
}

function getRegistered() {
  return parseRegistry().map(c => ({
    capability: c.capability,
    maturity: c.maturity,
    owner: c.owner,
    agent: mapToAgent(c.capability),
  }));
}

module.exports = { resolve, getRegistered, parseRegistry };
