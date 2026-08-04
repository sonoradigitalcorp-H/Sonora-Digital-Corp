# ADR-20260803-RYE-RDD-GATE

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260803-RYE-RDD-GATE` |
| **Fecha** | 2026-08-03 |
| **Spec** | SPEC-030: RYE OpenClaw Agents |
| **Estado** | aceptado |

---

## Context

`scripts/rdd/` contiene 7 scripts RDD (freeze.sh, review.sh, fix.sh, validate.sh, receipt.sh, commit.sh, run.sh) que nunca se ejecutaron, no están registrados en `opencode.json`, y hardcodean `apps/frontends/agentic-os`. El repo tiene historial de código sin revisión y keys leakadas. Se requiere un gate de calidad obligatorio para RYE.

## Decision

**RDD es el gate obligatorio**: sin recibo RDD no hay commit, push ni PR. El flujo por cambio:

1. `freeze.sh` — snapshot con huella dactilar del estado previo.
2. `review.sh` — 4 lentes de revisión en paralelo (sdd-engineer, test-engineer, frontend, backend); salida redactada (sin secrets).
3. `fix.sh` — arreglo acotado: 1 intento, máx 120 líneas; con guardian-angel.
4. `validate.sh` — validación read-only (no modifica nada).
5. `receipt.sh` — emite el recibo con hash RDD (autoriza commit).
6. `commit.sh` — commit incluyendo el hash RDD en el mensaje.

**Reglas**:
- Kill switch en `.rdd/killswitch.json`: `{"enabled": false}` desactiva el gate SOLO en emergencia documentada.
- El pipeline se generaliza en Sprint 4: parametrizar `RDD_APP_DIR` (hoy hardcodeado a `apps/frontends/agentic-os`).
- Los comandos se registran en `opencode.json` como `rdd:*` para que esta sesión los use.
- Benchmark: 60+ flujos (45 in-band, out-of-band, dead-end) con `make sdd-eval` + `make eval-promptfoo`.

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| **RDD como gate obligatorio (bloqueante)** | Calidad garantizada, nada sin revisar | Overhead por commit; kill switch necesario |
| RDD opcional | Flexible | Se salta siempre, pierde el propósito |
| Solo lint/typecheck | Rápido | No revisa lógica ni tests, no previene leaks |
| Sin gate | Máxima velocidad | Repite el historial de bugs/leaks del repo |

## Consequences

- **Positivas**: cada commit de código pasa por revisión; secrets redactados; cambio acotado (≤120 líneas).
- **Positivas**: el recibo con hash RDD da trazabilidad total commit↔revisión.
- **Riesgos**: el pipeline agrega latencia por commit; el kill switch puede abusarse — mitigado con documentación en `METHOD.md`.
- **Riesgos**: si `review.sh` falla por infra, el gate bloquea — mitigado con validate read-only y kill switch de emergencia.

## Related

- `docs/rdd/METHOD.md` (especificación completa)
- `scripts/rdd/*.sh` (implementación, a generalizar)
- `ADR-20260803-RYE-METHOD`
- `gherkin: tests/gherkin/rye-rdd-gate.feature`
