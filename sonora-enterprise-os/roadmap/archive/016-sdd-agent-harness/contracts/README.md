# Contracts: SDD Agent Harness

**Spec**: spec.md
---
## API Contracts
- `POST /api/harness/init` — Iniciar flujo SDD para una nueva spec
- `GET /api/harness/status` — Estado del pipeline
- `POST /api/harness/phase` — Ejecutar una fase específica
- `GET /api/registry/skills` — Listar habilidades registradas
- `GET /api/engram/search` — Buscar contexto previo

## Data Contracts
```json
{
  "harness_init": {
    "spec_id": "string",
    "title": "string",
    "priority": "P1|P2|P3"
  }
}
```
```json
{
  "phase_result": {
    "phase": "research|spec|design|apply|verify|archive",
    "status": "success|error",
    "result": "object"
  }
}
```
