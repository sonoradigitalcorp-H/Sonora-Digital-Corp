# Data Model: SDD Agent Harness

**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| Skill | id, name, category, version, description, mcp_server | Habilidad o herramienta disponible en el ecosistema |
| ContextEntry | id, spec_id, tags, summary, timestamp, embedding | Registro de aprendizaje o solución de una spec |
| PhaseExecution | id, spec_id, phase, status, result, timestamp | Ejecución de una fase del pipeline (research, spec, design, apply, verify) |
| ConstitutionRule | id, principle, description, validation_script | Regla de la constitución que debe verificarse |

## Relaciones
```
(Skill)-[:IMPLEMENTED_BY]->(Agent)
(ContextEntry)-[:REFERENCES]->(Spec)
(PhaseExecution)-[:PART_OF]->(Spec)
(ConstitutionRule)-[:APPLIES_TO]->(Spec)
```