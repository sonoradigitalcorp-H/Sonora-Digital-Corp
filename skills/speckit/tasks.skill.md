# speckit.tasks

**Description**: Genera tareas ordenadas por dependencias desde plan + spec.

**Usage**: `/speckit.tasks <spec-id>`

**Prompt**:
```
Eres un planificador de proyectos. Genera tareas detalladas para implementar la SPEC {spec-id}.

Pasos:
1. Lee `process/active/SPEC-{spec-id}.md` y `process/active/plan-{spec-id}.md`
2. Lee `.specify/templates/tasks-template.md` para el formato
3. Crea `process/active/tasks-{spec-id}.md` organizado en fases:
   - Fase 1: Setup (infraestructura compartida)
   - Fase 2: Foundation (prerrequisitos bloqueantes)
   - Fase 3: User Story 1 (P1 — MVP)
   - Fase 4: User Story 2 (P2)
   - Fase 5: User Story 3 (P3)
   - Fase N: Polish (cross-cutting)
4. Cada tarea debe incluir:
   - ID numérico
   - Priority marker [P] si es paralelizable
   - Story marker [US1/US2/US3]
   - Ruta de archivo exacta
5. Incluir tareas de test (TDD primero, luego implementación)
```
