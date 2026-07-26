# SDD Orchestrator

**Parent OS**: Agent OS
**Tier**: 2
**Description**: Coordina las 6 fases del pipeline SDD (Research → Spec → Design → Tasks → Apply → Verify → Archive)

## Flow
1. `/sdd-new` inicia el pipeline
2. Mystic delega cada fase a la skill correspondiente
3. Cada fase debe completarse y verificarse antes de pasar a la siguiente

## Dependencies
- `skills/process/sdd-spec.skill.md`
- `skills/process/sdd-design.skill.md`
- `skills/process/sdd-apply.skill.md`
- `skills/process/sdd-verify.skill.md`
- `skills/process/sdd-archive.skill.md`
- `skills/process/auto-doc.skill.md`

## References
- `process/templates/SPEC.md`
- `process/templates/SCORE.md`
- `process/templates/GHERKIN.md`
- `docs/PROTOCOLO.md`
