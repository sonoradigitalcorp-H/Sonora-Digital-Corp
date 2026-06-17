#!/usr/bin/env node
/**
 * ═══════════════════════════════════════════════════════════════
 * SONORA DIGITAL CORP — MCP Gateway Unificado v1.0
 * ═══════════════════════════════════════════════════════════════
 * Gateway MCP central que expone todos los servicios del
 * ecosistema como herramientas (tools) y recursos (resources)
 * accesibles via Model Context Protocol.
 *
 * Puertos de servicio:
 *   Paperclip  :3100   — Gestión de agentes
 *   n8n        :5678   — Automatización visual
 *   Metabase   :3002   — Dashboards SQL
 *   UptimeKuma :3003   — Monitor de estado
 *   Dashy      :3004   — Homepage servicios
 *   Plausible  :3006   — Analytics
 *   OpenClaw   :18789  — Gateway agentes
 *   PostgreSQL :5432   — Base de datos
 * ═══════════════════════════════════════════════════════════════
 */

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
const { z } = require('zod');
const http = require('http');
const https = require('https');

// ─── CONFIG ───────────────────────────────────────────────────────
const SERVICES = {
  paperclip: { name: 'Paperclip', port: 3100, host: '127.0.0.1', desc: 'Gestión de agentes IA', icon: '🧠' },
  n8n:       { name: 'n8n', port: 5678, host: '127.0.0.1', desc: 'Automatización visual de workflows', icon: '⚡' },
  metabase:  { name: 'Metabase', port: 3002, host: '127.0.0.1', desc: 'Dashboards SQL y métricas', icon: '📊' },
  uptime:    { name: 'UptimeKuma', port: 3003, host: '127.0.0.1', desc: 'Monitor de estado', icon: '🔍' },
  dashy:     { name: 'Dashy', port: 3004, host: '127.0.0.1', desc: 'Homepage de servicios', icon: '🚀' },
  plausible: { name: 'Plausible', port: 3006, host: '127.0.0.1', desc: 'Analytics web', icon: '📈' },
};

const MCP_VERSION = '1.0.0';
const SERVER_NAME = 'sonora-mcp-gateway';

// ─── UTILITIES ────────────────────────────────────────────────────

function httpRequest(service, path, method = 'GET', body = null) {
  return new Promise((resolve, reject) => {
    const cfg = SERVICES[service];
    if (!cfg) return reject(new Error(`Servicio desconocido: ${service}`));
    
    const opts = {
      hostname: cfg.host,
      port: cfg.port,
      path,
      method,
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      timeout: 10000
    };
    
    const req = http.request(opts, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, data: data ? JSON.parse(data) : null, raw: data });
        } catch {
          resolve({ status: res.statusCode, data: null, raw: data });
        }
      });
    });
    
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

function healthCheck(service) {
  return httpRequest(service, '/api/health')
    .then(r => r.status === 200)
    .catch(() => false);
}

// ─── MCP SERVER ──────────────────────────────────────────────────

const server = new Server(
  { name: SERVER_NAME, version: MCP_VERSION },
  { capabilities: { tools: {}, resources: {} } }
);

