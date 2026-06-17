# Data Model: Ecosistema Completo
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| Skill | name, source, enabled, version | Skill instalada |
| Platform | name, state, adapter, last_seen | Plataforma de comunicación |
| APIKey | name, scope, status, last_used | Llave de API configurada |
| Workflow | id, name, trigger, status, last_run | Workflow de n8n |
## Relaciones
```
(Platform)-[:USES]->(APIKey)
(Skill)-[:AVAILABLE_ON]->(Platform)
(Workflow)-[:TRIGGERED_BY]->(Platform)
```
