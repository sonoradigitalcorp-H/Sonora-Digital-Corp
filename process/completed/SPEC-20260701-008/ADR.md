# ADR-20260701-008 — Primer Agente Real con Modelo Local

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260701-008` |
| **Fecha** | 2026-07-01 |
| **Spec** | `SPEC-20260701-008` |
| **Estado** | aceptado |

---

## Context

Los scripts monitor.py, healer.py, dashboard-salud.py son lineales y no tienen capacidad de decisión. El sistema tiene JARVIS con 17 agentes, Redis Streams, Ollama local y Neo4j, pero nada de esto estaba conectado. Necesitábamos el primer agente real que use modelo local para decidir.

## Decision

### 1. Agentes como servicios systemd independientes

Tres agentes systemd que se comunican via Redis Stream (no llamadas directas):
- `agent-monitor.service`: detecta containers caídos, publica a Redis
- `agent-healer.service`: escucha Redis, consulta Neo4j + Ollama, decide
- `agent-notifier.service`: escucha eventos críticos, envía Telegram

### 2. Ollama como backend local de JARVIS

Se agregó el provider `ollama` a `llm.py` con función `ask_local()` que llama a `http://localhost:11434/api/chat`. Los agentes usan `qwen3:4b-64k` para decisiones rápidas.

### 3. Redis Stream como bus de mensajes (no JSONL)

Los eventos fluyen por Redis Stream `agent:messages` con consumer groups. Cada agente tiene su propio grupo. Esto reemplaza el patrón anterior de escribir a events.jsonl y que NADIE lea.

## Consequences

**Positivo:**
- Primer agente que usa modelo local para decidir (no script lineal)
- Comunicación asíncrona via Redis (agentes no se bloquean entre sí)
- Cada agente es reemplazable independientemente
- 7 tests pasando en CI

**Trade-offs:**
- Redis es otro punto de fallo (si Redis cae, los agentes no se comunican)
- Ollama puede ser lento (45s primera carga). Se usó qwen3:4b-64k como balance velocidad/calidad
- Los agentes JARVIS existentes (17 clases) aún no están conectados a este flujo

## Related

- Agents: `apps/agents/monitor_agent.py`, `healer_agent.py`, `notifier_agent.py`
- Redis Stream: `agent:messages`
- Ollama provider: `apps/jarvis/src/core/llm.py` → `ask_local()`
- Events: `container_down`, `healing_attempt`, `healing_success`, `healing_failure`, `container_critical`, `healing_escalated`
