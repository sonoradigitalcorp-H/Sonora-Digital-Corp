# Tasks: Modularización del Core

---

## US1 — Dividir orchestrator.py

- [x] Extraer AgentBase a src/core/agents/agent_base.py
- [x] Crear ResearchAgent, CodeAgent, MemoryAgent, ExploreAgent
- [x] Crear SkillAgent, VoiceAgent, ReviewAgent
- [x] Crear HermesAgent, GbrainAgent, OpenClawAgent
- [x] Reducir orchestrator.py de 1,080 a <200 líneas

## US2 — Dividir tools.py

- [x] Crear src/core/tools/definitions.py con JSON Schema
- [x] Crear src/core/tools/executors.py con implementaciones
- [x] Crear src/core/tools/router.py con dispatch
- [x] Verificar imports backward-compatibles

## US3 — Dividir fastapp.py

- [x] Crear webui/routes/app_state.py con estado compartido
- [x] Crear routers: pages, sessions, chat, files, skills
- [x] Crear routers: sdc, mysticverse, payments, abe
- [x] Crear routers: commands, voice, webhooks, approvals
- [x] Reducir fastapp.py de 1,453 a <30 líneas

## US4 — Tests y verificación

- [x] 330 tests pasan después de cada migración
- [x] Web UI responde en /api/status
- [ ] Verificar cobertura de código >80%

