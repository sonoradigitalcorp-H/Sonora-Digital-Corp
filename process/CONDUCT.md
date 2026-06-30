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
3. **TDD**: Tests must be written BEFORE code. `tests/` directory MUST have test files for every new module before any implementation commit.
4. **Tests Green**: All tests must pass before merge. CI enforces this.
5. **Coverage Gate**: Overall coverage ≥60% (enforced by pytest-cov). New modules must have ≥70% coverage.
6. **Events Emitted**: Events logged for all key actions
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
