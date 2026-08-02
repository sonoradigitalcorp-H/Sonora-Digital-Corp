# SPEC-20260701-003: Native Agent OS v3.0 — Workflow + Sandbox + UI

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260701-003` |
| **Fecha** | 2026-07-01 |
| **Autor** | Strategy OS |
| **Tier** | 3 |
| **Estado** | borrador |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Cerrar los 4 gaps contra la industria (Google ADK, OpenAI Agents SDK, Vercel AI SDK) para que SDC sea el Native Agent OS más completo del ecosistema.

---

## 2. Value Driver

**founder-independence**: workflows multi-agente sin código. **revenue**: agentes sandboxeados = producto vendible. **automation**: 100+ providers = sin vendor lock-in.

---

## 3. Los 4 Gaps vs Plan de Ataque

### Gap 1: Workflow Graph Engine → `sdc workflow`

**Industria**: Google ADK Workflow con grafo (routing, loops, fan-out/fan-in, human-in-the-loop)
**SDC hoy**: `orchestrator.py` con if/elif keyword matching

**Plan**:
```
sdc workflow init <name>        # crear workflow YAML
sdc workflow run <name>         # ejecutar
sdc workflow visualize <name>   # ver grafo

Formato:
  name: lead-to-cash
  steps:
    - id: qualify
      agent: sales-agent
      input: "califica este lead: {{lead}}"
    - id: proposal
      agent: sales-agent  
      input: "genera propuesta para {{qualify.output}}"
      depends_on: qualify
    - id: notify
      agent: hermes
      input: "notifica a slack: nuevo deal"
      depends_on: proposal
      on_failure: escalate
```

**Archivos**: `mcp/workflow/engine.js`, `mcp/adk/agents/*.yaml` (ya existen)
**Esfuerzo**: 3-4 días

---

### Gap 2: Sandbox Agents Reales → `sdc sandbox`

**Industria**: OpenAI Sandbox Agents con Docker, manifest.json, sesiones resumables
**SDC hoy**: `docker-runner.js` existe pero no está conectado al ADK ni tiene manifest

**Plan**:
```
sdc sandbox spawn <agent>       # crea contenedor Docker
sdc sandbox exec <agent> <cmd>  # ejecuta comando dentro
sdc sandbox logs <agent>        # logs en vivo
sdc sandbox kill <agent>        # mata contenedor

Cada agente ADK con:
  lifecycle:
    sandbox: docker
    image: node:20-alpine
    memory: 256m
    cpus: 0.5
    workspace: /home/agent
```

**Archivos**: `mcp/providers/docker-runner.js` (ya existe), conectar a `adk.js`
**Esfuerzo**: 2 días

---

### Gap 3: Multi-Provider Real → `sdc provider`

**Industria**: OpenAI SDK 100+ LLMs, Vercel SDK 30+ providers
**SDC hoy**: 2 providers hardcodeados en `provider-router.js`

**Plan**:
```
sdc provider add openai <key>   # registrar API key
sdc provider add anthropic <key>
sdc provider list               # ver todos
sdc provider test <name>        # probar conectividad
sdc provider fallback <chain>   # definir cadena de fallback

Fallback automático:
  research: gemini-2.5-flash → gpt-4o → deepseek-v4-flash
  code: deepseek-v4-flash → claude-3.5-sonnet → gpt-4o
  sales: gpt-4o → claude-3.5-sonnet → deepseek-v4-flash
```

**Archivos**: `mcp/providers/provider-router.js` (mejorar), `mcp/providers/provider-manager.js` (nuevo)
**Esfuerzo**: 1-2 días

---

### Gap 4: Web UI de Gestión → `adk web` equivalente

**Industria**: Google ADK tiene `adk web path/to/agents` — UI web para ver, crear, gestionar agentes
**SDC hoy**: Dashboard HTML de solo lectura en `/dashboard`

**Plan**:
```
Nuevo endpoint: GET /adk
UI interactiva con:
  - Lista de agentes ADK (vivos, muertos, capacitàs)
  - Editor YAML para crear/modificar agentes
  - Logs en tiempo real por agente
  - Botón "spawn" / "kill"
  - Selector de modelo por agente
  - Métricas de uso (tokens, costos, latencia)
```

**Archivos**: `mcp/gateway/adk.html` (nuevo), integrar con `adk.js` + `docker-runner.js`
**Esfuerzo**: 2 días

---

## 4. Lo que NO Vamos a Hacer (por ahora)

| Feature | Razón |
|---------|-------|
| 100+ providers | Solo necesitamos 5-6. El resto es ruido. Value First. |
| A2A protocol | Microsoft intenta estandarizar pero MCP ya ganó. |
| Tracing UI tipo OpenAI | Ya tenemos LangFuse + Dashboard. Suficiente. |
| Realtime voice agents | No es prioritario para SDC hoy. |

---

## 5. Roadmap + Esfuerzo Total

```
Semana 1: Workflow Engine
  └── engine.js + YAML parser + sdc workflow + tests
  └── 3-4 días

Semana 2: Sandbox + Multi-Provider
  └── Conectar docker-runner.js con ADK
  └── provider-manager.js + sdc provider
  └── 3-4 días

Semana 3: Web UI de Gestión  
  └── adk.html con editor YAML + logs + control
  └── 2 días

Total: ~8-10 días → Native Agent OS v3.0
```

---

## 6. Score Estimado

| Métrica | Score | Justificación |
|---------|-------|---------------|
| Revenue Impact | 7 | Sandbox agents = producto vendible a clientes |
| Scalability | 8 | Workflow engine escala mejor que if/elif |
| Reusability | 9 | Workflows reusables entre clients |
| Automation Impact | 9 | Workflows multi-agente automáticos |
| Knowledge Impact | 6 | Workflows documentados como YAML |
| Reliability | 7 | Fallback automático multi-provider |
| Founder Independence | 9 | Workflows sin código |
| Operational Simplicity | 7 | UI web reduce necesidad de CLI |
| Customer Value | 8 | Clientes pueden gestionar sus agents vía UI |
| FinOps Efficiency | 6 | Provider router ya conectado a FinOps |

**Total estimado: 76/100** → PASA

---

## 7. Kill Criteria

- Si después de 1 semana el workflow engine no ejecuta un workflow simple
- Si sandbox agents requieren más de 2 días de setup en VPS
- Si el equipo decide que Google ADK es mejor que seguir construyendo el propio

---

## 8. Scale Criteria

- Workflow engine escala a 50+ steps cuando se use Redis Streams para estado
- Sandbox agents escalan a 20+ concurrentes con Docker Compose
- Multi-provider escala a 10+ providers con rate limiting por provider
- UI web soporta 100+ agentes registrados
