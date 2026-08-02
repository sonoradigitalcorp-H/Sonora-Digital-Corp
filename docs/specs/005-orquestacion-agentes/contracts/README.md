# Contracts: Orquestación de Agentes
**Spec**: spec.md
---
## API Contracts
- `GET /api/agents` — Listar agentes disponibles
- `POST /api/agents/{name}/execute` — Ejecutar tarea en agente específico
- `GET /api/agents/context` — Obtener contexto de ejecución
## Data Contracts
```json
{ "agent": { "name": "string", "description": "string", "timeout": "int" } }
{ "task_result": { "agent": "string", "status": "success|error", "result": "object", "execution_time": "datetime" } }
```
