# Tasks: Servidor MCP

---

## US4 — Ejecutar herramientas desde el LLM (P1)

- [x] Implementar `src/core/tools.py` con 10 tool definitions (JSON Schema)
- [x] Implementar 10 tool executors en `AVAILABLE_TOOLS`
- [x] Implementar `execute_tool()` router
- [x] Whitelist de ~30 comandos permitidos en `execute_command`
- [x] Validación de rutas de proyecto en `write_file`
- [x] Implementar servidor MCP (`docker/mcp-server/server.py`) con FastMCP
- [x] Implementar 10 MCP tools
- [x] Embeddings reales en MCP tools (768d, `docker/mcp-server/embeddings.py`)
- [x] Dockerfile multi-stage con HEALTHCHECK
- [x] Tests unitarios en `tests/unit/test_tools.py`

## US5 — Skills expandibles (P2)

- [x] SkillAgent en `src/core/orchestrator.py` (list_skills, run_skill, skill_docs)
- [x] Catálogo de 8 skills con nombre, descripción y parámetros
- [x] `run_skill` ejecuta via `execute_tool()` de tools.py
- [x] `skill_docs` devuelve metadata de una skill específica
- [x] Rate limiting en web_fetch (10 req/min por dominio)
- [x] Cache de resultados frecuentes (in-memory LRU básico)
- [x] Implementar executor para tool `ask_user`

---

**Completado**: 14 tareas | **Pendiente**: 3 tareas