// ─── Lista de HERRAMIENTAS (Tools) ───────────────────────────────

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    // ── Sistema ──
    {
      name: 'health_all',
      description: 'Verifica el estado de TODOS los servicios del ecosistema',
      inputSchema: { type: 'object', properties: {} }
    },
    {
      name: 'health_service',
      description: 'Verifica el estado de un servicio específico',
      inputSchema: {
        type: 'object',
        properties: {
          service: { type: 'string', enum: Object.keys(SERVICES), description: 'Nombre del servicio' }
        },
        required: ['service']
      }
    },
    {
      name: 'service_info',
      description: 'Obtiene información detallada de un servicio',
      inputSchema: {
        type: 'object',
        properties: {
          service: { type: 'string', enum: Object.keys(SERVICES), description: 'Nombre del servicio' }
        },
        required: ['service']
      }
    },

    // ── Paperclip ──
    {
      name: 'paperclip_status',
      description: 'Obtiene el estado del dashboard Paperclip (gestión de agentes)',
      inputSchema: { type: 'object', properties: {} }
    },

    // ── n8n ──
    {
      name: 'n8n_workflows',
      description: 'Lista los workflows activos en n8n',
      inputSchema: { type: 'object', properties: {} }
    },
    {
      name: 'n8n_execute_workflow',
      description: 'Ejecuta un workflow de n8n por ID',
      inputSchema: {
        type: 'object',
        properties: {
          workflowId: { type: 'string', description: 'ID del workflow a ejecutar' }
        },
        required: ['workflowId']
      }
    },

    // ── Metabase ──
    {
      name: 'metabase_questions',
      description: 'Lista las preguntas (queries guardadas) en Metabase',
      inputSchema: { type: 'object', properties: {} }
    },
    {
      name: 'metabase_query',
      description: 'Ejecuta una pregunta de Metabase por ID',
      inputSchema: {
        type: 'object',
        properties: {
          questionId: { type: 'number', description: 'ID de la pregunta en Metabase' }
        },
        required: ['questionId']
      }
    },

    // ── Uptime Kuma ──
    {
      name: 'uptime_monitors',
      description: 'Lista los monitores configurados en Uptime Kuma',
      inputSchema: { type: 'object', properties: {} }
    },
    {
      name: 'uptime_monitor_detail',
      description: 'Obtiene el detalle de un monitor específico',
      inputSchema: {
        type: 'object',
        properties: {
          monitorId: { type: 'number', description: 'ID del monitor' }
        },
        required: ['monitorId']
      }
    },

    // ── Dashy ──
    {
      name: 'dashy_status',
      description: 'Verifica que Dashy homepage esté funcionando',
      inputSchema: { type: 'object', properties: {} }
    },

    // ── Plausible ──
    {
      name: 'plausible_stats',
      description: 'Obtiene estadísticas de Plausible analytics',
      inputSchema: {
        type: 'object',
        properties: {
          siteId: { type: 'string', description: 'ID del sitio en Plausible' },
          period: { type: 'string', enum: ['30d', '7d', 'today', 'month'], description: 'Período' }
        }
      }
    },
  ]
}));

// ─── EJECUCIÓN de HERRAMIENTAS ──────────────────────────────────

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    // ── Sistema ──
    case 'health_all': {
      const results = {};
      for (const [key, svc] of Object.entries(SERVICES)) {
        results[key] = await healthCheck(key);
      }
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            timestamp: new Date().toISOString(),
            services: results,
            summary: {
              total: Object.keys(SERVICES).length,
              online: Object.values(results).filter(Boolean).length,
              offline: Object.values(results).filter(v => !v).length
            }
          }, null, 2)
        }]
      };
    }

    case 'health_service': {
      const { service } = args;
      const alive = await healthCheck(service);
      const svc = SERVICES[service];
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            service: svc.name,
            icon: svc.icon,
            status: alive ? '🟢 online' : '🔴 offline',
            port: svc.port,
            description: svc.desc
          }, null, 2)
        }]
      };
    }

    case 'service_info': {
      const { service } = args;
      const svc = SERVICES[service];
      const alive = await healthCheck(service);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            name: svc.name,
            icon: svc.icon,
            description: svc.desc,
            status: alive ? 'online' : 'offline',
            endpoint: `http://${svc.host}:${svc.port}`,
            subdomain: `https://${service}.sonoradigitalcorp.com`,
            port: svc.port
          }, null, 2)
        }]
      };
    }

    // ── Paperclip ──
    case 'paperclip_status': {
      const result = await httpRequest('paperclip', '/api/health');
      return { content: [{ type: 'text', text: JSON.stringify(result.data || result, null, 2) }] };
    }

    // ── n8n ──
    case 'n8n_workflows': {
      try {
        const result = await httpRequest('n8n', '/rest/workflows');
        return { content: [{ type: 'text', text: JSON.stringify(result.data || { workflows: [] }, null, 2) }] };
      } catch (e) {
        return { content: [{ type: 'text', text: JSON.stringify({ error: e.message, note: 'n8n requiere autenticación. Workflows no listables sin token.' }) }] };
      }
    }

    case 'n8n_execute_workflow': {
      const { workflowId } = args;
      try {
        const result = await httpRequest('n8n', `/rest/workflows/${workflowId}/execute`, 'POST');
        return { content: [{ type: 'text', text: JSON.stringify(result.data || { executed: true }, null, 2) }] };
      } catch (e) {
        return { content: [{ type: 'text', text: JSON.stringify({ error: e.message }) }] };
      }
    }

    // ── Uptime Kuma ──
    case 'uptime_monitors': {
      try {
        const result = await httpRequest('uptime', '/api/monitors');
        return { content: [{ type: 'text', text: JSON.stringify(result.data || { monitors: [] }, null, 2) }] };
      } catch (e) {
        return { content: [{ type: 'text', text: JSON.stringify({ error: e.message, note: 'Uptime Kuma puede requerir login primero.' }) }] };
      }
    }

    // ── Metabase ──
    case 'metabase_questions': {
      return { content: [{ type: 'text', text: JSON.stringify({ note: 'Conectá Metabase en https://metabase.sonoradigitalcorp.com para crear queries. Luego usá metabase_query con el ID.' }) }] };
    }

    case 'metabase_query': {
      return { content: [{ type: 'text', text: JSON.stringify({ note: 'Primero configurá Metabase vía web UI y creá preguntas.' }) }] };
    }

    // ── Dashy ──
    case 'dashy_status': {
      const alive = await healthCheck('dashy');
      return { content: [{ type: 'text', text: JSON.stringify({ service: 'Dashy', status: alive ? 'online' : 'offline', url: 'https://dashy.sonoradigitalcorp.com' }) }] };
    }

    // ── Plausible ──
    case 'plausible_stats': {
      return { content: [{ type: 'text', text: JSON.stringify({ note: 'Plausible requiere configuración inicial vía web UI en https://analytics.sonoradigitalcorp.com' }) }] };
    }

    default:
      throw new McpError(ErrorCode.MethodNotFound, `Tool desconocida: ${name}`);
  }
});

