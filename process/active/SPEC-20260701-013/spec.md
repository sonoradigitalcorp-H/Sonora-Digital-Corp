# SPEC — Migración Completa a V2 + MCP Tools en Producción

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260701-013` |
| **Fecha** | 2026-07-01 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Completar la migración de todos los agentes JARVIS activos a la arquitectura V2 (Redis + Ollama + HermesClient) y conectar Git MCP + Memory MCP en producción para que los agentes commiteen cambios y recuerden decisiones.

---

## 2. Value Driver

founder-independence, automation, knowledge, scalability

---

## 3. Functional Requirements

### Fase A — Agentes V2 Restantes (14 agents)

| FR# | Agente | Archivo | Descripción |
|-----|--------|---------|-------------|
| FR1 | CodeAgentV2 | `code_v2.py` | Análisis y generación de código con Ollama |
| FR2 | ExploreAgentV2 | `explore_v2.py` | Navegación de archivos vía HermesClient |
| FR3 | SkillAgentV2 | `skill_v2.py` | Ejecución de skills especializadas |
| FR4 | VoiceAgentV2 | `voice_v2.py` | Procesamiento de voz (STT/TTS) |
| FR5 | PRAgentV2 | `pr_v2.py` | GitHub Pull Requests vía Hermes/Git MCP |
| FR6 | SalesAgentV2 | `sales_v2.py` | Pipeline de ventas con decisiones Ollama |
| FR7 | HermesAgentV2 | `hermes_v2.py` | Bridge a Hermes MCP Gateway |
| FR8 | OpenClawAgentV2 | `openclaw_v2.py` | Bridge a OpenClaw Gateway |
| FR9 | GbrainAgentV2 | `gbrain_v2.py` | Cerebro con grafo vía Neo4j + Ollama |

### Fase B — MCP Tools en Producción

| FR# | Descripción |
|-----|-------------|
| FR10 | Git MCP conectado: agente healer commitea cambios de config automáticamente |
| FR11 | Memory MCP conectado: agente healer guarda decisiones en grafo persistente |
| FR12 | OrchestratorV2 actualizado con todos los agentes V2 |

### Fase C — Tests y CI

| FR# | Descripción |
|-----|-------------|
| FR13 | Tests para cada V2 agent (mínimo 1 test por agente) |
| FR14 | CI workflow actualizado con V2 tests |
| FR15 | Total tests ≥ 160 |

---

## 4. Success Criteria

- [ ] 14 V2 agents creados con AgentBaseV2
- [ ] OrchestratorV2 enruta a todos los V2 agents
- [ ] Healer agent usa Git MCP para commits automáticos
- [ ] Healer agent usa Memory MCP para recordar decisiones
- [ ] Tests ≥ 160
- [ ] CI verde
- [ ] Score ≥ 60

---

## 5. Technical Approach

```
Fase A: Crear agentes V2
  └─ Cada agente hereda de AgentBaseV2 (Redis + Ollama + HermesClient)
  └─ Cada agente tiene método run(task, context) -> dict
  └─ OrchestratorV2 registra todos los agentes

Fase B: MCP Tools en producción
  └─ Agregar git_commit() al healer agent después de healing exitoso
  └─ Agregar memory_create_entities() al healer agent para registrar decisiones
  └─ Git MCP ya instalado (mcp-server-git)
  └─ Memory MCP ya instalado (@modelcontextprotocol/server-memory)

Fase C: Tests
  └─ tests/agents/test_agents_v2.py → tests para cada V2 agent
  └─ tests/agents/test_mcp_healer.py → tests para healer + MCP tools
```

---

## 6. Dependencies

- AgentBaseV2 existente ✅
- HermesClient existente ✅
- Git MCP instalado (mcp-server-git) ✅
- Memory MCP instalado (npx @modelcontextprotocol/server-memory) ✅
- pytest-timeout para CI ✅

---

## 7. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `agent_v2_created` | Nuevo V2 agent registrado |
| `healer_git_commit` | Healer agent commitea cambios |
| `healer_memory_store` | Healer guarda decision en Memory MCP |

---

## 8. Kill Criteria

Si después de 1 hora no se alcanzan 160 tests, abandonar migración parcial y dejar agents legacy funcionando.

---

## 9. Scale Criteria

- Auto-registro de agentes V2 en OpenClaw
- Heartbeat de agentes V2 via Telegram
- Dashboard de salud de agentes V2
