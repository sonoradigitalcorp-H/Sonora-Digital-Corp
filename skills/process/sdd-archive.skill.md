# SDD Archive

**Parent OS**: Agent OS
**Tier**: 2
**Description**: Documenta resultados y archiva la SPEC completada en process/completed/

## Output
- Mover `process/active/SPEC-{ID}.md` → `process/completed/SPEC-{ID}/`
- Mover `process/active/SCORE-{ID}.md` → `process/completed/SPEC-{ID}/`
- Mover `process/active/gherkin/` → `process/completed/SPEC-{ID}/`
- Mover `process/active/plan-{ID}.md` → `process/completed/SPEC-{ID}/`
- Mover `process/active/tasks-{ID}.md` → `process/completed/SPEC-{ID}/`
- Actualizar `AGENTS.md` si es necesario

## Prerequisites
- SDD Verify pasó todos los gates
- ADR.md escrito (si aplica)
- LECCION.md escrito
