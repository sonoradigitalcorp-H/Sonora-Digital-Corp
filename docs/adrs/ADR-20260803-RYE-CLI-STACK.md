# ADR-20260803-RYE-CLI-STACK

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260803-RYE-CLI-STACK` |
| **Fecha** | 2026-08-03 |
| **Spec** | SPEC-030: RYE OpenClaw Agents |
| **Estado** | aceptado |

---

## Context

El proyecto RYE usa varias CLIs para construir, evaluar y operar el sistema. Inventario actual (2026-08-03):

| CLI | Estado | Uso |
|-----|--------|-----|
| `openclaw` | ✅ instalado (2026.7.1-2) | gateway de bots, agentes, MCP |
| `engram` | ✅ instalado (v1.19) | memoria persistente |
| `sdd` | ⬜ NO instalado | `sdd eval`/`init` (requiere `pip install -e scripts/tools/sdd`) |
| `gh` (GitHub CLI) | ✅ instalado | PRs, issues, checks |
| Playwright CLI | ✅ instalado (1.60.0) | browser automation |
| Context7 | ⬜ pendiente | contexto de librerías |
| Cloudflare Tunnel | ⬜ pendiente | túnel público (deploy VPS) |
| Railway | ⬜ pendiente | deploy cloud |
| TestSprite | ⬜ pendiente | QA automático |

## Decision

Para RYE se usa un **stack CLI mínimo pero completo** en esta ronda:

1. **Obligatorios (esta ronda)**: `openclaw` (gateway+agentes), `engram` (memoria), `sdd` (evals estructurales — se instala en T0.6), `gh` (git/PRs), Playwright (testing UI).
2. **Opcionales (fuera de ronda, NO instalar todavía)**: Context7, Cloudflare Tunnel, Railway, TestSprite — solo documentados; se instalan en el Sprint 5 (deploy VPS) cuando haya necesidad real.
3. Todos se registran en `opencode.json` (comandos `rdd:*`, aliases `make doctor-quick`).

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| **Instalar solo lo necesario ahora** | Sin fricción, sin deps rotas | Hay que instalar `sdd` manualmente |
| Instalar todo el stack de golpe | Todo listo | Riesgo de conflictos de versiones, sin uso real |
| No usar CLIs (todo manual) | Nada que mantener | Sin evals, sin gates, sin benchmark |

## Consequences

- **Positivas**: stack mínimo funcional; `sdd` habilita `make sdd-eval` y `make sdd-test`; `gh` habilita el flujo de PRs con RDD gate.
- **Positivas**: las CLIs opcionales quedan documentadas para el Sprint 5 sin costo ahora.
- **Riesgos**: `sdd` requiere instalar con pip; si falla, se degrada a evals estructurales manuales (T0.5).

## Related

- `scripts/tools/sdd/` (CLI SDD a instalar)
- `ADR-20260803-RYE-METHOD`
- `ADR-20260803-RYE-RDD-GATE`
