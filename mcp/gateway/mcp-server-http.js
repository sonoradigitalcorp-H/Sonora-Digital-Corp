#!/usr/bin/env node
/**
 * ═══════════════════════════════════════════════════════════════
 * SONORA MCP HTTP Server — Gateway con soporte HTTP + Stdio
 * ═══════════════════════════════════════════════════════════════
 * Corre como servidor HTTP en :18989 para que MCP clients
 * puedan conectarse via HTTP en lugar de stdio.
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

const MCP_PORT = 18989;
const N8N_HOST = '127.0.0.1';
const N8N_PORT = 5678;
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

// Tool handlers
const TOOL_HANDLERS = {
  health_all: async () => {
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

  paperclip_status: async () => {
    return await httpGet('127.0.0.1', 3100, '/api/health');
  },

  n8n_workflows: async () => {
    return await httpGet(N8N_HOST, N8N_PORT, '/rest/workflows');
  },

  uptime_monitors: async () => {
    return await httpGet('127.0.0.1', 3003, '/api/status');
  },

  // === NEW N8N TOOLS ===
  n8n_trigger_workflow: async ({ workflow_id, payload }) => {
    if (!workflow_id) return { error: 'workflow_id es requerido' };
    const body = payload || {};
    return await httpPost(N8N_HOST, N8N_PORT, `/webhook/${workflow_id}`, body);
  },

  n8n_get_workflows: async () => {
    return await httpGet(N8N_HOST, N8N_PORT, '/rest/workflows');
  },

  n8n_get_workflow_runs: async ({ workflow_id }) => {
    if (!workflow_id) return { error: 'workflow_id es requerido' };
    return await httpGet(N8N_HOST, N8N_PORT, `/rest/workflows/${workflow_id}/runs`);
  },

  // === DOCKER TOOLS ===
  docker_ps: async () => {
    return execCommand('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"');
  },

  docker_logs: async ({ container_name }) => {
    if (!container_name) return { error: 'container_name es requerido' };
    return execCommand(`docker logs --tail 50 ${container_name}`);
  },

  docker_restart: async ({ container_name }) => {
    if (!container_name) return { error: 'container_name es requerido' };
    return execCommand(`docker restart ${container_name}`);
  },

  // === GIT TOOLS ===
  git_status: async () => {
    const status = execCommand('git status');
    const log = execCommand('git log -1 --oneline');
    return { status: status.output, last_commit: log.output };
  },

  git_pull: async () => {
    return execCommand('cd /root/sonora-digital-corp && git pull --rebase origin main');
  },
};

// HTTP Server handling MCP requests via REST
const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Content-Type', 'application/json');
  
  if (req.method === 'OPTIONS') { res.end(); return; }

  const url = new URL(req.url, `http://${req.headers.host}`);
  const path = url.pathname;

  try {
    if (path === '/api/health' || path === '/healthz') {
      const services = await checkAllServices();
      res.end(JSON.stringify({ status: 'ok', services, timestamp: new Date().toISOString() }));
    
    } else if (path === '/api/tools') {
      res.end(JSON.stringify({
        tools: [
          { name: 'health_all', description: 'Estado de todos los servicios', params: {} },
          { name: 'health_service', description: 'Estado de un servicio específico', params: { service: { type: 'string', enum: Object.keys(SERVICES) } } },
          { name: 'service_info', description: 'Info detallada de un servicio', params: { service: { type: 'string', enum: Object.keys(SERVICES) } } },
          { name: 'paperclip_status', description: 'Estado de Paperclip', params: {} },
          { name: 'n8n_workflows', description: 'Lista workflows n8n', params: {} },
          { name: 'uptime_monitors', description: 'Lista monitores UptimeKuma', params: {} },
          // N8N Tools
          { name: 'n8n_trigger_workflow', description: 'Dispara un workflow de n8n por webhook', params: { workflow_id: { type: 'string' }, payload: { type: 'object' } } },
          { name: 'n8n_get_workflows', description: 'Lista workflows activos en n8n', params: {} },
          { name: 'n8n_get_workflow_runs', description: 'Últimos runs de un workflow', params: { workflow_id: { type: 'string' } } },
          // Docker Tools
          { name: 'docker_ps', description: 'Lista contenedores Docker', params: {} },
          { name: 'docker_logs', description: 'Últimas 50 líneas de logs de un contenedor', params: { container_name: { type: 'string' } } },
          { name: 'docker_restart', description: 'Reinicia un contenedor Docker', params: { container_name: { type: 'string' } } },
          // Git Tools
          { name: 'git_status', description: 'Estado de git repo', params: {} },
          { name: 'git_pull', description: 'Hace git pull origin main', params: {} },
        ]
      }));
    
    } else if (path === '/api/call' && req.method === 'POST') {
      let body = '';
      req.on('data', chunk => body += chunk);
      req.on('end', async () => {
        try {
          const { tool, params } = JSON.parse(body);
          const handler = TOOL_HANDLERS[tool];
          if (!handler) {
            res.statusCode = 404;
            res.end(JSON.stringify({ error: `Tool ${tool} no encontrada` }));
            return;
          }
          const result = await handler(params || {});
          res.end(JSON.stringify(result));
        } catch (e) {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: e.message }));
        }
      });
    
    } else if (path === '/api/services') {
      const services = await checkAllServices();
      res.end(JSON.stringify(Object.entries(SERVICES).map(([k, v]) => ({
        id: k, name: v.name, icon: v.icon, desc: v.desc, port: v.port,
        status: services[k] ? 'online' : 'offline',
        subdomain: `https://${k}.sonoradigitalcorp.com`,
        endpoint: `http://${v.host}:${v.port}`
      }))));
    
    } else if (path === '/api/status') {
      const services = await checkAllServices();
      res.end(JSON.stringify({
        ecosystem: 'Sonora Digital Corp',
        timestamp: new Date().toISOString(),
        services,
        summary: {
          total: Object.keys(SERVICES).length,
          online: Object.values(services).filter(Boolean).length,
          offline: Object.values(services).filter(v => !v).length
        }
      }));
    
    } else {
      res.statusCode = 404;
      res.end(JSON.stringify({ error: 'Not Found', paths: ['/api/health', '/api/tools', '/api/call', '/api/services', '/api/status'] }));
    }
  } catch (e) {
    res.statusCode = 500;
    res.end(JSON.stringify({ error: e.message }));
  }
});

server.listen(MCP_PORT, '127.0.0.1', () => {
  console.error(`🔮 Sonora MCP HTTP Server corriendo en puerto ${MCP_PORT}`);
  console.error(`📡 Servicios: ${Object.keys(SERVICES).join(', ')}`);
  console.error(`🌐 Endpoints:`);
  console.error(`   GET  /api/health   — Health check`);
  console.error(`   GET  /api/tools    — Lista de herramientas MCP`);
  console.error(`   POST /api/call     — Ejecutar herramienta`);
  console.error(`   GET  /api/services — Servicios del ecosistema`);
  console.error(`   GET  /api/status   — Estado completo`);
});
