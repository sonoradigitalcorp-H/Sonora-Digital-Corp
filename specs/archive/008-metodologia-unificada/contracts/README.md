# Contracts: Metodología Unificada
**Spec**: spec.md
---
## API Contracts
- `POST /api/commands` — Ejecutar comando de metodología (/gsd, /wrap-up, /reflect, /learn)
## Data Contracts
```json
{ "command": { "type": "gsd|wrap-up|reflect|learn", "steps": ["string"], "output": "string" } }
{ "experience": { "pattern": "string", "solution": "string", "confidence": "float", "source_agent": "string" } }
```
