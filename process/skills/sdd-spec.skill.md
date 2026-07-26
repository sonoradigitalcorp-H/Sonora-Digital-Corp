# SDD Spec

**Parent OS**: Agent OS
**Tier**: 2
**Description**: Genera especificaciones SDD completas a partir de briefings usando el template SPEC.md

## Input
- Briefing del usuario o requerimiento

## Output
- `process/active/SPEC-{ID}.md` con FRs, success criteria, edge cases, score

## Template
`process/templates/SPEC.md`

## Verification
- [ ] Todos los campos del template están completos
- [ ] Score estimado ≥ 60
- [ ] Gherkin scenarios definidos
