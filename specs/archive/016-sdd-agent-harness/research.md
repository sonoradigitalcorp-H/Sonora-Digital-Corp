# Research: SDD Agent Harness

**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| SQLite + FTS5 | Ligero, embedido, búsqueda full-text | No distribuido | ✅ Seleccionado para Engram |
| PostgreSQL | Robusto, extensible | Overhead para uso sencillo | ❌ Descartado |
| Redis | Rápido, estructuras avanzados | Volátil sin persistencia | ❌ Descartado (necesitamos persistencia) |
| JSON Files | Simple, legible | Búsqueda lenta | ❌ Descartado para búsqueda de contexto |
## Decisión Arquitectónica
- **Selección**: SQLite con FTS5 para almacenar contexto etiquetado (Engram) + JSON registry para índice de habilidades
- **Motivo**: Baja latencia, zero-config, portabilidad
## Limitaciones
1. SQLite no soporta concurrent writes altos (pero suficiente para nuestro uso)
2. FTS5 requiere rebuilding ocasional para optimizar búsqueda
