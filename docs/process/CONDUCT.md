# Pipeline Process — CONDUCT.md (HAS-007)

## Overview

Every change follows the **Hermes Architecture Standard (HAS)** pipeline. The old VDD→TDD pipeline is replaced by **Mission→Evolution** (HAS-007). See `process/has/` for the full specification.

## Pipeline Stages

```
Tier 0:  Implementation → Verification
Tier 1:  Research → Implementation → Verification → Observability
Tier 2:  Architecture → Specification → Implementation → Verification → Observability
Tier 3:  Mission → Constitution → Research → Architecture → Simulation → Specification → Implementation → Verification → Observability → Evolution
```

## Tiers

| Tier | Scope | Pipeline Stages | Gates |
|------|-------|-----------------|-------|
| 0 | Typo, config, comment | 7 → 8 | Tests green |
| 1 | Quick fix, minor bug | 3 → 7 → 8 → 9 | Constitution + Tests |
| 2 | Feature, improvement | 4 → 6 → 7 → 8 → 9 | Full constitution + Tests + Score ≥60 |
| 3 | Capability, platform, initiative | 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 | All gates + ADR + Score ≥75 |

## Gates

0. **Sync First (GIT-006)**: `scripts/git-sync.sh --status` antes de empezar. Repo en sync o no se trabaja.
1. **Constitution Gate**: `python3 scripts/constitution-gate.py --plan PLAN.yaml` — 6 sub-gates: Policy → Security → Cost → Compliance → Quality → Knowledge. Todos PASS obligatorio.
2. **Spec First (HAS Stage 6)**: No code without an approved spec (Tier 2+). Specs now use HAS-007 templates.
3. **Score Gate**: Score ≥60 (Tier 2), ≥75 (Tier 3). `scripts/score-gate.py`.
4. **TDD**: Tests first, code second. `tests/` must exist before implementation.
5. **Tests Green**: All tests pass. CI enforces.
6. **Coverage Gate**: ≥60% overall, ≥70% new modules.
7. **Event Bus**: Every operation emits event via `scripts/emit-event.py` (HAS-003 schema).
8. **Constitution Compliance**: Every output validated against `constitution/` YAML (HAS-001).
9. **ADR Filed**: Architecture decisions documented (Tier 3).
10. **Lección Saved**: Learning stored in Evolution Engine (HAS-008).
11. **Observability Gate**: Deploy + monitor + alert configured (Tier 2+).

## Hermes Architecture Standard (HAS)

The full specification lives in `process/has/`:

| Spec | What it defines |
|---|---|
| HAS-000 | Index + Glossary |
| HAS-001 | Constitution Engine (16 YAML files, gates) |
| HAS-002 | Memory Contracts (MemoryStore interface, 7 types) |
| HAS-003 | Event Mesh (schema, catalog.yaml, producers/consumers) |
| HAS-004 | Cognitive Kernel (Context → Planner → Policy → Router → Executor → Reflector) |
| HAS-005 | Capability Bus (capability.yaml, lifecycle, Workflow Engine) |
| HAS-006 | Agent Runtime (HermesAgent ABC, registry, lifecycle) |
| HAS-007 | Pipeline Evolution (Mission→Evolution flow, tiers, gates) |
| HAS-008 | Evolution Engine (observer, scorecard, proposer, ADR generator, auto-doc) |
| HAS-009 | Experience Layer (Orb states, channels, Kernel→UI contract) |
| HAS-010 | Security & Governance (agent auth, secrets, audit) |
| HAS-011 | Multi-tenancy (tenant_id, isolation levels) |

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
