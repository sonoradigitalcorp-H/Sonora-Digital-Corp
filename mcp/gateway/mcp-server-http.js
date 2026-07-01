#!/usr/bin/env node
/**
 * ═══════════════════════════════════════════════════════════════
 * SONORA MCP HTTP Server v2.0 — Gateway Unificado con Auth
 * ═══════════════════════════════════════════════════════════════
 * Entry point único del ecosistema SDC.
 * Autenticación JWT RS256, CapabilityRegistry, tools migradas.
 * ═══════════════════════════════════════════════════════════════
 */

const http = require('http');
const { execSync, exec } = require('child_process');
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ErrorCode,
  McpError
} = require('@modelcontextprotocol/sdk/types.js');

const { signToken, verifyToken, signRefreshToken } = require('../auth/jwt');
const { authMiddleware, requireScope } = require('../auth/middleware');
const capabilityRegistry = require('../registry/capability-registry');
const { tools: salesTools } = require('../tools/sales');
const { tools: scoreTools } = require('../tools/score');
const { tools: voiceTools } = require('../tools/voice');
const { runtime: adkRuntime } = require('../adk/adk');
const providerRouter = require('../providers/provider-router');
const { runner: dockerRunner } = require('../providers/docker-runner');
const { registry: skillRegistry } = require('../registry/skill-registry');
const { tools: sessionTools } = require('../tools/sessions');
const { tools: brainTools } = require('../tools/brain');
const { tools: contentTools } = require('../tools/content');
const { tools: storeTools } = require('../tools/store');
const { tools: webhookTools } = require('../tools/webhooks');
const { tools: commandsTools } = require('../tools/commands');
const { tools: sdcTools } = require('../tools/sdc');
const { tools: mysticverseTools } = require('../tools/mysticverse');
const { tools: paymentsTools } = require('../tools/payments');
const { tools: abeTools } = require('../tools/abe');
const { tools: zamoraTools } = require('../tools/zamora');
const { tools: approvalsTools } = require('../tools/approvals');
const { tools: filesTools } = require('../tools/files');
const { tools: skillsTools } = require('../tools/skills');
const { tools: appTools } = require('../tools/app');
const { engine: workflowEngine } = require('../workflow/engine');
const { manager: providerManager } = require('../providers/provider-manager');

const MCP_PORT = 18989;
const N8N_HOST = '127.0.0.1';
const N8N_PORT = 5678;

const TENANTS_PATH = require('path').join(__dirname, '..', '..', 'config', 'tenants.json');
const TENANTS = JSON.parse(require('fs').readFileSync(TENANTS_PATH, 'utf-8')).tenants;

const SERVICES = {
  paperclip: { name: 'Paperclip', port: 3100, host: '127.0.0.1', desc: 'Gestión de agentes IA', icon: '🧠', healthPath: '/api/health' },
  n8n:       { name: 'n8n', port: 5678, host: '127.0.0.1', desc: 'Automatización visual', icon: '⚡', healthPath: '/healthz' },
  metabase:  { name: 'Metabase', port: 3002, host: '127.0.0.1', desc: 'Dashboards SQL', icon: '📊', healthPath: '/api/health' },
  uptime:    { name: 'UptimeKuma', port: 3003, host: '127.0.0.1', desc: 'Monitor de estado', icon: '🔍', healthPath: '/' },
  dashy:     { name: 'Dashy', port: 3004, host: '127.0.0.1', desc: 'Homepage servicios', icon: '🚀', healthPath: '/' },
  plausible: { name: 'Plausible', port: 3006, host: '127.0.0.1', desc: 'Analytics web', icon: '📈', healthPath: '/' },
};

function httpGet(host, port, path) {
  return new Promise((resolve) => {
    const req = http.get({ hostname: host, port, path, timeout: 5000 }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, data }));
    });
    req.on('error', () => resolve({ status: 0, data: null }));
    req.on('timeout', () => { req.destroy(); resolve({ status: 0, data: null }); });
  });
}

function httpPost(host, port, path, body) {
  return new Promise((resolve) => {
    const data = JSON.stringify(body);
    const req = http.request({ hostname: host, port, path, method: 'POST', headers: { 'Content-Type': 'application/json', 'Content-Length': data.length }, timeout: 10000 }, (res) => {
      let result = '';
      res.on('data', chunk => result += chunk);
      res.on('end', () => resolve({ status: res.statusCode, data: result }));
    });
    req.on('error', () => resolve({ status: 0, data: null }));
    req.on('timeout', () => { req.destroy(); resolve({ status: 0, data: null }); });
    req.write(data);
    req.end();
  });
}

