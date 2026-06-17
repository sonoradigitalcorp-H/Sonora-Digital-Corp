# Data Model: Modularización del Core
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| Module | name, path, lines, dependencies | Módulo del core |
| Route | path, method, handler, module | Ruta de la Web UI |
| AgentModule | name, file, base_class, methods_count | Módulo de agente |
## Relaciones
```
(Module)-[:DEPENDS_ON]->(Module)
(Route)-[:HANDLED_BY]->(Module)
(AgentModule)-[:IS_A]->(Module)
```
