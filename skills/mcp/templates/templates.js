/**
 * Templates — Scaffold agents, workflows, plugins in seconds
 */

const AGENT_TEMPLATE = `name: {{name}}
version: 1.0.0
description: "{{description}}"
model: llama3.2:3b
provider: ollama
capability: {{capability}}
maturity: 1-Manual
tools:
  - sonora:capability_resolve
  - sonora:enterprise_score
policies:
  max_tokens_per_call: 4096
  timeout_seconds: 30
events:
  emits: []
  listens: []
lifecycle:
  spawn: on-demand
  max_idle: 30m
  max_concurrent: 3
`;

const WORKFLOW_TEMPLATE = `name: {{name}}
description: "{{description}}"
steps:
  - id: step1
    agent: capability_resolve
    input: "{{input}}"
  - id: step2
    agent: enterprise_score
    input: "Actualiza métricas"
    depends_on: step1
`;

const PLUGIN_TEMPLATE = `{
  "name": "{{name}}",
  "version": "1.0.0",
  "description": "{{description}}",
  "tools": [],
  "capabilities": [],
  "webhook": null
}`;

const SCHEDULE_TEMPLATE = `{
  "id": "task-{{id}}",
  "name": "{{name}}",
  "schedule": "{{schedule}}",
  "tool": "{{tool}}",
  "params": {},
  "enabled": true
}`;

const ACHIEVEMENTS = {
  first_agent: { name: 'Primer Agente', desc: 'Creaste tu primer agente ADK', xp: 100, icon: '🧠' },
  first_workflow: { name: 'Primer Workflow', desc: 'Ejecutaste tu primer workflow multi-paso', xp: 150, icon: '⚡' },
  first_swarm: { name: 'Primer Swarm', desc: 'Coordinaste agentes en paralelo', xp: 200, icon: '🐝' },
  ten_tools: { name: 'Power User', desc: 'Usaste 10 tools diferentes', xp: 50, icon: '🔧' },
  first_plugin: { name: 'Plugin Master', desc: 'Instalaste tu primer plugin', xp: 100, icon: '🧩' },
  perfect_score: { name: 'Perfect Score', desc: 'Enterprise Score ≥ 80', xp: 300, icon: '🏆' },
  security_audit: { name: 'Security First', desc: 'Ejecutaste auditoría de seguridad', xp: 100, icon: '🔐' },
};

const templates = {
  agent: (vars) => AGENT_TEMPLATE.replace(/{{(\w+)}}/g, (_, k) => vars[k] || `\${${k}}`),
  workflow: (vars) => WORKFLOW_TEMPLATE.replace(/{{(\w+)}}/g, (_, k) => vars[k] || `\${${k}}`),
  plugin: (vars) => PLUGIN_TEMPLATE.replace(/{{(\w+)}}/g, (_, k) => vars[k] || `\${${k}}`),
  schedule: (vars) => SCHEDULE_TEMPLATE.replace(/{{(\w+)}}/g, (_, k) => vars[k] || `\${${k}}`),
  achievements: ACHIEVEMENTS,
};

module.exports = { templates };
