const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SDC_DIR = path.join(__dirname, '..', '..');
const EVENTS_FILE = path.join(SDC_DIR, 'state', 'logs', 'events.jsonl');
const FINOPS_FILE = path.join(SDC_DIR, 'state', 'finops.jsonl');
const CONFIG_DIR = path.join(SDC_DIR, 'config');
const SECRETS_DIR = path.join(CONFIG_DIR, '.secrets');

class SecurityAudit {
  constructor() { this.issues = []; }

  _check(label, condition, severity) {
    if (!condition) this.issues.push({ label, severity, status: 'fail' });
    else this.issues.push({ label, severity, status: 'pass' });
  }

  _checkFile(path, label) {
    const exists = fs.existsSync(path);
    this._check(label + ' exists', exists, 'high');
    if (exists) {
      const perms = fs.statSync(path).mode.toString(8).slice(-3);
      this._check(label + ' permissions (600/644)', perms === '600' || perms === '644', 'medium');
    }
  }

  run() {
    this.issues = [];
    // Secrets
    this._checkFile(path.join(SECRETS_DIR, 'clients.json'), 'clients.json secrets');
    this._checkFile(path.join(SDC_DIR, '.env'), '.env file');
    if (fs.existsSync(path.join(SDC_DIR, '.env'))) {
      const env = fs.readFileSync(path.join(SDC_DIR, '.env'), 'utf-8');
      this._check('.env has no hardcoded secrets', !env.includes('sk-placeholder') && !env.includes('your_'), 'high');
      this._check('.env has API keys', env.includes('OPENROUTER_API_KEY=') || env.includes('OPENCODE_API_KEY='), 'high');
    }

    // MCP Gateway
    const mcpCode = fs.readFileSync(path.join(SDC_DIR, 'mcp', 'gateway', 'mcp-server-http.js'), 'utf-8');
    this._check('MCP has auth', mcpCode.includes('authMiddleware'), 'critical');
    const jwtCodeCheck = fs.readFileSync(path.join(SDC_DIR, 'mcp', 'auth', 'jwt.js'), 'utf-8');
    this._check('MCP has JWT', jwtCodeCheck.includes('jsonwebtoken') || mcpCode.includes('jwt'), 'critical');
    this._check('MCP has rate limiting', mcpCode.includes('checkRateLimit'), 'high');
    this._check('CORS restricted', mcpCode.includes('Access-Control-Allow-Origin'), 'medium');

    // Token validation
    const jwtCode = fs.readFileSync(path.join(SDC_DIR, 'mcp', 'auth', 'jwt.js'), 'utf-8');
    this._check('JWT uses RS256', jwtCode.includes('RS256'), 'critical');
    this._check('JWT has expiry', jwtCode.includes('expiresIn'), 'high');
    this._check('JWT has refresh token', jwtCode.includes('Refresh'), 'medium');

    // Auth middleware
    const authCode = fs.readFileSync(path.join(SDC_DIR, 'mcp', 'auth', 'middleware.js'), 'utf-8');
    this._check('Auth middleware checks Bearer', authCode.includes('Bearer'), 'critical');
    this._check('Auth has public paths whitelist', authCode.includes('PUBLIC_PATHS'), 'medium');

    // Infrastructure
    const dockerExists = fs.existsSync(path.join(SDC_DIR, 'infra', 'docker-compose.yml'));
    this._check('Docker compose exists', dockerExists, 'medium');
    if (dockerExists) {
      const dc = fs.readFileSync(path.join(SDC_DIR, 'infra', 'docker-compose.yml'), 'utf-8');
      this._check('Docker ports bound to 127.0.0.1', dc.includes('127.0.0.1:'), 'high');
      this._check('Docker has healthchecks', dc.includes('healthcheck'), 'medium');
      this._check('Docker has memory limits', dc.includes('mem_limit'), 'medium');
    }

    // FinOps
    if (fs.existsSync(FINOPS_FILE)) {
      const finops = fs.readFileSync(FINOPS_FILE, 'utf-8');
      const entries = finops.trim().split('\n').filter(Boolean).length;
      this._check('FinOps has entries', entries > 0, 'low');
    }

    // Events
    if (fs.existsSync(EVENTS_FILE)) {
      const events = fs.readFileSync(EVENTS_FILE, 'utf-8');
      const entries = events.trim().split('\n').filter(Boolean).length;
      this._check('Events log has entries', entries > 0, 'low');
    }

    // Brand & Soul
    this._checkFile(path.join(SDC_DIR, 'sonora-enterprise-os', 'constitution', 'SOUL.md'), 'SOUL.md constitution');
    this._checkFile(path.join(SDC_DIR, 'sonora-enterprise-os', 'constitution', 'OMEGA-PROMPT-v10.0.md'), 'OMEGA PROMPT constitution');

    // Git
    try {
      const status = execSync('git status --porcelain', { cwd: SDC_DIR, encoding: 'utf-8', timeout: 5000 });
      this._check('No uncommitted changes', status.trim().length === 0, 'medium');
    } catch { this._check('Git available', false, 'low'); }

    return {
      timestamp: new Date().toISOString(),
      total: this.issues.length,
      passed: this.issues.filter(i => i.status === 'pass').length,
      failed: this.issues.filter(i => i.status === 'fail').length,
      critical: this.issues.filter(i => i.severity === 'critical' && i.status === 'fail').length,
      high: this.issues.filter(i => i.severity === 'high' && i.status === 'fail').length,
      issues: this.issues,
      score: Math.round((this.issues.filter(i => i.status === 'pass').length / Math.max(1, this.issues.length)) * 100),
    };
  }
}

const audit = new SecurityAudit();
module.exports = { SecurityAudit, audit };
