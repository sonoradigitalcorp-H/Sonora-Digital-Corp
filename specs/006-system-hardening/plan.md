# Plan: System Hardening & Bridge Fix

## Archivos a modificar
1. `src/core/neo4j_store.py` — +save_memory, +get_memory, +search_memory, +memory_stats (YA HECHO)
2. `webui/routes/__init__.py` — key hardcodeada → env var (YA HECHO)
3. `src/core/unified_bridge.py` — Qdrant wiring (YA HECHO)
4. `src/core/verify.py` — fix divide-by-zero (YA HECHO)
5. `scripts/automation/memory-save.py` — auto-save script (YA HECHO)
6. `tests/unit/test_security_guard.py` — 17 tests (YA HECHO)
7. `tests/unit/test_engram.py` — 5 tests (YA HECHO)
8. `tests/unit/test_verify.py` — 6 tests (YA HECHO)
9. `tests/unit/test_harness.py` — 4 tests (YA HECHO)

## Archivos nuevos (no trackeados)
10. `DOCUMENTO_DE_ERRORES.md` — documentación de errores
11. `scripts/automation/` — auto-save cron
12. `.openclaw/workspace/skills/workflow-enforcer/` — enforcement system
13. `state/` — auto-save snapshots

## Riesgos
- WhatsApp bridge port: código usa 3001, bridge real está en 3002
- OpenClaw no corre (port 18789)
- RAM limitada (683Mi disponible)

## Línea base
- Tests: 376 passed
- Cobertura: 69%
- Bridges: Neo4j ✅ Qdrant ✅ Hermes ✅ WhatsApp 3002 ✅ OpenClaw ❌
