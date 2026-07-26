# SDD Framework — Sonora Digital Corp

**Spec-Driven Development** con Spec Kit integrado.

## Comandos disponibles

### CLI `sdd` (instalado global)

```bash
sdd init                          # Inicializa estructura SDD
sdd spec-new <capability-id>      # Crea nueva capability spec
sdd test                          # Corre BDD + structural evals
sdd eval                          # Corre structural evals
```

### OpenClaw skills (`/speckit.*`)

| Comando | Función |
|---------|---------|
| `/speckit.constitution` | Fotografía reglas del proyecto en `.specify/memory/constitution.md` |
| `/speckit.specify` | Crea SPEC en `process/active/` |
| `/speckit.clarify` | Quality gate: resuelve ambigüedades |
| `/speckit.plan` | Crea plan de implementación |
| `/speckit.analyze` | Validación cruzada constitución/spec/plan |
| `/speckit.tasks` | Genera tareas ordenadas por dependencias |
| `/speckit.implement` | Ejecuta implementación tarea por tarea |

### Makefile

```bash
make test         # Run unit tests
make test-all     # Run all tests (unit + gherkin BDD)
make eval         # Run structural evals
make sdd-test     # Run SDD BDD + structural tests
```

## Estructura del framework

```
.specify/              # Spec Kit workspace (constitution, templates, hooks)
specs/                 # Canonical capability specs (9 capabilities)
  index.yaml           # Índice de todas las capabilities
  schema/spec-v1.yaml  # Schema canónico adaptable
  capabilities/<id>/   # spec.md, plan.md, tasks.md, adr.md, gherkin/
adrs/                  # Architecture Decision Records
tests/gherkin/         # BDD Gherkin features (21 feature files)
tests/steps/           # Step definitions (pytest-bdd)
evals/                 # Structural evals + promptfoo LLM evals
  promptfoo/           # Promptfoo config para evals de LLM
  structural/          # Tests de integridad estructural
tools/sdd/             # CLI sdd package
skills/speckit/        # OpenClaw skills para /speckit.* commands
```

## Flujo de trabajo típico

1. `/speckit.constitution` — fotografía reglas actuales
2. `/speckit.specify "Feature Title"` — define qué y por qué
3. `/speckit.clarify SPEC-001` — resuelve ambigüedades
4. `sdd spec-new <capability>` — crea spec canónico en `specs/`
5. Crea Gherkin en `specs/capabilities/<id>/gherkin/`
6. `/speckit.plan SPEC-001` — define cómo
7. `/speckit.analyze SPEC-001` — valida consistencia
8. `/speckit.tasks SPEC-001` — genera tareas
9. `sdd test` — corre BDD tests (deben pasar con mocks)
10. `/speckit.implement SPEC-001` — implementa tarea por tarea
11. `make test-all` — verificación final

## Capacidades actuales (9)

- clone-person, sync-artist-data, analyze-artist, search-knowledge
- score-artist, generate-video, manage-crm, publish-track, process-payment
