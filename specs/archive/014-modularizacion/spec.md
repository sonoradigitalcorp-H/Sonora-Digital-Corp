# Spec 014: Modularización del Core

## Objetivo
Dividir los archivos monolíticos del core en módulos independientes y reutilizables.

## Archivos target

| Archivo | Líneas | Estrategia |
|---------|--------|------------|
| `src/core/tools.py` | 503 | Dividir en `tools/` package (definitions, executors, router) |
| `webui/fastapp.py` | 1,453 | Dividir en `routes/` package por dominio (próximo sprint) |

## Plan tools.py → tools/

### Módulos nuevos

```
src/core/tools/
├── __init__.py      → Re-exporta todo para backward compat
├── definitions.py   → TOOL_DEFINITIONS (11 schemas JSON) + ALLOWED_COMMANDS
├── executors.py     → Las 11 funciones ejecutoras + rate_limit
└── router.py        → execute_tool dispatch + AVAILABLE_TOOLS

src/core/tools.py    → SE ELIMINA al final
```

### Dependencias
- `executors.py` importa `definitions.py` (ALLOWED_COMMANDS)
- `router.py` importa `executors.py` (funciones) + `definitions.py` (TOOL_DEFINITIONS)
- `__init__.py` re-exporta todo lo público

### Backward compatibility
Ningún import externo cambia: `from src.core.tools import X` sigue funcionando porque `tools/__init__.py` re-exporta todo.

## Criterios de éxito
- [ ] 330 tests pasan sin modificaciones
- [ ] Web UI responde en `/api/status`
- [ ] Cada módulo < 200 líneas
- [ ] Sin imports circulares

## Estado
**Sprint actual**: tools.py completo
**Próximo**: fastapp.py → routes/
