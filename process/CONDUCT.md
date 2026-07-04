# Pipeline Process — CONDUCT.md

## Overview

Every change to this repo follows a tiered pipeline. The tier determines how much ceremony is required.

## Tiers

| Tier | Scope | Requirements | Score Gate |
|------|-------|-------------|------------|
| 1 | Quick fix, bug, typo, config | Lección only | No |
| 2 | Feature, improvement | Spec → Score → Gherkin → TDD → Code → ADR → Lección | ≥60 |
| 3 | Initiative, platform, product | VDD → EDD → PDD → ODD → SDD → BDD → TDD → ADR → Lección | ≥60 |

## Lifecycle

```
Tier 1:  Execute → Lección
Tier 2:  Spec → Score → Gherkin → Tests-First → Code → Tests-Green → Events → ADR → Lección
Tier 3:  VDD → EDD → PDD → ODD → SDD → BDD → TDD → ADR → Events → Lección
```

## Gates

1. **Spec First**: No code without an approved spec (except tier 1)
2. **Score Gate**: Score ≥60 required for tier 2+
3. **Planning Gate**: `scripts/plan-gate.py` debe generar PLAN.yaml antes de cualquier ejecución (tier 2+). Sin plan aprobado, no hay código.
4. **Verification Pipeline**: `scripts/verify-gate.py` ejecuta truth gate + security gate + cost gate después del plan, antes de ejecutar. Si algún gate falla → STOP + EXPLAIN + FIX.
5. **TDD**: Tests must be written BEFORE code. `tests/` directory MUST have test files for every new module before any implementation commit.
6. **Tests Green**: All tests must pass before merge. CI enforces this.
7. **Coverage Gate**: Overall coverage ≥60% (enforced by pytest-cov). New modules must have ≥70% coverage.
8. **Event Bus**: Toda operación emite evento via `scripts/emit-event.py` al stream unificado `state/events/events.jsonl`. No más events.jsonl dispersos.
9. **Truth Compliance**: Todo output debe ser validado contra `truth/` YAML. `scripts/validate-truth.py` corre en CI.
7. **ADR Filed**: Decisions documented
8. **Lección Saved**: Learning stored in Engram

## Joaquin Ruiz Lite — 15-Point Compliance

Every tier 2+ spec must pass:

1. [ ] Objetivo claro en 1 línea
2. [ ] Value Driver identificado
3. [ ] FR numerados (≥1)
4. [ ] Success criteria verificables
5. [ ] Gherkin scenarios (≥2: happy path + edge)
6. [ ] Edge cases documentados
7. [ ] Enums tipados (si aplica)
8. [ ] Data classes frozen (si aplica)
9. [ ] Módulos < 200 líneas
10. [ ] Dependencias explícitas
11. [ ] Eventos definidos
12. [ ] Kill criteria
13. [ ] Scale criteria
14. [ ] Docstrings con FR reference
15. [ ] Score calculado

## Directory Structure

```
process/
├── CONDUCT.md                    # This file
├── templates/
│   ├── SPEC.md                   # Spec template (JR-Lite compliant)
│   ├── SCORE.md                  # Score template
│   ├── EVENT.md                  # Event template
│   ├── ADR.md                    # ADR template
│   ├── LECCION.md                # Lecciones template
│   └── GHERKIN.md                # Gherkin template
├── active/                       # Active specs
│   ├── SPEC-{ID}.md
│   └── gherkin/
│       └── SPEC-{ID}.feature
├── completed/                    # Completed specs
│   ├── {YYYYMMDD}-{title}/
│   │   ├── SPEC.md
│   │   ├── SCORE.md
│   │   ├── ADR.md
│   │   ├── LECCION.md
│   │   └── events.jsonl
│   └── CATALOG.md               # Master catalog of everything done
```

## CATALOG.md Format

```markdown
| Fecha | ID | Título | Tier | Score | Estado | Lección |
|-------|-----|--------|------|-------|--------|---------|
| YYYY-MM-DD | SPEC-XXX | Title | 2 | 85 | completed | link |
```

## Auto-Doc System

**Cada sesión debe documentarse antes de marcar DONE.** El sistema auto-doc genera los archivos de proceso automáticamente.

### Gates de Documentación (obligatorios)

1. **No DONE sin docs**: Toda sesión con cambios (Tier 2+) debe generar directorio completo en `process/completed/`
2. **Auto-Doc primero**: Ejecutar `/doc` (o `python3 scripts/auto-doc.py --auto`) al final de cada sesión
3. **Verificar salida**: El auto-doc puede no capturar todo — revisar y completar manualmente
4. **CATALOG.md actualizado**: Toda spec completada debe aparecer en el catálogo
5. **Lección en Engram**: La lección debe almacenarse en la base de conocimiento (Engram/Neo4j)

### Cómo usar

```bash
# Auto-detect desde AGENTS.md
./scripts/auto-doc.sh --auto

# O manual:
./scripts/auto-doc.sh --spec-id SPEC-20260703-003 --title "Mi Feature" --tier 2 --summary "..."

# O via OpenCode agent:
/doc
```

### Checklist de Cierre de Sesión

```markdown
[ ] `/doc` ejecutado y docs generados
[ ] Directorio en `process/completed/{fecha}-{title}/` creado
[ ] SPEC.md con FRs y criterios de éxito
[ ] SCORE.md ≥60
[ ] ADR.md con decisiones documentadas
[ ] LECCION.md con ¿qué pasó?, ¿qué salió bien/mal?, ¿qué harías diferente?
[ ] events.jsonl con eventos de la sesión
[ ] gherkin/ con feature file
[ ] CATALOG.md actualizado
[ ] AGENTS.md anchored summary actualizado
```
