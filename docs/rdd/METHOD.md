# RDD — Review-Driven Development (Method Spec)

> **RDD (Receipt/Review Driven Development)** es el gate de calidad obligatorio de Sonora Digital Corp para el proyecto RYE. Sin recibo RDD, no hay commit, push ni PR.
> Método híbrido: **JR-Lite** (spec-first, Joki Ruiz) + **Gentleman Programming** (Scope Rule, SDD, guardian-angel, Alan Buscaglia).

**Status:** Aceptado
**Created:** 2026-08-03
**Spec:** SPEC-030 · **ADR:** `ADR-20260803-RYE-RDD-GATE`

---

## 1. Principios

1. **Spec-first**: todo trabajo empieza con una spec (≥60/75), gherkin y eval antes del código.
2. **Gate obligatorio**: sin recibo RDD no hay commit/push/PR.
3. **Guardian-angel**: los fixes son acotados (1 intento, máx 120 líneas) y la validación es read-only.
4. **Kill switch**: `.rdd/killswitch.json` desactiva el gate solo en emergencia documentada.
5. **Trazabilidad**: cada commit lleva el hash RDD del recibo que lo autorizó.

## 2. Pipeline (6 pasos)

| Paso | Script | Descripción |
|------|--------|-------------|
| 1. Freeze | `scripts/rdd/freeze.sh` | Snapshot del candidato: huella dactilar (sha256 de fuentes), patch del diff, manifest.json |
| 2. Review | `scripts/rdd/review.sh` | 4 lentes en paralelo: sdd-engineer, test-engineer, frontend-architect, backend-architect |
| 3. Fix | `scripts/rdd/fix.sh` | Arreglo acotado: 1 intento, máx 120 líneas |
| 4. Validate | `scripts/rdd/validate.sh` | Validación read-only (no modifica nada) |
| 5. Receipt | `scripts/rdd/receipt.sh` | Recibo con hash RDD → autoriza commit (score ≥80, 0 criticals) |
| 6. Commit | `scripts/rdd/commit.sh` | Commit con hash RDD en el mensaje |

```
feature → freeze.sh → review.sh (4 lentes) ─┬─ ok → receipt.sh → commit.sh
                                            └─ issues → fix.sh (≤120L) → validate.sh → receipt.sh
```

## 3. Comandos (registrados en opencode.json como `rdd:*`)

```bash
opencode run rdd:freeze 'feature-name'
opencode run rdd:review all 'feature-name'           # 4 lentes en paralelo
opencode run rdd:fix 'feature-name'                  # arreglo acotado
opencode run rdd:validate 'feature-name'             # read-only
opencode run rdd:receipt 'feature-name'              # autorización
opencode run rdd:commit 'feature-name'               # commit con hash RDD
opencode run rdd:run 'feature-name'                  # pipeline completo
```

## 4. Recibo (receipt.json)

Campos clave:

| Campo | Regla |
|-------|-------|
| `aggregated_score` | promedio de los 4 lentes (0-100) |
| `critical_issues` | count de findings critical/high |
| `allowed_to_commit` | `true` solo si `score >= 80 && critical == 0` |
| `line_fix_budget` | 120 líneas máx por fix |
| `validation_passed` | validación read-only OK |

## 5. Kill switch

```json
// .rdd/killswitch.json
{
  "enabled": true,
  "reason": null,
  "activated_at": null
}
```

- `enabled: true` → gate activo (por defecto).
- `enabled: false` → gate desactivado SOLO en emergencia documentada (se anota `reason` y `activated_at`).
- La reactivación vuelve a `enabled: true`.

## 6. Benchmark

Objetivo: **60+ flujos** evaluados con `make sdd-eval` + `make eval-promptfoo`.

| Categoría | Flujos |
|-----------|--------|
| In-band (éxito) | 45 |
| Out-of-band (edge) | 10+ |
| Dead-end (bloqueado) | 5+ |
| **Total** | **60+** |

## 7. Generalización (Sprint 4)

Los scripts actuales hardcodean `apps/frontends/agentic-os`. En Sprint 4 se parametriza `RDD_APP_DIR` (env/arg) para que el gate funcione con cualquier directorio del monorepo, incluido `tenants/rye/` y `scripts/`.

## 8. Referencias

- `scripts/rdd/` — implementación (7 scripts)
- `ADR-20260803-RYE-RDD-GATE`
- `ADR-20260803-RYE-METHOD`
- `tests/gherkin/rye-rdd-gate.feature`
- `process/CONDUCT.md` (HAS-007)
