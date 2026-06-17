#!/usr/bin/env node
/**
 * ═══════════════════════════════════════════════════════════════
 * SONORA SDK v1.0 — Client Library para Sonora Digital Corp
 * ═══════════════════════════════════════════════════════════════
 * SDK en Node.js para interactuar con todos los servicios del
 * ecosistema vía MCP o directamente via REST.
 *
 * Uso:                   
 *   const Sonora = require('./sonora-client');
 *   const sdk = new Sonora();
 *   await sdk.health('n8n');
 *   await sdk.status();
 * ═══════════════════════════════════════════════════════════════
 */

const http = require('http');

class SonoraSDK {
  constructor(options = {}) {
    this.baseHost = options.host || '127.0.0.1';
    this.gatewayPort = options.gatewayPort || 0;
    this.services = {
      paperclip: { port: 3100 },
      n8n:       { port: 5678 },
      metabase:  { port: 3002 },
      uptime:    { port: 3003, name: 'uptime-kuma' },
      dashy:     { port: 3004 },
      plausible: { port: 3006 },
    };
  }

  /**
   * HTTP request helper
   */
  _request(service, path, method = 'GET', body = null) {
    return new Promise((resolve, reject) => {
      const svc = typeof service === 'string' ? this.services[service] : service;
      if (!svc) return reject(new Error(`Servicio desconocido: ${service}`));
      
      const opts = {
        hostname: this.baseHost,
        port: svc.port,
        path,
        method,
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        timeout: 10000
      };
      
      const req = http.request(opts, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try { resolve({ status: res.statusCode, data: JSON.parse(data), raw: data }); }
          catch { resolve({ status: res.statusCode, data: null, raw: data }); }
        });
      });
      req.on('error', reject);
      req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
      if (body) req.write(JSON.stringify(body));
      req.end();
    });
  }

  /**
   * Health check de un servicio específico
   */
  async health(serviceId) {
    try {
      const r = await this._request(serviceId, '/api/health');
      return { service: serviceId, status: r.status === 200 ? 'online' : 'degraded', code: r.status };
    } catch (e) {
      return { service: serviceId, status: 'offline', error: e.message };
    }
  }

  /**
   * Health check de todos los servicios
   */
  async healthAll() {
    const results = {};
    for (const key of Object.keys(this.services)) {
      results[key] = await this.health(key);
    }
    return {
      timestamp: new Date().toISOString(),
      services: results,
      summary: {
        total: Object.keys(results).length,
        online: Object.values(results).filter(r => r.status === 'online').length,
        offline: Object.values(results).filter(r => r.status === 'offline').length
      }
    };
  }

  /**
   * Ejecutar un tool MCP
   */
  async tool(serviceId, toolName, params = {}) {
    const endpoint = `/api/tool/${toolName}`;
    return this._request(serviceId, endpoint, 'POST', params);
  }

  /**
   * Leer un recurso MCP
   */
  async resource(serviceId, resourceUri) {
    const endpoint = `/api/resource/${encodeURIComponent(resourceUri)}`;
    return this._request(serviceId, endpoint);
  }

  /**
   * Información de todos los servicios con estado
   */
  async status() {
    const services = [];
    for (const [key, svc] of Object.entries(this.services)) {
      const h = await this.health(key);
      services.push({
        id: key,
        name: svc.name || key.charAt(0).toUpperCase() + key.slice(1),
        port: svc.port,
        status: h.status,
        httpCode: h.code || 0
      });
    }
    return services;
  }

  /**
   * Gateway MCP: envía comando al gateway unificado
   */
  async mcp(action, params = {}) {
    if (!this.gatewayPort) throw new Error('Gateway MCP no configurado. Usar options.gatewayPort');
    return this._request({ port: this.gatewayPort }, `/mcp/${action}`, 'POST', params);
  }
}

module.exports = SonoraSDK;

// ─── CLI mode ─────────────────────────────────────────────────────
if (require.main === module) {
  const sdk = new SonoraSDK();
  const cmd = process.argv[2] || 'status';
  
  (async () => {
    switch (cmd) {
      case 'status':
        const services = await sdk.status();
        console.log('\n🔮 SONORA SDK — Estado del Ecosistema\n');
        services.forEach(s => {
          const icon = s.status === 'online' ? '🟢' : s.status === 'degraded' ? '🟡' : '🔴';
          console.log(` ${icon} ${s.name.padEnd(14)} | :${s.port} | ${s.status}`);
        });
        break;
      case 'health':
        const h = await sdk.healthAll();
        console.log(JSON.stringify(h, null, 2));
        break;
      default:
        console.log('Uso: node sonora-client.js <status|health>');
    }
  })().catch(e => console.error('Error:', e.message));
}
