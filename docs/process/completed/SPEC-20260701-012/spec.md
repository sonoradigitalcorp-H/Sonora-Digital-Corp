# SPEC — Migrar 17 JARVIS Agents al Nuevo Ecosistema

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260701-012` |
| **Fecha** | 2026-07-01 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Migrar los 17 agentes JARVIS (Research, Code, Memory, Voice, etc.) al nuevo ecosistema: Redis Stream para comunicación, Ollama local para decisiones, y HermesClient para herramientas.

---

## 2. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | AgentBaseV2 con Redis pub/sub + Ollama (ask_local) + HermesClient |
| FR2 | ResearchAgentV2 — busca en Neo4j + decide con Ollama |
| FR3 | MemoryAgentV2 — almacena/recupera de Neo4j + Redis |
| FR4 | ReviewAgentV2 — code review con Ollama local |
| FR5 | OrchestratorV2 que enruta tareas a V2 agents |
| FR6 | Tests para V2 agents (mocks) |
| FR7 | CI verde con nuevos tests |

---

## 3. Success Criteria

- [ ] AgentBaseV2 con Redis + Ollama + HermesClient
- [ ] 3 V2 agents migrados (research, memory, review)
- [ ] OrchestratorV2 funcionando
- [ ] 6 tests pasando
- [ ] CI verde

---

## 4. Technical Approach

```
AgentBaseV2 (agent_base_v2.py)
  ├── Redis pub/sub (agent:messages stream)
  ├── ask_ollama() (local via llm.py)
  └── HermesClient (tools via MCP)

agents_v2/
  ├── research_v2.py — busca en Neo4j, sintetiza con Ollama
  ├── memory_v2.py — guarda/recupera en Neo4j via Redis
  ├── review_v2.py — code review con Ollama
  └── __init__.py — OrchestratorV2 con routing
```
