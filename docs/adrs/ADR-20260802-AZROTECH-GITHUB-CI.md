# ADR-20260802-AZROTECH-GITHUB-CI

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260802-AZROTECH-GITHUB-CI` |
| **Fecha** | 2026-08-02 |
| **Spec** | Sync GitHub + CI (MVP) |
| **Estado** | aceptado |

---

## Context

El repo local apuntaba a un remoto Gitea (`http://149.56.46.173:3080/mystic/Sonora-Digital-Corp.git`) cuyo VPS está **muerto** (sin acceso). El trabajo del bot (módulos TICKET-001..010, evals, memorias) no estaba versionado. Se decidió mover la fuente de verdad a GitHub.

## Decision

1. **Nuevo remoto GitHub**: `git@github.com:sonoradigitalcorp-H/Sonora-Digital-Corp.git` (push por token HTTPS; el SSH por defecto apuntaba a otro usuario `perrykingla69-cyber`).
2. **CI con GitHub Actions** (`.github/workflows/aztrotech-ci.yml`): en push a `tenants/Aztrotech/bot/**` y `scripts/evals/**` → `py_compile` de todos los módulos, flake8 (errores graves E9/F63/F7/F82), y **eval gate** (lead accuracy con dataset, modo reglas).
3. **Sync de memorias**: `ops/state/sync_engram.py` exporta/importa el engram (por tenant: `engram_<tenant>.db`) a JSON versionable en `ops/state/memory-snapshots/`. Un job `sync-memories` importa el snapshot y commitea cambios.
4. **Keys**: la key de OpenRouter válida (`f78...1ab`) queda en `~/.bashrc` y `infra/.env.backup`; la key de suscripción OpenCode GO (`sk-...YU`) se guarda como `OPENCODE_API_KEY`. No se commitean secretos.

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| **GitHub (Actions + sync)** | CI real, backup en la nube, historial | Keys en URLs (se guardan en .gitconfig/credenciales) |
| Mantener Gitea muerto | Sin migración | Sin backup ni CI |
| Solo commit local sin CI | Rápido | Sin validación automática |

## Consequences

- **Positivas**: push `2ac784d..02e4e95` a GitHub (24 archivos), CI valida el bot en cada cambio, memorias versionadas y restaurables.
- **Positivas**: el ADR `WHATSAPP-OS-FASE1` y workflows legacy ya existían en `.github/workflows/`.
- **Trade-off**: el push usa token con permiso de `sonoradigitalcorp-H`; el SSH global del host no es del dueño del repo.
- **Nota**: el repo tiene ~6208 archivos marcados borrados en working tree (estado pre-existente); no se tocaron.

## Lessons

- `gh auth token` no existe en esta versión de gh; se extrajo el token del hosts.yml con python+yaml.
- El remoto con token en la URL funciona pero hay que evitar que quede en logs; usar credenciales helper es mejor a largo plazo.
- La CI corre el eval en modo `--no-llm` (sin key) para validar reglas sin costo.

## Related

- Spec: Sync GitHub + CI
- Events: `.github/workflows/aztrotech-ci.yml`, `ops/state/sync_engram.py`, `ops/state/memory-snapshots/aztrotech.json`
