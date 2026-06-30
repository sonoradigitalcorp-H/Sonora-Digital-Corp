# SPEC — FASE 2: Redis Streams como Sistema Nervioso

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260630-004` |
| **Fecha** | 2026-06-30 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Reemplazar el `context_history` (lista Python en memoria) del orquestador por Redis Streams, y publicar eventos del pipeline también vía Redis Streams. Esto elimina el SPOF del orquestador y permite que otros consumidores (n8n, dashboards) escuchen eventos en tiempo real.

---

## 2. Value Driver

reliability, scalability, automation, founder-independence

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Módulo `redis_streams.py` con conexión lazy a Redis, XADD, XREVRANGE, XREAD |
| FR2 | `push_context()` del orquestador → XADD a stream `context:history` + fallback a lista en memoria |
| FR3 | `get_context()` del orquestador → XREVRANGE desde stream `context:history` + fallback a lista |
| FR4 | `_emit_event()` en sales_pipeline.py → publica a Redis Stream `events:pipeline` + events.jsonl |
| FR5 | `_emit_event()` en pipeline_bridge.py → publica a Redis Stream + events.jsonl |
| FR6 | Backward compat: si Redis no está disponible, opera en modo degradado (lista/file) |
| FR7 | Eventos publicados con `MAXLEN ~1000` para evitar crecimiento infinito del stream |
| FR8 | Tests: verificar publicación y lectura con Redis mock |

---

## 4. Success Criteria

- [ ] `push_context` escribe en Redis Stream cuando Redis está disponible
- [ ] `get_context` lee desde Redis Stream (últimos N)
- [ ] `_emit_event` escribe en Redis Stream + events.jsonl simultáneamente
- [ ] Modo degradado: sin Redis, opera con lista en memoria (sin crash)
- [ ] Todos los tests existentes siguen pasando (432)
- [ ] `redis-cli XLEN context:history` muestra entries después de operaciones

---

## 5. Technical Approach

- Módulo `apps/jarvis/src/core/redis_streams.py` con:
  - `get_redis()`: conexión lazy (redis.Redis), timeout 2s, captura excepciones
  - `stream_push(stream, data, maxlen=1000)`: XADD con MAXLEN ~
  - `stream_read(stream, count=10)`: XREVRANGE (más recientes primero)
  - `emit_event(event, payload)`: XADD a `events:pipeline` + write a events.jsonl
- Conexión Redis vía variables de entorno REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
- Fallback: si get_redis() devuelve None, la función retorna sin hacer nada

---

## 6. Dependencies

- Redis contenedor funcionando (sdc-redis, puerto 6379) ✅
- redis-py (ya en requirements.txt via `pip install neo4j`? No, `redis` package needed)

---

## 7. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `redis_stream_initialized` | Primera conexión exitosa a Redis |
| `redis_stream_fallback` | Redis no disponible, modo degradado |

---

## 8. Kill Criteria

Si Redis Streams introduce latencia perceptible (>100ms por operación) vs la lista en memoria, revertir y mantener el fallback como única opción.

---

## 9. Scale Criteria

Cuando haya >3 consumidores de streams (n8n, dashboard, agentes), agregar consumer groups con XREADGROUP.
