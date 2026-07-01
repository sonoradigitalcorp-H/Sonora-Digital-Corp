/**
 * Business Generator — Creates complete business systems in seconds
 * Agents · SaaS · Workflows · Automations · Skills · Designs
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ADK_DIR = path.join(__dirname, '..', 'adk', 'agents');
const WF_DIR = path.join(__dirname, '..', 'workflow', 'samples');
const EVENTS_FILE = path.join(__dirname, '..', '..', 'state', 'logs', 'events.jsonl');

function _emit(event, detail) {
  try {
    const entry = JSON.stringify({ event, producer: 'generator', timestamp: new Date().toISOString(), payload: detail }) + '\n';
    fs.appendFileSync(EVENTS_FILE, entry);
  } catch {}
}

function _capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

const BUSINESS_TEMPLATES = {
  music_label: {
    name: 'Sello Discográfico',
    agents: ['crm', 'revenue', 'marketing', 'analytics', 'scheduler'],
    workflows: ['weekly-report', 'content-pipeline'],
    features: ['artist management', 'revenue tracking', 'content generation', 'analytics'],
    icon: '🎵',
  },
  ecommerce: {
    name: 'E-commerce',
    agents: ['crm', 'marketing', 'analytics', 'scheduler'],
    workflows: ['lead-to-cash-real', 'content-pipeline'],
    features: ['product management', 'order tracking', 'customer CRM', 'marketing campaigns'],
    icon: '🛍️',
  },
  saas: {
    name: 'SaaS Platform',
    agents: ['crm', 'revenue', 'analytics', 'scheduler', 'support'],
    workflows: ['client-onboarding', 'weekly-report'],
    features: ['user management', 'billing', 'analytics', 'support tickets'],
    icon: '☁️',
  },
  agency: {
    name: 'Agencia Digital',
    agents: ['crm', 'marketing', 'analytics', 'scheduler', 'support'],
    workflows: ['lead-to-cash-real', 'content-pipeline', 'client-onboarding'],
    features: ['client CRM', 'project tracking', 'content pipeline', 'reporting'],
    icon: '🏢',
  },
  education: {
    name: 'Educación Online',
    agents: ['crm', 'marketing', 'analytics', 'scheduler'],
    workflows: ['client-onboarding', 'content-pipeline'],
    features: ['student management', 'course delivery', 'progress tracking', 'certificates'],
    icon: '📚',
  },
};

const tools = {
  // ── Generate Complete Business ──
  generate_business: {
    description: 'Crea un sistema de negocio completo: agents, workflows, dashboards, SaaS',
    inputSchema: { type: 'object', properties: {
      name: { type: 'string', description: 'Nombre del negocio' },
      type: { type: 'string', enum: Object.keys(BUSINESS_TEMPLATES), description: 'Tipo de negocio' },
      description: { type: 'string', description: 'Descripción del negocio' },
      tenant_id: { type: 'string', description: 'ID del tenant (opcional)' },
    }, required: ['name', 'type'] },
    handler: async (args) => {
      const tmpl = BUSINESS_TEMPLATES[args.type];
      if (!tmpl) return { error: 'Tipo de negocio no válido' };
      
      const slug = args.name.toLowerCase().replace(/[^a-z0-9]/g, '-');
      const tenant = args.tenant_id || slug;
      const results = { business: args.name, type: args.type, tenant, agents: [], workflows: [], files: [] };

      // 1. Create ADK agents
      for (const agentType of tmpl.agents) {
        const agentName = `${slug}-${agentType}-agent`;
        const capabilityMap = {
          crm: 'client-onboarding', revenue: 'financial-operations', marketing: 'content-production',
          analytics: 'business-intelligence', scheduler: 'agent-operations', support: 'support-operations',
        };
        const toolMap = {
          crm: `- sonora:intake_query\n  - sonora:intake_stats\n  - sonora:enterprise_score`,
          revenue: `- sonora:billing_plan\n  - sonora:billing_invoice\n  - sonora:finops_summary`,
          marketing: `- sonora:media_image\n  - sonora:media_album_cover\n  - sonora:content_generate`,
          analytics: `- sonora:enterprise_score\n  - sonora:enterprise_score_history\n  - sonora:learning_stats`,
          scheduler: `- sonora:scheduler_list\n  - sonora:scheduler_add\n  - sonora:alerts_check`,
          support: `- sonora:sessions_list\n  - sonora:incident_report\n  - sonora:health_all`,
        };
        
        const yaml = `name: ${agentName}
version: 1.0.0
description: "${agentType} agent for ${args.name}"
model: llama3.2:3b
provider: ollama
capability: ${capabilityMap[agentType] || 'general'}
maturity: 2-Assisted
tools:
  - sonora:capability_resolve
${toolMap[agentType] || '  - sonora:enterprise_score'}
policies:
  max_tokens_per_call: 4096
  timeout_seconds: 60
events:
  emits: []
  listens: []
lifecycle:
  spawn: on-demand
  max_idle: 30m
  max_concurrent: 3
`;
        const filePath = path.join(ADK_DIR, `${agentName}.yaml`);
        fs.writeFileSync(filePath, yaml);
        results.agents.push(agentName);
        results.files.push(filePath);
      }

      // 2. Create tenant config
      const tenantConfig = {
        name: args.name,
        type: args.type,
        tenant_id: tenant,
        agents: results.agents,
        features: tmpl.features,
        icon: tmpl.icon,
        created_at: new Date().toISOString(),
        status: 'active',
        design_system: 'arc',
        model: 'llama3.2:3b',
        provider: 'ollama',
      };
      
      const configPath = path.join(__dirname, '..', '..', 'config', `business-${slug}.json`);
      fs.writeFileSync(configPath, JSON.stringify(tenantConfig, null, 2));
      results.files.push(configPath);

      // 3. Generate system prompt
      const prompt = `# ${args.name} — System Configuration

**Type**: ${tmpl.name}
**Tenant**: ${tenant}
**Agents**: ${results.agents.join(', ')}
**Features**: ${tmpl.features.join(', ')}

## Architecture
- Gateway: MCP :18989
- Auth: JWT RS256
- Models: ${tmpl.agents.length}x llama3.2:3b (Ollama, local, 0$/call)
- Fallback: opencode-go

## Quick Start
\`\`\`bash
# List agents
curl -X POST https://sonoradigitalcorp.com/api/call \\
  -H "Authorization: Bearer <token>" \\
  -d '{"tool":"adk_list_agents","params":{}}'

# Run business tasks
curl -X POST https://sonoradigitalcorp.com/api/call \\
  -H "Authorization: Bearer <token>" \\
  -d '{"tool":"intake_text","params":{"text":"New ${args.type} task","source":"manual"}}'

# Check system health
curl https://sonoradigitalcorp.com/api/health
\`\`\`

## Dashboards
- https://sonoradigitalcorp.com/dashboard (System)
- https://sonoradigitalcorp.com/adk (Agents)
- https://sonoradigitalcorp.com/abe-services (Services)
- https://sonoradigitalcorp.com/cheatsheet (Reference)
`;
      const promptPath = path.join(__dirname, '..', '..', 'sonora-enterprise-os', 'prompts', 'prompts', 'BUSINESS', `${slug}-system.md`);
      fs.mkdirSync(path.dirname(promptPath), { recursive: true });
      fs.writeFileSync(promptPath, prompt);
      results.files.push(promptPath);

      _emit('business_generated', { name: args.name, type: args.type, tenant, agents: results.agents.length });

      return {
        status: 'created',
        business: args.name,
        type: tmpl.name,
        tenant,
        agents_created: results.agents,
        files_created: results.files.length,
        config_file: `config/business-${slug}.json`,
        prompt_file: `sonora-enterprise-os/prompts/prompts/BUSINESS/${slug}-system.md`,
        next_steps: [
          `sdc adk list — verifica los agents creados`,
          `sdc workflow list — usa los workflows existentes`,
          `curl https://sonoradigitalcorp.com/${slug} — dashboard (si aplica)`,
        ],
      };
    },
  },

  // ── Generate New Agent ──
  generate_agent: {
    description: 'Crea un nuevo agente ADK en segundos',
    inputSchema: { type: 'object', properties: {
      name: { type: 'string', description: 'Nombre del agente' },
      capability: { type: 'string', description: 'Capacidad principal' },
      model: { type: 'string', enum: ['llama3.2:3b', 'qwen3:4b', 'qwen3:1.7b', 'deepseek-r1:7b', 'deepseek-v4-flash'] },
      description: { type: 'string' },
      tools: { type: 'string', description: 'Tools extra (opcional)' },
    }, required: ['name', 'capability'] },
    handler: async (args) => {
      const yaml = `name: ${args.name}
version: 1.0.0
description: "${args.description || args.capability + ' agent'}"
model: ${args.model || 'llama3.2:3b'}
provider: ${(args.model || '').includes('deepseek') ? 'opencode-go' : 'ollama'}
capability: ${args.capability}
maturity: 2-Assisted
tools:
  - sonora:capability_resolve
  - sonora:enterprise_score
${args.tools || ''}
policies:
  max_tokens_per_call: 4096
  timeout_seconds: 60
events:
  emits: []
  listens: []
lifecycle:
  spawn: on-demand
  max_idle: 30m
  max_concurrent: 3
`;
      const filePath = path.join(ADK_DIR, `${args.name}.yaml`);
      fs.writeFileSync(filePath, yaml);
      _emit('agent_generated', { name: args.name, capability: args.capability });
      return {
        status: 'created',
        agent: args.name,
        capability: args.capability,
        model: args.model || 'llama3.2:3b',
        file: filePath,
        next_step: 'sdc adk list — verificar que el agente esté registrado',
      };
    },
  },

  // ─── List Business Types ──
  generate_business_types: {
    description: 'Lista los tipos de negocio disponibles para generar',
    inputSchema: { type: 'object', properties: {} },
    handler: async () => {
      return {
        types: Object.entries(BUSINESS_TEMPLATES).map(([id, t]) => ({
          id, name: t.name, icon: t.icon,
          agents: t.agents.length, workflows: t.workflows.length,
          features: t.features,
        })),
      };
    },
  },

  // ── Generate Complete SaaS ──
  generate_saas: {
    description: 'Genera un SaaS completo: dashboard + agents + billing',
    inputSchema: { type: 'object', properties: {
      name: { type: 'string' }, industry: { type: 'string' },
      features: { type: 'string' }, color: { type: 'string' },
    }, required: ['name', 'industry'] },
    handler: async (args) => {
      const slug = args.name.toLowerCase().replace(/[^a-z0-9]/g, '-');
      
      // Create dashboard HTML
      const html = `<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>${args.name} — SaaS</title>
<style>
:root{--bg:#0a0a12;--surface:rgba(255,255,255,.05);--border:rgba(255,255,255,.1);--text:#f0f0f0;--dim:rgba(255,255,255,.4);--accent:${args.color || '#7c5cfc'};--radius:16px;--font:'Inter',-apple-system,sans-serif}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:var(--font);background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased;padding:2rem}
.glass{background:var(--surface);backdrop-filter:blur(20px);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem;margin-bottom:1rem}
h1{font-size:1.5rem;margin-bottom:.5rem}
h1 span{color:var(--accent)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem}
.stat{padding:1rem}
.stat .label{font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;color:var(--dim)}
.stat .value{font-size:1.8rem;font-weight:700;color:var(--accent)}
</style>
</head>
<body>
<h1>🚀 <span>${args.name}</span></h1>
<p style="color:var(--dim);margin-bottom:2rem">${args.industry} · Powered by Native Agent OS · 179 tools</p>
<div class="grid">
  <div class="stat glass"><div class="label">Status</div><div class="value">Online</div></div>
  <div class="stat glass"><div class="label">Agents</div><div class="value">Active</div></div>
  <div class="stat glass"><div class="label">AI</div><div class="value">24/7</div></div>
</div>
<div class="glass">
  <h3 style="margin-bottom:.5rem">✨ Features</h3>
  <p style="color:var(--dim)">${args.features || 'Custom AI-powered platform'}</p>
</div>
<div class="glass">
  <h3 style="margin-bottom:.5rem">🔧 Tech</h3>
  <p style="color:var(--dim)">MCP Gateway · 179 tools · 12 agents · 7 workflows · 6 models · All local · 0$/call</p>
</div>
</body>
</html>`;
      
      const dashPath = path.join(__dirname, '..', 'gateway', `${slug}-saas.html`);
      fs.writeFileSync(dashPath, html);
      
      _emit('saas_generated', { name: args.name, industry: args.industry });
      
      return {
        status: 'created',
        name: args.name,
        industry: args.industry,
        dashboard_url: `/${slug}-saas`,
        file: dashPath,
        features: args.features || 'AI-powered',
      };
    },
  },
};

module.exports = { tools };
