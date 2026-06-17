# Tasks: Infraestructura y Seguridad

---

## US15 — Sin credenciales expuestas (P1)

- [x] API keys movidas de código a `.env` (python-dotenv)
- [x] `.env.example` sanitizado con placeholders
- [x] Secrets almacenados en `~/sdcorp/.secrets/keys.env` (fuera del repo)
- [x] `.env` es symlink a `~/sdcorp/.secrets/keys.env`
- [x] Git history reescrito para remover keys expuestas
- [x] `git gc` purga objetos eliminados
- [x] GitHub token revocado y regenerado
- [x] OpenRouter key revocada y regenerada
- [x] OpenCode key revocada y regenerada
- [x] Tailscale auth key rotada
- [x] Vercel token revocado
- [x] Repositorio hecho privado en GitHub
- [x] No hay hardcoded keys en `src/core/llm.py`

## US16 — Tests automatizados (P1)

- [x] Tests de orquestador (`tests/unit/test_orchestrator.py`, 30 tests)
- [x] Tests de tools (`tests/unit/test_tools.py`, 17 tests)
- [x] Tests de neo4j_store (`tests/unit/test_neo4j_store.py`, 7 tests)
- [x] Tests de LLM (`tests/unit/test_llm.py`, 4 tests)
- [x] Tests de voice (`tests/unit/test_voice.py`, 19 tests)
- [x] Tests de integración de API (`tests/integration/test_api.py`, 13 tests)
- [x] CI pipeline (GitHub Actions: lint, test, docker build)
- [x] CD pipeline (deploy on tag/release)
- [x] Tests unitarios para MemoryAgent, ExploreAgent, SkillAgent, VoiceAgent, ReviewAgent
- [x] Tests para `embeddings.py` y `rag.py` (22 tests)

## US17 — Docker funcional (P2)

- [x] `docker-compose.yml` con 3 servicios funcionales (Neo4j, Qdrant, MCP)
- [x] HEALTHCHECK en cada servicio
- [x] Networks y volumes configurados
- [x] Dockerfile para cada servicio (multi-stage para MCP)
- [x] Servicio `web-ui` eliminado (apuntaba a `./saas-web/` inexistente)
- [x] Scripts de automatización: backup, healthcheck, setup-systemd

---

**Completado**: 24 tareas | **Pendiente**: 2 tareas
