# SDD Design

**Parent OS**: Agent OS
**Tier**: 2
**Description**: Crea plan.md y tasks.md desde especificaciones aprobadas

## Input
- `process/active/SPEC-{ID}.md` (score ≥ 60)

## Output
- `process/active/plan-{ID}.md` — secuencia de ejecución, fases, rollback
- `process/active/tasks-{ID}.md` — tareas desglosadas con verificación cada una

## Principles
- Una tarea a la vez
- Cada tarea tiene verificación explícita
- Fases atómicas (cada una termina con commit)