function execCommand(cmd) {
  try {
    const result = execSync(cmd, { encoding: 'utf-8', timeout: 10000 });
    return { success: true, output: result };
  } catch (e) {
    return { success: false, error: e.message, output: e.stdout || '' };
  }
}

async function checkAllServices() {
  const results = {};
  for (const [key, svc] of Object.entries(SERVICES)) {
    const r = await httpGet(svc.host, svc.port, svc.healthPath);
    results[key] = r.status >= 200 && r.status < 500;
  }
  return results;
}

function checkRateLimit(tenantId) {
  const config = TENANTS[tenantId] || { rate_limit: 10, period_seconds: 60 };
  return { allowed: true, limit: config.rate_limit, tenant: tenantId };
}

const SHARED_TOOL_HANDLERS = {
  health_all: async (args, auth) => {
    const services = await checkAllServices();
    return { services, summary: { total: Object.keys(SERVICES).length, online: Object.values(services).filter(Boolean).length } };
  },
  health_service: async ({ service }) => {
    const svc = SERVICES[service];
    if (!svc) return { error: `Servicio ${service} no encontrado` };
    const r = await httpGet(svc.host, svc.port, svc.healthPath);
    return { service, status: r.status >= 200 && r.status < 500 ? 'online' : 'offline', http_status: r.status };
  },
  service_info: async ({ service }) => {
    const svc = SERVICES[service];
    if (!svc) return { error: `Servicio ${service} no encontrado` };
    return { ...svc, status: 'configured' };
  },
  paperclip_status: async () => await httpGet('127.0.0.1', 3100, '/api/health'),
  n8n_workflows: async () => await httpGet(N8N_HOST, N8N_PORT, '/rest/workflows'),
  uptime_monitors: async () => await httpGet('127.0.0.1', 3003, '/api/status'),
  n8n_trigger_workflow: async ({ workflow_id, payload }) => {
    if (!workflow_id) return { error: 'workflow_id es requerido' };
    return await httpPost(N8N_HOST, N8N_PORT, `/webhook/${workflow_id}`, payload || {});
  },
  n8n_get_workflows: async () => await httpGet(N8N_HOST, N8N_PORT, '/rest/workflows'),
  n8n_get_workflow_runs: async ({ workflow_id }) => {
    if (!workflow_id) return { error: 'workflow_id es requerido' };
    return await httpGet(N8N_HOST, N8N_PORT, `/rest/workflows/${workflow_id}/runs`);
  },
  docker_ps: async () => execCommand('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'),
  docker_logs: async ({ container_name }) => {
    if (!container_name) return { error: 'container_name es requerido' };
    return execCommand(`docker logs --tail 50 ${container_name}`);
  },
  docker_restart: async ({ container_name }) => {
    if (!container_name) return { error: 'container_name es requerido' };
    return execCommand(`docker restart ${container_name}`);
  },
  git_status: async () => {
    const status = execCommand('git status');
    const log = execCommand('git log -1 --oneline');
    return { status: status.output, last_commit: log.output };
  },
  git_pull: async () => execCommand('cd /root/sonora-digital-corp && git pull --rebase origin main'),
};

const ADK_TOOL_HANDLERS = {
  adk_register_agent: async ({ name, definition }) => {
    try {
      const agent = adkRuntime.parse(definition);
      const validation = adkRuntime.validate(agent);
      if (!validation.valid) return { error: 'Validación falló', errors: validation.errors };
      const filePath = require('path').join(__dirname, '..', 'adk', 'agents', `${name}.yaml`);
      require('fs').writeFileSync(filePath, definition);
      adkRuntime.loadAll();
      return { success: true, agent: name, capability: agent.capability, model: agent.model };
    } catch (e) { return { error: e.message }; }
  },
  adk_list_agents: async () => {
    const agents = adkRuntime.list();
    return { agents: agents.map(a => ({
      name: a.name, capability: a.capability, model: a.model, provider: a.provider,
      tools: a.tools.length, lifecycle: a.lifecycle.spawn,
    })) };
  },
  adk_spawn_agent: async ({ name }) => {
    return await dockerRunner.spawn(name);
  },
  adk_kill_agent: async ({ name }) => {
    return await dockerRunner.kill(name);
  },
  adk_list_running: async () => {
    const running = await dockerRunner.list();
    return { agents: running };
  },
  adk_agent_logs: async ({ name, lines }) => {
    return await dockerRunner.logs(name, lines || 50);
  },
};