// ─── RECURSOS MCP ────────────────────────────────────────────────

server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: 'mcp://sonora/status',
      name: 'Estado del Ecosistema',
      description: 'Estado actual de todos los servicios',
      mimeType: 'application/json'
    },
    {
      uri: 'mcp://sonora/services',
      name: 'Lista de Servicios',
      description: 'Todos los servicios disponibles en el ecosistema',
      mimeType: 'application/json'
    },
    {
      uri: 'mcp://sonora/vision',
      name: 'Visión Cuántica',
      description: 'Documento de visión cuántica del ecosistema',
      mimeType: 'text/html'
    },
    ...Object.keys(SERVICES).map(key => ({
      uri: `mcp://sonora/service/${key}`,
      name: `${SERVICES[key].name} — Info`,
      description: SERVICES[key].desc,
      mimeType: 'application/json'
    }))
  ]
}));

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const uri = request.params.uri;
  
  if (uri === 'mcp://sonora/status') {
    const results = {};
    for (const [key] of Object.entries(SERVICES)) {
      results[key] = await healthCheck(key);
    }
    return {
      contents: [{
        uri,
        mimeType: 'application/json',
        text: JSON.stringify({ timestamp: new Date().toISOString(), services: results }, null, 2)
      }]
    };
  }
  
  if (uri === 'mcp://sonora/services') {
    return {
      contents: [{
        uri,
        mimeType: 'application/json',
        text: JSON.stringify(Object.entries(SERVICES).map(([k, v]) => ({
          id: k, name: v.name, icon: v.icon, desc: v.desc, port: v.port
        })), null, 2)
      }]
    };
  }
  
  // Servicio individual
  const match = uri.match(/^mcp:\/\/sonora\/service\/(\w+)$/);
  if (match && SERVICES[match[1]]) {
    const svc = SERVICES[match[1]];
    const alive = await healthCheck(match[1]);
    return {
      contents: [{
        uri,
        mimeType: 'application/json',
        text: JSON.stringify({
          id: match[1], name: svc.name, status: alive ? 'online' : 'offline',
          endpoint: `http://${svc.host}:${svc.port}`,
          subdomain: `https://${match[1]}.sonoradigitalcorp.com`,
          icon: svc.icon, description: svc.desc
        }, null, 2)
      }]
    };
  }
  
  throw new McpError(ErrorCode.NotFound, `Recurso no encontrado: ${uri}`);
});

// ─── ARRANQUE ────────────────────────────────────────────────────

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`🔮 ${SERVER_NAME} v${MCP_VERSION} — Conectado vía MCP Stdio`);
  console.error(`📡 Servicios monitoreados: ${Object.keys(SERVICES).join(', ')}`);
}

main().catch(e => {
  console.error('❌ Error fatal:', e);
  process.exit(1);
});
