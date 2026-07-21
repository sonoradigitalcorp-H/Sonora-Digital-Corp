# Skill Spec Reference para Pack Generator

## Estructura de una Skill

```yaml
nexus_skill_spec: "1.0"

# Metadata
id: {pack}.{skill_name}
name: Nombre
version: 1.0.0
description: Qué hace

# Runtime
language: python   # o node
timeout: 10s

# Input/Output
inputs:
  action: { type: enum, values: [list, create, update, delete] }
  {param}: { type: string|number|boolean, required: true|false }

outputs:
  success: { type: boolean }
  data: { type: object }

# Tools MCP que necesita
tools_required:
  - id: hasura.query
  - id: qdrant.search
  - id: llm.chat

# Permisos
permissions:
  roles: [admin, manager, staff]

# Costo estimado
cost:
  per_call_usd: 0.002
  avg_latency_ms: 500

# Memoria
memory:
  reads_from: [tenant_kb, session]
  writes_to: [session]

# Eventos que emite
events:
  emits: [skill_name.action]
```

## Reglas

- Toda skill debe tener al menos 1 tool MCP
- Inputs y outputs documentados en spec
- Cost tracking obligatorio
- Timeout máximo: 30s
- Incluir tests unitarios + Gherkin