const PROVIDER_TOOL_HANDLERS = {
  provider_list: async () => {
    return { providers: Object.keys(providerRouter.PROVIDERS), models: providerRouter.listModels() };
  },
  provider_resolve: async ({ capability }) => {
    try {
      const resolved = providerRouter.resolveForCapability(capability);
      return { capability, ...resolved };
    } catch (e) { return { error: e.message }; }
  },
  skills_list: async () => {
    const skills = skillRegistry.list();
    return { skills: skills.map(s => ({
      id: s.id, name: s.name, source: s.source, type: s.type,
      category: s.category || 'general', description: s.description?.slice(0, 100) || '',
      version: s.version || '1.0.0',
    })) };
  },
  skills_search: async ({ query }) => {
    if (!query) return { error: 'query es requerido' };
    return { results: skillRegistry.search(query) };
  },
  skills_by_category: async ({ category }) => {
    if (!category) return { error: 'category es requerido' };
    return { category, skills: skillRegistry.getByCategory(category) };
  },
  skills_stats: async () => {
    return skillRegistry.getStats();
  },
  finops_summary: async () => {
    return providerRouter.getFinOpsSummary();
  },
  provider_test: async ({ provider, model, message }) => {
    try {
      const result = await providerRouter.chatCompletion({
        provider, model, messages: [{ role: 'user', content: message || 'test' }], timeout: 10000,
      });
      return { success: true, model: result.model, usage: result.usage };
    } catch (e) { return { error: e.message }; }
  },
};

const ALL_TOOL_HANDLERS = { ...SHARED_TOOL_HANDLERS, ...ADK_TOOL_HANDLERS, ...PROVIDER_TOOL_HANDLERS };

