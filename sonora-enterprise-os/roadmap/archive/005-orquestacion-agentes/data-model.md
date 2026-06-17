# Data Model: Orquestación de Agentes
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| Agent | name, description, timeout, run() | Agente especializado |
| Task | id, input, agent, result, execution_time | Tarea enrutada |
| ContextEntry | id, agent, task, result_summary, timestamp | Historia de ejecución |
## Relaciones
```
(Agent)-[:EXECUTES]->(Task)
(Task)-[:PRODUCES]->(ContextEntry)
```
