# ADR-0001: Estructura de Directorios Enterprise para Sonora Digital Corp

## Status
Accepted (Implemented 2026-08-05)

## Context
The previous directory structure of `/home/mystic/Documentos/Sonora Digital Corp` was a flat, unorganized tree with mixed client code, audiovisual assets, finances, and AI tooling scattered across random paths. This created friction for:
- AI agents (OpenCode, OpenHands) creating duplicate/casual folders
- New developer onboarding
- CI/CD pipeline scoping
- Security boundary enforcement per client/tenant

## Decision
Adopt a standardized Enterprise multitenant directory layout under `/home/mystic/Documentos/Sonora Digital Corp Nuevo`:

```
00_Administration/     → Governance, finances, reference materials
01_Core_Platform/       → Shared platform code (harvis-os, sonora-digital-corp)
02_Client_Projects/     → Per-client isolation with 4 standard layers
03_Sandbox_and_RnD/     → Temporary experiments (ops, state, tenants legacy)
```

Each client directory follows the 4-Layer Standard:
1. `01_Discovery/` → Requirements, specifications, documentation
2. `02_Source_Code/` → Application code (Skills/Bots/Agentes subfolders)
3. `03_Media_Assets/` → Audio and visual resources
4. `04_Deployment/` → Database files, environment configs

## Consequences
- ✅ 652 files migrated across 8 client directories
- ✅ All trash/cache folders (node_modules, .git, __pycache__) ignored during migration
- ✅ 25 empty directories cleaned post-migration
- ✅ SYSTEM_MANIFEST.md created as contract for future AI automation
- ❌ Legacy folders (00_Admin, 01_Core, 02_Clientes, 03_Sandbox) kept temporarily for rollback
- ❌ Source `Sonora Digital Corp` (old) retains only cache/temporary artifacts

## References
- System Manifest: `SYSTEM_MANIFEST.md`
- Specification: `docs/specs/0001-directory-refactor-spec.md`