for (const [name, def] of Object.entries(salesTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(scoreTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(voiceTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(sessionTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(brainTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(contentTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(storeTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(webhookTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(commandsTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(sdcTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(mysticverseTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(paymentsTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(abeTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(zamoraTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(approvalsTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(filesTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(skillsTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}
for (const [name, def] of Object.entries(appTools)) {
  ALL_TOOL_HANDLERS[name] = def.handler;
}

// Workflow Engine tools
ALL_TOOL_HANDLERS['workflow_run'] = async ({ name, context }) => {
  const samples = workflowEngine.loadSamples();
  const sample = samples.find(s => s.name === name);
  if (!sample) return { error: `Workflow sample "${name}" no encontrado` };
  const def = workflowEngine.parse(sample.content);
  return await workflowEngine.run(def, context || {});
};
ALL_TOOL_HANDLERS['workflow_list'] = async () => {
  return { workflows: workflowEngine.list() };
};
ALL_TOOL_HANDLERS['workflow_list_samples'] = async () => {
  return { samples: workflowEngine.loadSamples().map(s => ({ name: s.name })) };
};
ALL_TOOL_HANDLERS['workflow_get'] = async ({ id }) => {
  const wf = workflowEngine.get(id);
  return wf || { error: 'Workflow no encontrado' };
};

// Provider Manager tools
ALL_TOOL_HANDLERS['provider_manager_list'] = async () => {
  return { providers: providerManager.list() };
};
ALL_TOOL_HANDLERS['provider_manager_add'] = async ({ name, config }) => {
  return providerManager.add(name, config);
};
ALL_TOOL_HANDLERS['provider_manager_remove'] = async ({ name }) => {
  return providerManager.remove(name);
};
ALL_TOOL_HANDLERS['provider_manager_test'] = async ({ name }) => {
  return providerManager.test(name);
};
ALL_TOOL_HANDLERS['provider_manager_fallback'] = async ({ capability, chain }) => {
  return providerManager.setFallbackChain(capability, chain);
};

function buildToolList() {
  const list = [
    { name: 'health_all', description: 'Estado de todos los servicios', inputSchema: { type: 'object', properties: {} } },
    { name: 'health_service', description: 'Estado de un servicio específico', inputSchema: { type: 'object', properties: { service: { type: 'string', enum: Object.keys(SERVICES) } }, required: ['service'] } },
    { name: 'service_info', description: 'Info detallada de un servicio', inputSchema: { type: 'object', properties: { service: { type: 'string', enum: Object.keys(SERVICES) } }, required: ['service'] } },
    { name: 'paperclip_status', description: 'Estado de Paperclip', inputSchema: { type: 'object', properties: {} } },
    { name: 'n8n_workflows', description: 'Lista workflows n8n', inputSchema: { type: 'object', properties: {} } },
    { name: 'uptime_monitors', description: 'Lista monitores UptimeKuma', inputSchema: { type: 'object', properties: {} } },
    { name: 'n8n_trigger_workflow', description: 'Dispara un workflow de n8n por webhook', inputSchema: { type: 'object', properties: { workflow_id: { type: 'string' }, payload: { type: 'object' } }, required: ['workflow_id'] } },
    { name: 'n8n_get_workflows', description: 'Lista workflows activos en n8n', inputSchema: { type: 'object', properties: {} } },
    { name: 'n8n_get_workflow_runs', description: 'Últimos runs de un workflow', inputSchema: { type: 'object', properties: { workflow_id: { type: 'string' } }, required: ['workflow_id'] } },
    { name: 'docker_ps', description: 'Lista contenedores Docker', inputSchema: { type: 'object', properties: {} } },
    { name: 'docker_logs', description: 'Últimas 50 líneas de logs de un contenedor', inputSchema: { type: 'object', properties: { container_name: { type: 'string' } }, required: ['container_name'] } },
    { name: 'docker_restart', description: 'Reinicia un contenedor Docker', inputSchema: { type: 'object', properties: { container_name: { type: 'string' } }, required: ['container_name'] } },
    { name: 'git_status', description: 'Estado de git repo', inputSchema: { type: 'object', properties: {} } },
    { name: 'git_pull', description: 'Hace git pull origin main', inputSchema: { type: 'object', properties: {} } },
    { name: 'capability_resolve', description: 'Resuelve qué capability/agente puede manejar un task', inputSchema: { type: 'object', properties: { task: { type: 'string', description: 'Descripción de la tarea' } }, required: ['task'] } },
    { name: 'capability_list', description: 'Lista todas las capabilities registradas en el sistema', inputSchema: { type: 'object', properties: {} } },
    { name: 'adk_register_agent', description: 'Registra un nuevo agente ADK desde definición YAML', inputSchema: { type: 'object', properties: { name: { type: 'string' }, definition: { type: 'string' } }, required: ['name', 'definition'] } },
    { name: 'adk_list_agents', description: 'Lista todos los agentes ADK registrados', inputSchema: { type: 'object', properties: {} } },
    { name: 'adk_spawn_agent', description: 'Spawns un agente ADK en contenedor Docker', inputSchema: { type: 'object', properties: { name: { type: 'string' } }, required: ['name'] } },
    { name: 'adk_kill_agent', description: 'Mata un agente ADK corriendo', inputSchema: { type: 'object', properties: { name: { type: 'string' } }, required: ['name'] } },
    { name: 'adk_list_running', description: 'Lista agentes ADK corriendo', inputSchema: { type: 'object', properties: {} } },
    { name: 'adk_agent_logs', description: 'Obtiene logs de un agente ADK', inputSchema: { type: 'object', properties: { name: { type: 'string' }, lines: { type: 'number' } }, required: ['name'] } },
    { name: 'provider_list', description: 'Lista todos los providers y modelos disponibles', inputSchema: { type: 'object', properties: {} } },
    { name: 'provider_resolve', description: 'Resuelve qué provider/model usar para una capability', inputSchema: { type: 'object', properties: { capability: { type: 'string' } }, required: ['capability'] } },
    { name: 'provider_test', description: 'Prueba un provider/model específico', inputSchema: { type: 'object', properties: { provider: { type: 'string' }, model: { type: 'string' }, message: { type: 'string' } }, required: ['provider'] } },
    { name: 'skills_list', description: 'Lista todas las skills del marketplace unificado', inputSchema: { type: 'object', properties: {} } },
    { name: 'skills_search', description: 'Busca skills por query', inputSchema: { type: 'object', properties: { query: { type: 'string' } }, required: ['query'] } },
    { name: 'skills_by_category', description: 'Skills filtradas por categoría', inputSchema: { type: 'object', properties: { category: { type: 'string' } }, required: ['category'] } },
    { name: 'skills_stats', description: 'Estadísticas del skill marketplace', inputSchema: { type: 'object', properties: {} } },
    { name: 'finops_summary', description: 'Resumen de costos FinOps por capability y modelo', inputSchema: { type: 'object', properties: {} } },
    { name: 'sessions_list', description: 'Lista sesiones del sistema', inputSchema: { type: 'object', properties: { pinned: { type: 'boolean' }, project: { type: 'string' }, tag: { type: 'string' }, limit: { type: 'number' } } } },
    { name: 'sessions_search', description: 'Busca sesiones por texto', inputSchema: { type: 'object', properties: { q: { type: 'string' } }, required: ['q'] } },
    { name: 'sessions_get', description: 'Obtiene sesión por ID', inputSchema: { type: 'object', properties: { session_id: { type: 'string' } }, required: ['session_id'] } },
    { name: 'sessions_create', description: 'Crea nueva sesión', inputSchema: { type: 'object', properties: { title: { type: 'string' }, project: { type: 'string' }, tags: { type: 'array', items: { type: 'string' } } } } },
    { name: 'sessions_delete', description: 'Elimina sesión', inputSchema: { type: 'object', properties: { session_id: { type: 'string' } }, required: ['session_id'] } },
    { name: 'brain_graph', description: 'Grafo del sistema (arquitectura + agentes)', inputSchema: { type: 'object', properties: {} } },
    { name: 'brain_activity', description: 'Actividad reciente de agentes', inputSchema: { type: 'object', properties: { limit: { type: 'number' } } } },
    { name: 'content_generate', description: 'Genera contenido desde plantilla', inputSchema: { type: 'object', properties: { template: { type: 'string' }, topic: { type: 'string' } }, required: ['template'] } },
    { name: 'content_deliver', description: 'Entrega contenido a canal', inputSchema: { type: 'object', properties: { channel: { type: 'string' }, content_id: { type: 'string' } }, required: ['channel'] } },
    { name: 'content_list', description: 'Lista contenido generado', inputSchema: { type: 'object', properties: {} } },
    { name: 'store_products', description: 'Lista productos de la tienda', inputSchema: { type: 'object', properties: {} } },
    { name: 'store_featured', description: 'Productos destacados', inputSchema: { type: 'object', properties: {} } },
    { name: 'store_create_order', description: 'Crea orden en tienda', inputSchema: { type: 'object', properties: { product_id: { type: 'string' } }, required: ['product_id'] } },
    { name: 'store_get_order', description: 'Detalle de orden', inputSchema: { type: 'object', properties: { order_id: { type: 'string' } }, required: ['order_id'] } },
    { name: 'webhook_backup', description: 'Trigger backup', inputSchema: { type: 'object', properties: {} } },
    { name: 'webhook_healthcheck', description: 'Trigger healthcheck', inputSchema: { type: 'object', properties: {} } },
    { name: 'webhook_incoming', description: 'Webhook de entrada n8n', inputSchema: { type: 'object', properties: { data: { type: 'object' } } } },
    { name: 'webhook_status', description: 'Estado webhooks', inputSchema: { type: 'object', properties: {} } },
    { name: 'commands_execute', description: 'Ejecuta comando del sistema', inputSchema: { type: 'object', properties: { command: { type: 'string' }, session_id: { type: 'string' } }, required: ['command'] } },
    { name: 'sdc_plans', description: 'Lista planes SDC', inputSchema: { type: 'object', properties: {} } },
    { name: 'sdc_plan', description: 'Detalle de plan', inputSchema: { type: 'object', properties: { plan_id: { type: 'string' }, nicho: { type: 'string' } }, required: ['plan_id'] } },
    { name: 'sdc_nicho', description: 'Perfil de nicho', inputSchema: { type: 'object', properties: { nicho: { type: 'string' } }, required: ['nicho'] } },
    { name: 'sdc_onboarding', description: 'Onboarding SDC', inputSchema: { type: 'object', properties: {} } },
    { name: 'sdc_onboarding_mystic', description: 'Onboarding Mystic', inputSchema: { type: 'object', properties: { message: { type: 'string' }, step: { type: 'number' } } } },
    { name: 'mysticverse_create_twin', description: 'Crea digital twin', inputSchema: { type: 'object', properties: {} } },
    { name: 'mysticverse_get_twin', description: 'Obtiene twin', inputSchema: { type: 'object', properties: { twin_id: { type: 'string' } }, required: ['twin_id'] } },
    { name: 'mysticverse_kyc_age', description: 'Verifica edad KYC', inputSchema: { type: 'object', properties: { creator_id: { type: 'string' } }, required: ['creator_id'] } },
    { name: 'mysticverse_kyc_status', description: 'Estado KYC', inputSchema: { type: 'object', properties: { creator_id: { type: 'string' } }, required: ['creator_id'] } },
    { name: 'mysticverse_gamification_xp', description: 'Añade XP', inputSchema: { type: 'object', properties: { player_id: { type: 'string' }, amount: { type: 'number' } }, required: ['player_id'] } },
    { name: 'mysticverse_gamification_player', description: 'Perfil jugador', inputSchema: { type: 'object', properties: { player_id: { type: 'string' } }, required: ['player_id'] } },
    { name: 'mysticverse_gamification_leaderboard', description: 'Leaderboard', inputSchema: { type: 'object', properties: { limit: { type: 'number' } } } },
    { name: 'payments_spei', description: 'Info SPEI', inputSchema: { type: 'object', properties: {} } },
    { name: 'payments_plans', description: 'Planes de pago', inputSchema: { type: 'object', properties: {} } },
    { name: 'payments_create', description: 'Crea pago', inputSchema: { type: 'object', properties: { plan: { type: 'string' }, provider: { type: 'string' } } } },
    { name: 'payments_transaction', description: 'Obtiene transacción', inputSchema: { type: 'object', properties: { tx_id: { type: 'string' } }, required: ['tx_id'] } },
    { name: 'abe_create_artist', description: 'Crea artista ABE', inputSchema: { type: 'object', properties: {} } },
    { name: 'abe_list_artists', description: 'Lista artistas', inputSchema: { type: 'object', properties: { status: { type: 'string' } } } },
    { name: 'abe_get_artist', description: 'Obtiene artista', inputSchema: { type: 'object', properties: { artist_id: { type: 'string' } }, required: ['artist_id'] } },
    { name: 'abe_ceo_dashboard', description: 'Dashboard CEO ABE', inputSchema: { type: 'object', properties: {} } },
    { name: 'zamora_services', description: 'Servicios Zamora', inputSchema: { type: 'object', properties: {} } },
    { name: 'zamora_pricing', description: 'Precios Zamora', inputSchema: { type: 'object', properties: {} } },
    { name: 'zamora_portfolio', description: 'Portfolio Zamora', inputSchema: { type: 'object', properties: {} } },
    { name: 'approvals_list', description: 'Aprobaciones pendientes', inputSchema: { type: 'object', properties: {} } },
    { name: 'approvals_approve', description: 'Aprueba ticket', inputSchema: { type: 'object', properties: { ticket: { type: 'string' } }, required: ['ticket'] } },
    { name: 'approvals_reject', description: 'Rechaza ticket', inputSchema: { type: 'object', properties: { ticket: { type: 'string' } }, required: ['ticket'] } },
    { name: 'files_list', description: 'Lista archivos del proyecto', inputSchema: { type: 'object', properties: { path: { type: 'string' } } } },
    { name: 'files_git_status', description: 'Estado git', inputSchema: { type: 'object', properties: {} } },
    { name: 'skills_system', description: 'Skills del sistema', inputSchema: { type: 'object', properties: {} } },
    { name: 'app_register', description: 'Registra usuario', inputSchema: { type: 'object', properties: { nombre: { type: 'string' }, email: { type: 'string' }, nicho: { type: 'string' } }, required: ['nombre', 'email', 'nicho'] } },
    { name: 'app_login', description: 'Login de usuario', inputSchema: { type: 'object', properties: { email: { type: 'string' }, password: { type: 'string' } }, required: ['email', 'password'] } },
    { name: 'app_dashboard', description: 'Dashboard de usuario', inputSchema: { type: 'object', properties: { user_id: { type: 'string' } }, required: ['user_id'] } },
    { name: 'app_execute', description: 'Ejecuta acción para usuario', inputSchema: { type: 'object', properties: { user_id: { type: 'string' }, type: { type: 'string' }, name: { type: 'string' } }, required: ['user_id', 'type', 'name'] } },
    { name: 'workflow_run', description: 'Ejecuta un workflow multi-agente', inputSchema: { type: 'object', properties: { name: { type: 'string' }, context: { type: 'object' } }, required: ['name'] } },
    { name: 'workflow_list', description: 'Lista ejecuciones de workflow', inputSchema: { type: 'object', properties: {} } },
    { name: 'workflow_list_samples', description: 'Lista samples de workflow disponibles', inputSchema: { type: 'object', properties: {} } },
    { name: 'workflow_get', description: 'Obtiene detalle de un workflow', inputSchema: { type: 'object', properties: { id: { type: 'string' } }, required: ['id'] } },
    { name: 'provider_manager_list', description: 'Lista providers configurados', inputSchema: { type: 'object', properties: {} } },
    { name: 'provider_manager_add', description: 'Añade un nuevo provider', inputSchema: { type: 'object', properties: { name: { type: 'string' }, config: { type: 'object' } }, required: ['name'] } },
    { name: 'provider_manager_remove', description: 'Elimina un provider', inputSchema: { type: 'object', properties: { name: { type: 'string' } }, required: ['name'] } },
    { name: 'provider_manager_test', description: 'Prueba un provider', inputSchema: { type: 'object', properties: { name: { type: 'string' } }, required: ['name'] } },
    { name: 'provider_manager_fallback', description: 'Configura cadena de fallback por capability', inputSchema: { type: 'object', properties: { capability: { type: 'string' }, chain: { type: 'array', items: { type: 'string' } } }, required: ['capability'] } },
  ];

  for (const [name, def] of Object.entries(salesTools)) {
    list.push({ name, description: def.description, inputSchema: def.inputSchema });
  }
  for (const [name, def] of Object.entries(scoreTools)) {
    list.push({ name, description: def.description, inputSchema: def.inputSchema });
  }
  for (const [name, def] of Object.entries(voiceTools)) {
    list.push({ name, description: def.description, inputSchema: def.inputSchema });
  }

  return list;
}

function parseBody(req) {
  return new Promise((resolve) => {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try { resolve(JSON.parse(body)); }
      catch { resolve({}); }
    });
  });
}

function sendJson(res, data, status = 200) {
  res.statusCode = status;
  res.end(JSON.stringify(data));
}

function authHandler(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const path = url.pathname;

  if (path === '/api/auth/token' && req.method === 'POST') {
    parseBody(req).then(async (body) => {
      const { client_id, client_secret } = body;
      if (!client_id || !client_secret) {
        return sendJson(res, { error: 'client_id y client_secret requeridos' }, 401);
      }
      const tenant = TENANTS[client_id];
      if (!tenant) return sendJson(res, { error: 'client_id inválido' }, 401);

      const secretsPath = require('path').join(__dirname, '..', '..', 'config', '.secrets', 'clients.json');
      let validSecret = false;
      try {
        const secrets = JSON.parse(require('fs').readFileSync(secretsPath, 'utf-8'));
        validSecret = secrets[client_id] === client_secret;
      } catch { validSecret = false; }

      if (!validSecret) return sendJson(res, { error: 'client_secret inválido' }, 401);

      const scopeMap = {
        'sdc-core': 'admin',
        'abe-fenix': 'sales:read sales:write score:read voice:write',
        'free': 'score:read',
      };

      const token = signToken({ sub: client_id, tenant: client_id, scope: scopeMap[client_id] || 'score:read' });
      const refresh = signRefreshToken({ sub: client_id, type: 'refresh' });

      sendJson(res, {
        access_token: token,
        refresh_token: refresh,
        expires_in: 3600,
        token_type: 'Bearer',
        scope: scopeMap[client_id] || 'score:read',
        tenant: client_id,
      });
    });
    return true;
  }
  return false;
}

function getReqAuth(req) {
  return req.auth || { tenant: 'anonymous', scope: '' };
}

const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Tenant-ID');
  res.setHeader('Content-Type', 'application/json');

  if (req.method === 'OPTIONS') { res.end(); return; }

  const url = new URL(req.url, `http://${req.headers.host}`);
  const path = url.pathname;

  if (authHandler(req, res)) return;

  authMiddleware(req, res, () => {
    handleRequest(req, res, path);
  });
});

async function handleRequest(req, res, path) {
  try {
    if (path === '/api/health' || path === '/healthz') {
      const services = await checkAllServices();
      sendJson(res, { status: 'ok', services, timestamp: new Date().toISOString() });

    } else if (path === '/api/tools') {
      sendJson(res, { tools: buildToolList() });

    } else if (path === '/api/call' && req.method === 'POST') {
      const body = await parseBody(req);
      const { tool, params } = body;
      const handler = ALL_TOOL_HANDLERS[tool];
      if (!handler) {
        return sendJson(res, { error: `Tool ${tool} no encontrada` }, 404);
      }
      const auth = getReqAuth(req);
      const rl = checkRateLimit(auth.tenant);
      if (!rl.allowed) {
        return sendJson(res, { error: 'Rate limit excedido', limit: rl.limit, tenant: rl.tenant }, 429);
      }
      const result = await handler(params || {}, auth);
      sendJson(res, result);

    } else if (path === '/api/services') {
      const services = await checkAllServices();
      sendJson(res, Object.entries(SERVICES).map(([k, v]) => ({
        id: k, name: v.name, icon: v.icon, desc: v.desc, port: v.port,
        status: services[k] ? 'online' : 'offline',
        subdomain: `https://${k}.sonoradigitalcorp.com`,
        endpoint: `http://${v.host}:${v.port}`
      })));

    } else if (path === '/api/status') {
      const services = await checkAllServices();
      const auth = getReqAuth(req);
      sendJson(res, {
        ecosystem: 'Sonora Digital Corp — Native Agent OS',
        version: '2.0.0',
        timestamp: new Date().toISOString(),
        tenant: auth.tenant,
        services,
        summary: {
          total: Object.keys(SERVICES).length,
          online: Object.values(services).filter(Boolean).length,
          offline: Object.values(services).filter(v => !v).length
        }
      });

    } else if (path === '/api/capability/resolve' && req.method === 'POST') {
      const body = await parseBody(req);
      const result = capabilityRegistry.resolve(body.task || '');
      sendJson(res, result);

    } else if (path === '/api/capability/list') {
      const list = capabilityRegistry.getRegistered();
      sendJson(res, { capabilities: list });

    } else if (path === '/dashboard' || path === '/api/dashboard') {
      const fs = require('fs');
      const dashPath = require('path').join(__dirname, 'dashboard.html');
      if (fs.existsSync(dashPath)) {
        res.setHeader('Content-Type', 'text/html; charset=utf-8');
        res.end(fs.readFileSync(dashPath, 'utf-8'));
      } else {
        sendJson(res, { error: 'Dashboard no encontrado' }, 404);
      }
    } else if (path === '/adk' || path === '/api/adk') {
      const fs = require('fs');
      const adkPath = require('path').join(__dirname, 'adk.html');
      if (fs.existsSync(adkPath)) {
        res.setHeader('Content-Type', 'text/html; charset=utf-8');
        res.end(fs.readFileSync(adkPath, 'utf-8'));
      } else {
        sendJson(res, { error: 'ADK Web no encontrado' }, 404);
      }
    } else {
      sendJson(res, { error: 'Not Found', paths: [
        '/api/health', '/api/tools', '/api/call', '/api/services', '/api/status',
        '/api/auth/token', '/api/capability/resolve', '/api/capability/list'
      ] }, 404);
    }
  } catch (e) {
    sendJson(res, { error: e.message }, 500);
  }
}

server.listen(MCP_PORT, '127.0.0.1', () => {
  console.error(`🔮 Sonora MCP HTTP Server v2.0 — Puerto ${MCP_PORT}`);
  console.error(`🔐 Auth: JWT RS256 (obtén token en POST /api/auth/token)`);
  console.error(`📋 CapabilityRegistry activo (${capabilityRegistry.getRegistered().length} capabilities)`);
  console.error(`📡 Servicios: ${Object.keys(SERVICES).join(', ')}`);
  console.error(`🌐 Endpoints:`);
  console.error(`   POST /api/auth/token         — Obtener token JWT`);
  console.error(`   GET  /api/health              — Health check`);
  console.error(`   GET  /api/tools               — Lista de herramientas MCP`);
  console.error(`   POST /api/call                — Ejecutar herramienta`);
  console.error(`   GET  /api/services            — Servicios del ecosistema`);
  console.error(`   GET  /api/status              — Estado completo`);
  console.error(`   POST /api/capability/resolve  — Resolver capability`);
  console.error(`   GET  /api/capability/list     — Lista capabilities`);
  console.error(`   GET  /dashboard               — Native Agent OS Dashboard`);
  console.error(`   GET  /api/dashboard            — Native Agent OS Dashboard`);
  console.error(`   GET  /adk                      — ADK Web — Agent Manager UI`);
});
