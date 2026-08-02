# SPEC — Primer Agente Real: Healer Agent con Modelo Local

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260701-008` |
| **Fecha** | 2026-07-01 |
| **Autor** | OpenClaw |
| **Tier** | 3 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Reemplazar `scripts/healer.py` (script lineal) por un **agente JARVIS real** que use **deepseek-r1:7b** (local) para decidir si reiniciar un contenedor o escalar. Los agentes JARVIS hoy existen pero no usan modelos locales ni se comunican entre sí. Este spec activa ambas cosas.

---

## 2. Value Driver

founder-independence, automation, knowledge, reliability

---

## 3. Diagrama de Arquitectura Actual vs Propuesta

```
HOY (scripts lineales, sin agentes reales):

  cron/timer → monitor.py → events.jsonl (nadie lee)
  cron/timer → healer.py → docker restart (sin decision, sin LLM)
  cron/timer → dashboard-salud.py → HTML estatico

MAÑANA (agentes reales con modelo local):

  AgenteMonitor (JARVIS) → detecta → publica a Redis Stream
       ↓
  AgenteHealer (JARVIS) ← lee de Redis Stream
       ↓
  consulta Neo4j: "dependencias del container?"
       ↓
  consulta Ollama (deepseek-r1:7b): "reinicio o escalo?"
       ↓
  ejecuta decision → publica resultado a Redis
       ↓
  AgenteNotifier ← resultado critico → Telegram
       ↓
  AgenteAprendiz (Engram): "que aprendi de este evento?"
```

---

## 4. Functional Requirements

| FR# | Descripción | Capa |
|-----|-------------|------|
| FR1 | JARVIS agents usan Ollama (deepseek-r1:7b) en vez de API externa | Runtime |
| FR2 | Redis Stream `agent:messages` creado con consumer groups | Communication |
| FR3 | AgenteMonitor publica `container_down` a Redis Stream (no a JSONL) | Agent |
| FR4 | AgenteHealer escucha Redis Stream, consulta Neo4j + Ollama, decide | Agent |
| FR5 | AgenteNotifier escucha resultados críticos, envía Telegram | Agent |
| FR6 | Hermes MCP reactivado y sirviendo como gateway de agentes | Infrastructure |
| FR7 | AgenteHealer tiene sandbox: timeout 30s, si excede → fallback a restart directo | Sandbox |
| FR8 | Metadata evolutiva: cada decision se guarda en Engram con resultado | Learning |
| FR9 | Dashboard muestra decisiones recientes de agentes (no solo eventos crudos) | UI |

---

## 5. Success Criteria

- [ ] JARVIS agent llama a Ollama local y recibe respuesta (<10s)
- [ ] AgenteMonitor escribe a Redis Stream, no a JSONL
- [ ] AgenteHealer lee de Redis Stream y ejecuta decision
- [ ] AgenteHealer consulta Neo4j antes de reiniciar
- [ ] AgenteHealer usa deepseek-r1:7b para decidir
- [ ] AgenteNotifier envía Telegram cuando un agente decide escalar
- [ ] Decisiones guardadas en Engram con resultado (exito/fracaso)
- [ ] Score ≥60

---

## 6. Archivos a crear/modificar

| Archivo | Acción | Qué hace |
|---------|--------|----------|
| `apps/jarvis/src/core/agents/healer_agent.py` | **Nuevo** | Agente Healer con Ollama + Neo4j |
| `apps/jarvis/src/core/agents/monitor_agent.py` | **Nuevo** | Agente Monitor que publica a Redis |
| `apps/jarvis/src/core/agents/notifier_agent.py` | **Nuevo** | Agente que escucha y notifica Telegram |
| `apps/jarvis/src/core/redis_streams.py` | **Modificar** | Agregar consumer groups para agentes |
| `apps/jarvis/src/core/llm.py` | **Modificar** | Agregar backend Ollama local |
| `apps/jarvis/src/core/orchestrator.py` | **Modificar** | Registrar 3 nuevos agentes |
| `apps/jarvis/src/core/unified_bridge.py` | **Modificar** | Conectar Hermes MCP |
| `scripts/healer.py` | **Deprecar** | Reemplazado por agente |
| `scripts/monitor.py` | **Deprecar** | Reemplazado por agente |
| `tests/agents/test_healer_agent.py` | **Nuevo** | Tests mock con Ollama simulado |
| `tests/agents/test_monitor_agent.py` | **Nuevo** | Tests mock con Redis simulado |

---

## 7. Pipeline de Decision del AgenteHealer

```
1. Recibe evento de Redis Stream: {"type": "container_down", "container": "sdc-neo4j"}
2. Consulta Neo4j: "MATCH (c:Service {id: 'sdc-neo4j'})-[r:DEPENDS_ON]->(d) RETURN d"
   → Sabe que servicios dependen de neo4j
3. Construye prompt para Ollama:
   """
   Container sdc-neo4j (Neo4j Graph DB) esta caido.
   Dependencias: abe-service, jarvis-webui dependen de el.
   Historial: ultimo restart fue hace 6h por falta de memoria.
   RAM disponible: 3.8GB de 11GB.
   Decidir: reiniciar ahora, esperar, o escalar a humano?
   """
4. Ollama (deepseek-r1:7b) responde: "reiniciar"
5. Ejecuta docker restart
6. Publica resultado a Redis Stream: {"type": "healing_decision", "decision": "restart", "result": "success"}
7. Guarda en Engram: aprendizaje para futuras decisiones
```

---

## 8. Timeline

| Fase | Duración | Qué |
|------|----------|-----|
| F1: Conectar Ollama a JARVIS | 20 min | Modificar llm.py para backend local |
| F2: Reactivar Hermes MCP | 15 min | Diagnóstico y fix del gateway |
| F3: Crear AgenteMonitor | 15 min | Publica container_down a Redis |
| F4: Crear AgenteHealer | 25 min | Neo4j + Ollama + decision + restart |
| F5: Crear AgenteNotifier | 15 min | Escucha + Telegram |
| F6: Tests + CI | 20 min | Mocks para cada agente |
| **Total** | **~110 min** | |

---

## 9. Dependencies

- JARVIS Core corriendo (Docker) ✅
- Ollama con deepseek-r1:7b ✅
- Redis corriendo ✅
- Neo4j con grafo del sistema ✅
- Telegram bot @ABEfenix_bot ✅
- `apps/jarvis/src/core/` accesible ✅

---

## 10. Kill Criteria

Si después de 2 sesiones los agentes JARVIS no pueden usar Ollama local, abandonar enfoque de agentes y mantener scripts actuales.

---

## 11. Scale Criteria

- AgenteAprendiz: mining de decisiones pasadas para mejorar prompts
- Multi-modelo: deepseek para decisiones, qwen3 para tareas ligeras
- Sandbox completo: timeout + memoria limitada + jail por agente
- Mesh de agentes: cualquier agente puede llamar a cualquier otro via MCP
