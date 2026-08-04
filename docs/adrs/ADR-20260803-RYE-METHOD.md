# ADR-20260803-RYE-METHOD

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260803-RYE-METHOD` |
| **Fecha** | 2026-08-03 |
| **Spec** | SPEC-030: RYE OpenClaw Agents |
| **Estado** | aceptado |

---

## Context

El repo ya tiene dos metodologías documentadas en el pipeline de desarrollo: **JR-Lite** (Joki Ruiz, 15 puntos spec-first) y **Gentleman Programming** (Alan Buscaglia — Scope Rule, SDD desde cero, guardian-angel, gentle-ai, RDD). Sin embargo, no había un documento que unificara ambas para el proyecto RYE, ni una especificación formal de RDD adaptada al monorepo.

## Decision

Para RYE se adopta un **método híbrido documentado en `docs/rdd/METHOD.md`**:

1. **Spec-first (JR-Lite + SDD)**: todo trabajo empieza con una spec (`docs/specs/030-*`), puntuada ≥60/75, con gherkin y eval antes del código.
2. **RDD como gate obligatorio**: cada commit de código pasa por el pipeline RDD (freeze → review 4 lentes → fix → validate → receipt → commit). Sin recibo, no hay commit/push/PR (`ADR-20260803-RYE-RDD-GATE`).
3. **Guardian-angel / gentle-ai**: los cambios son acotados (fix máx 120 líneas, 1 intento), con revisión read-only antes de escribir.
4. **Benchmark continuo**: `make sdd-eval` + `make eval-promptfoo` corren en cada sprint; objetivo 60+ flujos.
5. **Kill switch**: `.rdd/killswitch.json` desactiva el gate solo en emergencia documentada.

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| **JR-Lite + SDD + RDD unificados** | Pipeline completo spec→test→code→review→commit | Más pasos antes de commit |
| Solo JR-Lite (spec-first) | Rápido | Sin gate de revisión, código sin calidad |
| Solo RDD (review-driven) | Calidad en el commit | Sin spec previa, el scope puede crecer |
| Sin método formal | Máxima velocidad | Repite los problemas del repo (scope creep, leaks) |

## Consequences

- **Positivas**: un solo documento `METHOD.md` que unifica JR-Lite + Gentleman (SDD/RDD); gates claros (spec ≥60/75, RDD receipt); benchmark objetivo medible.
- **Positivas**: guardian-angel (fix acotado) reduce el riesgo de cambios destructivos.
- **Riesgos**: el pipeline agrega overhead por commit; se mitiga con scripts `scripts/rdd/*.sh` y kill switch.
- **Riesgos**: la disciplina la mantiene el agente (esta sesión) — se mitiga registrando los comandos `rdd:*` en `opencode.json`.

## Related

- `docs/rdd/METHOD.md` (la especificación)
- `process/CONDUCT.md` (HAS-007 pipeline)
- `ADR-20260803-RYE-RDD-GATE`
