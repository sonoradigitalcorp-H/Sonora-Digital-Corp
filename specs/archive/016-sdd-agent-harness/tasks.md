# Tasks: SDD Agent Harness

---

## US1 — Registro de Habilidades (P1)

- [x] Crear `config/registry.json` con índice de habilidades
- [ ] Implementar `src/core/registry.py` para lectura/escritura del índice
- [ ] Integrar registry con el orquestador para discovery de skills

## US2 — Motor de Engram (P1)

- [x] Implementar `src/core/engram.py` con persistencia de contexto
- [ ] Crear sistema de etiquetado de lecciones aprendidas
- [ ] Integrar recuperación de contexto en ResearchAgent

## US3 — Pipeline de Fases (P1)

- [x] Crear `src/core/harness.py` con el flujo Research → Spec → Design → Apply → Verify → Archive
- [x] Implementar agentes especializados (spec.py, design.py, apply.py, verify.py, archive.py)
- [ ] Implementar el paso de "Briefing" entre Research y Spec

## US4 — Guardas de Calidad (P2)

- [x] Refinar `src/core/verify.py` con checks de constitución y checklist
- [ ] Crear scripts de validación estructural de specs
- [ ] Implementar TDD gate obligatoria antes de commit

---

**Completado**: 7 tareas | **Pendiente**: 5 tareas
