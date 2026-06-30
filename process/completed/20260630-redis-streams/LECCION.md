# Lección — SPEC-20260630-004

| Campo | Valor |
|-------|-------|
| **Spec** | `SPEC-20260630-004` |
| **Tier** | 2 |
| **Fecha** | 2026-06-30 |

---

## ¿Qué pasó?

Implementación de Redis Streams como sistema nervioso: reemplazo del context_history en memoria por Redis Streams, y publicación dual de eventos (file + stream).

---

## ¿Qué salió bien?

- [x] `redis_streams.py` con conexión lazy, XADD, XREVRANGE, fallback degradado
- [x] Orquestador: push_context → Redis Stream + lista, get_context → Redis primero
- [x] Pipeline: _emit_event → events.jsonl + Redis Stream simultáneamente
- [x] 11 tests nuevos (443 total)
- [x] Build Docker exitoso con redis-py instalado
- [x] Fallback probado: sin Redis todo opera en modo degradado

---

## ¿Qué salió mal?

- [ ] Import conflict: orchestrator.clear_context() vs redis_streams.clear_context() (alias necesario)
- [ ] El alias `redis_clear_stream` quedó verboso — podría llamarse `clear_redis_stream`
- [ ] No se probó con Redis real (no corre en local)

---

## ¿Qué haríamos diferente?

- Probar con Redis real en VPS después del deploy
- Agregar consumer groups cuando haya >3 consumidores
- Simplificar el naming: `clear_redis_stream` en vez de `redis_clear_stream`

---

## Engram Tags

redis, streams, event-driven, orchestrator, fallback, nervous-system, spec-004
