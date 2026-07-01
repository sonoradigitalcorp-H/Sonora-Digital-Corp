/**
 * ═══════════════════════════════════════════════════════════════
 * Sonora Docker Runner v1.0 — Agent Sandboxing
 * ═══════════════════════════════════════════════════════════════
 * Corre cada agente ADK en su propio contenedor Docker efímero.
 * Aislamiento completo, recursos limitados, auto-cleanup.
 *
 * Uso:
 *   const runner = require('./docker-runner');
 *   await runner.spawn('sales-agent');
 *   await runner.kill('sales-agent');
 *   await runner.list();
 * ═══════════════════════════════════════════════════════════════
 */

const { execSync, exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const AGENTS_DIR = path.join(__dirname, '..', 'adk', 'agents');
const NETWORK = 'sdc-network';
const IMAGE = 'node:20-alpine';
const CONTAINER_PREFIX = 'sdc-agent-';

class DockerRunner {
  constructor() {
    this.running = new Map();
  }

  _docker(args) {
    try {
      const result = execSync(`docker ${args}`, { encoding: 'utf-8', timeout: 15000 });
      return { success: true, output: result.trim() };
    } catch (e) {
      return { success: false, error: e.message, output: e.stdout || '' };
    }
  }

  async spawn(agentName) {
    const agentFile = path.join(AGENTS_DIR, `${agentName}.yaml`);
    if (!fs.existsSync(agentFile)) {
      return { error: `Agente ${agentName} no encontrado en ADK` };
    }

    if (this.running.has(agentName)) {
      return { error: `Agente ${agentName} ya está corriendo (PID: ${this.running.get(agentName)})` };
    }

    const containerName = CONTAINER_PREFIX + agentName;
    const envFile = path.join(__dirname, '..', '..', '.env');

    let envArgs = '';
    if (fs.existsSync(envFile)) {
      const envContent = fs.readFileSync(envFile, 'utf-8');
      envContent.split('\n').forEach(line => {
        const trimmed = line.trim();
        if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
          envArgs += ` -e "${trimmed}"`;
        }
      });
    }

    const result = this._docker(
      `run -d --name ${containerName} --network ${NETWORK} --restart no` +
      ` --memory "256m" --cpus "0.5"` +
      ` --label "sdc.agent=${agentName}"` +
      ` --label "sdc.component=adk"` +
      ` ${envArgs}` +
      ` ${IMAGE} sleep 3600`
    );

    if (!result.success) {
      return { error: `Error spawning container: ${result.error}` };
    }

    this.running.set(agentName, containerName);
    return {
      success: true,
      agent: agentName,
      container: containerName,
      status: 'running',
      pid: result.output,
    };
  }

  async kill(agentName) {
    const containerName = this.running.get(agentName) || CONTAINER_PREFIX + agentName;
    const result = this._docker(`rm -f ${containerName}`);

    if (result.success) {
      this.running.delete(agentName);
      return { success: true, agent: agentName, status: 'stopped' };
    }
    return { error: `Error killing ${agentName}: ${result.error}` };
  }

  async list() {
    const result = this._docker(
      `ps --filter "label=sdc.component=adk" --format "{{.Names}}\t{{.Status}}\t{{.Ports}}"`
    );

    if (!result.success) return [];

    const agents = [];
    result.output.split('\n').forEach(line => {
      const [name, status, ports] = line.split('\t');
      if (name) {
        const agentName = name.replace(CONTAINER_PREFIX, '');
        agents.push({
          agent: agentName,
          container: name,
          status: status || 'unknown',
          ports: ports || '',
        });
      }
    });

    return agents;
  }

  async cleanup() {
    this._docker(`rm -f $(docker ps -aq --filter "label=sdc.component=adk") 2>/dev/null`);
    this.running.clear();
    return { success: true };
  }

  async exec(agentName, command) {
    const containerName = CONTAINER_PREFIX + agentName;
    const result = this._docker(`exec ${containerName} sh -c "${command}"`);
    return result;
  }

  async logs(agentName, lines = 50) {
    const containerName = CONTAINER_PREFIX + agentName;
    const result = this._docker(`logs --tail ${lines} ${containerName}`);
    return result;
  }
}

const runner = new DockerRunner();

module.exports = { DockerRunner, runner };
