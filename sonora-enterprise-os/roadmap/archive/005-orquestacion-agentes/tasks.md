# Tasks: Orquestación de Agentes

---

## US11 — Delegar tareas (P1)

- [x] Implementar `AgentBase` clase abstracta
- [x] Implementar `AgentOrchestrator` con registro de 7 agentes
- [x] Routing por keywords con regex word-boundary
- [x] Soporte de ejecución secuencial y paralela (asyncio.gather)
- [x] Timeout por agente
- [x] Error handling por agente
- [x] Singleton `get_orchestrator()`
- [x] Convenience function `execute_task()`
- [x] 17+ casos de routing parametrizados en tests
- [x] Variantes verbales para routing ("revisá", "buscá", "mostrame", "decí")
- [x] Pasar contexto entre agentes (historial de ejecución)

## US12 — CodeAgent (P1)

- [x] `_analyze(path)` — métricas de archivo (líneas, funciones, complejidad)
- [x] `_generate(task)` — generar código con LLM y escribirlo
- [x] `_read(task)` — leer uno o varios archivos
- [x] `_fix_bug(task)` — leer + LLM fix + write + verify
- [x] Detección de intención por keywords

## US13 — MemoryAgent (P1)

- [x] `store(task)` — guardar en Neo4j con fallback in-memory
- [x] `recall(task)` — buscar en Neo4j + in-memory
- [x] `forget(task)` — eliminar de Neo4j + in-memory
- [x] `list(task)` — listar todos los recuerdos
- [x] Prueba en test_orchestrator.py

## US14 — ReviewAgent, ExploreAgent, SkillAgent, VoiceAgent (P2)

- [x] ReviewAgent: `review_file`, `review_snippet`, `suggest_fixes` con score 1-10
- [x] ExploreAgent: `explore`, `search`, `structure` (tree), `read_batch`
- [x] SkillAgent: `list_skills` (8), `run_skill`, `skill_docs`
- [x] VoiceAgent: `transcribe`, `speak`, session management, `status`
- [x] Tests unitarios para los 5 agentes nuevos (+3 bridge agents)

---

**Completado**: 25 tareas | **Pendiente**: 0 tareas
