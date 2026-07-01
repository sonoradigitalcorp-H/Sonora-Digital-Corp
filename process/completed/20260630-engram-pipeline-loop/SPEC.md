# SPEC — FASE 5: Engram Pipeline Loop

| Campo | Valor |
|-------|-------|
| **ID** | SPEC-20260701-001 |
| **Fecha** | 2026-06-30 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | completado |

## Implementación

- `process-pipeline.sh complete` → llama a `pipeline_bridge.store_spec_completion()`
- `orchestrator.execute()` → `query_engram_context()` antes de `agent.run()`
- `orchestrator.execute()` → `store_spec_completion()` en errores con tag "error"
