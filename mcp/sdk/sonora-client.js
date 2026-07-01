#!/usr/bin/env node
/**
 * ═══════════════════════════════════════════════════════════════
 * SONORA SDK v2.0 — Client Library con Auth JWT
 * ═══════════════════════════════════════════════════════════════
 * SDK en Node.js con manejo automático de tokens JWT.
 *
 * Uso:
 *   const Sonora = require('./sonora-client');
 *   const sdk = new Sonora({ clientId: 'sdc-core', clientSecret: '...' });
 *   await sdk.health('n8n');
 *   await sdk.tool('enterprise_score', {});
 * ═══════════════════════════════════════════════════════════════
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

class SonoraSDK {
  constructor(options = {}) {
    this.baseHost = options.host || '127.0.0.1';
    this.gatewayPort = options.gatewayPort || 18989;
    this.clientId = options.clientId || process.env.SONORA_CLIENT_ID;
    this.clientSecret = options.clientSecret || process.env.SONORA_CLIENT_SECRET;
    this._token = null;
    this._tokenExpiry = 0;

    this.services = {
      paperclip: { port: 3100 },
      n8n:       { port: 5678 },
      metabase:  { port: 3002 },
      uptime:    { port: 3003, name: 'uptime-kuma' },
      dashy:     { port: 3004 },
      plausible: { port: 3006 },
    };
  }

  _request(host, port, path, method = 'GET', body = null, headers = {}) {
    return new Promise((resolve, reject) => {
      const opts = {
        hostname: host,
        port,
        path,
        method,
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json', ...headers },
        timeout: 10000
      };

      const req = http.request(opts, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try { resolve({ status: res.statusCode, data: JSON.parse(data), raw: data, headers: res.headers }); }
          catch { resolve({ status: res.statusCode, data: null, raw: data, headers: res.headers }); }
        });
      });
      req.on('error', reject);
      req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
      if (body) req.write(JSON.stringify(body));
      req.end();
    });
  }

  _requestService(service, path, method = 'GET', body = null) {
    const svc = typeof service === 'string' ? this.services[service] : service;
    if (!svc) return Promise.reject(new Error(`Servicio desconocido: ${service}`));
    return this._request(this.baseHost, svc.port, path, method, body);
  }

  _requestGateway(path, method = 'GET', body = null) {
    return this._request(this.baseHost, this.gatewayPort, path, method, body);
  }

  async _ensureToken() {
    if (this._token && Date.now() < this._tokenExpiry) return this._token;
    if (!this.clientId || !this.clientSecret) {
      throw new Error('Se requiere clientId y clientSecret. Usar SONORA_CLIENT_ID / SONORA_CLIENT_SECRET env vars');
    }

    const r = await this._requestGateway('/api/auth/token', 'POST', {
      client_id: this.clientId,
      client_secret: this.clientSecret,
    });

    if (r.status !== 200) {
      throw new Error(`Auth failed: ${r.status} ${r.raw}`);
    }

    this._token = r.data.access_token;
    this._tokenExpiry = Date.now() + (r.data.expires_in * 1000) - 60000;
    return this._token;
  }

  async _authRequest(path, method = 'GET', body = null) {
    const token = await this._ensureToken();
    const result = await this._requestGateway(path, method, body, {
      'Authorization': `Bearer ${token}`,
      'X-Tenant-ID': this.clientId,
    });
    return result;
  }

  async health(serviceId) {
    try {
      const r = await this._requestService(serviceId, '/api/health');
      return { service: serviceId, status: r.status === 200 ? 'online' : 'degraded', code: r.status };
    } catch (e) {
      return { service: serviceId, status: 'offline', error: e.message };
    }
  }

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

  async tool(toolName, params = {}) {
    const r = await this._authRequest('/api/call', 'POST', { tool: toolName, params });
    return r.data;
  }

  async tools() {
    const r = await this._authRequest('/api/tools', 'GET');
    return r.data;
  }

  async status() {
    const r = await this._authRequest('/api/status', 'GET');
    return r.data;
  }

  async capability(task) {
    const r = await this._authRequest('/api/capability/resolve', 'POST', { task });
    return r.data;
  }

  async capabilities() {
    const r = await this._authRequest('/api/capability/list', 'GET');
    return r.data;
  }

  async skills() {
    const r = await this._authRequest('/api/call', 'POST', { tool: 'skills_list', params: {} });
    return r.data;
  }

  async skillSearch(query) {
    const r = await this._authRequest('/api/call', 'POST', { tool: 'skills_search', params: { query } });
    return r.data;
  }

  async skillStats() {
    const r = await this._authRequest('/api/call', 'POST', { tool: 'skills_stats', params: {} });
    return r.data;
  }

  async resource(serviceId, resourceUri) {
    const endpoint = `/api/resource/${encodeURIComponent(resourceUri)}`;
    return this._requestService(serviceId, endpoint);
  }

  async mcp(action, params = {}) {
    return this._requestGateway(`/api/call`, 'POST', { tool: action, params });
  }
}

module.exports = SonoraSDK;

if (require.main === module) {
  const cmd = process.argv[2] || 'status';
  const sdk = new SonoraSDK();

  (async () => {
    try {
      switch (cmd) {
        case 'status':
          const st = await sdk.status();
          console.log('\n🔮 SONORA SDK v2.0 — Estado del Ecosistema\n');
          console.log(`   Tenant: ${st.tenant || 'N/A'}`);
          console.log(`   Versión: ${st.version}`);
          console.log(`   Timestamp: ${st.timestamp}\n`);
          if (st.services) {
            for (const [key, status] of Object.entries(st.services)) {
              const icon = status ? '🟢' : '🔴';
              console.log(` ${icon} ${key.padEnd(14)} ${status ? 'online' : 'offline'}`);
            }
          }
          if (st.summary) {
            console.log(`\n 📊 ${st.summary.online}/${st.summary.total} servicios online`);
          }
          break;

        case 'health':
          const h = await sdk.healthAll();
          console.log(JSON.stringify(h, null, 2));
          break;

        case 'capabilities':
          const caps = await sdk.capabilities();
          console.log('\n📋 Capability Registry\n');
          (caps.capabilities || []).forEach(c => {
            console.log(` • ${c.capability.padEnd(30)} ${c.maturity.padEnd(18)} ${c.agent}`);
          });
          break;

        case 'skills':
          const sk = await sdk.skills();
          console.log(`\n📦 Skills Marketplace: ${(sk.skills || []).length} skills\n`);
          const bySource = {};
          (sk.skills || []).forEach(s => { bySource[s.source] = (bySource[s.source] || 0) + 1; });
          Object.entries(bySource).forEach(([k, v]) => console.log(`   ${k.padEnd(12)} ${v} skills`));
          break;

        case 'tools':
          const tl = await sdk.tools();
          console.log(`\n🔧 Tools disponibles: ${(tl.tools || []).length}\n`);
          (tl.tools || []).forEach(t => {
            console.log(` • ${t.name}`);
          });
          break;

        default:
          console.log(`Uso: node sonora-client.js <status|health|capabilities|skills|tools>`);
      }
    } catch (e) {
      console.error('Error:', e.message);
      process.exit(1);
    }
  })();
}
