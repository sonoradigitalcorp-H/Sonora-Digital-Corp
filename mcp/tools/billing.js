const fs = require('fs');
const path = require('path');

const BILLING_FILE = path.join(__dirname, '..', '..', 'state', 'billing.json');
const FINOPS_FILE = path.join(__dirname, '..', '..', 'state', 'finops.jsonl');
const EVENTS_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'events.jsonl');

const PLANS = {
  'sdc-core': { name: 'Enterprise', price: 0, rate_limit: 1000, max_tokens: -1, features: ['all'] },
  'abe-fenix': { name: 'Pro', price: 499, rate_limit: 200, max_tokens: 500000, features: ['chat', 'agents', 'rag', 'music', 'booking'] },
  'free': { name: 'Free', price: 0, rate_limit: 10, max_tokens: 10000, features: ['chat'] },
};

function _init() {
  try {
    if (!fs.existsSync(BILLING_FILE)) {
      fs.writeFileSync(BILLING_FILE, JSON.stringify({ invoices: [], total_collected: 0 }, null, 2));
    }
  } catch {}
}

function getPlan(tenantId) {
  return PLANS[tenantId] || PLANS.free;
}

function getUsage(tenantId) {
  const plan = getPlan(tenantId);
  let calls = 0, tokens = 0, cost = 0;
  try {
    if (fs.existsSync(FINOPS_FILE)) {
      const lines = fs.readFileSync(FINOPS_FILE, 'utf-8').trim().split('\n').filter(Boolean);
      for (const line of lines) {
        try {
          const e = JSON.parse(line);
          if (e.event === 'ai_call') {
            calls++;
            tokens += e.total_tokens || 0;
            cost += e.cost || 0;
          }
        } catch {}
      }
    }
  } catch {}
  return { tenant: tenantId, plan: plan.name, calls, tokens, cost: Math.round(cost * 100) / 100, rate_limit: plan.rate_limit, max_tokens: plan.max_tokens };
}

function generateInvoice(tenantId) {
  _init();
  const usage = getUsage(tenantId);
  const plan = getPlan(tenantId);
  const invoice = {
    id: 'INV-' + Date.now().toString(36).toUpperCase(),
    tenant: tenantId,
    plan: plan.name,
    amount: plan.price,
    tokens_used: usage.tokens,
    calls_made: usage.calls,
    ai_cost: usage.cost,
    period: new Date().toISOString().slice(0, 7),
    issued_at: new Date().toISOString(),
    status: plan.price > 0 ? 'pending' : 'free',
  };

  try {
    const data = JSON.parse(fs.readFileSync(BILLING_FILE, 'utf-8'));
    data.invoices.push(invoice);
    if (plan.price === 0) data.total_collected += 0;
    fs.writeFileSync(BILLING_FILE, JSON.stringify(data, null, 2));
  } catch {}

  return invoice;
}

const tools = {
  billing_plan: {
    description: 'Obtiene plan y uso de un tenant',
    inputSchema: { type: 'object', properties: { tenant_id: { type: 'string' } }, required: ['tenant_id'] },
    handler: async (args) => getUsage(args.tenant_id || 'sdc-core'),
  },
  billing_invoice: {
    description: 'Genera factura para un tenant',
    inputSchema: { type: 'object', properties: { tenant_id: { type: 'string' } }, required: ['tenant_id'] },
    handler: async (args) => generateInvoice(args.tenant_id || 'sdc-core'),
  },
  billing_plans: {
    description: 'Lista planes disponibles',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      return Object.entries(PLANS).map(([id, p]) => ({ id, ...p }));
    },
  },
};

module.exports = { tools };
