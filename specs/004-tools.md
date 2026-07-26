---
title: Registro de Herramientas
date: 2026-07-25
status: draft
author: SDC Architecture Team
version: 1.0.0
---

# Tools — Registro y Ejecución

## Principio

Las herramientas están registradas con un **schema JSON** y solo el **Planner** puede ejecutarlas. El LLM nunca invoca herramientas directamente — esto garantiza seguridad, auditabilidad y baja latencia.

## Estructura de una Tool

```python
@dataclass
class Tool:
    name: str                    # Identificador único
    description: str             # Qué hace (para el planner/LLM)
    input_schema: dict           # JSON Schema de entrada
    output_schema: dict          # JSON Schema de salida
    permissions: list[str]       # Qué permisos necesita
    handler: Callable            # Función que ejecuta la tool
    timeout: int = 30            # Timeout en segundos
    tenant_scope: bool = True    # Si opera sobre datos del tenant
```

## Tools Canónicas

### system_monitor

```yaml
name: system_monitor
description: Obtiene métricas del sistema (CPU, RAM, disco, uptime)
input_schema:
  type: object
  properties:
    metric:
      type: string
      enum: [cpu, ram, disk, uptime, all]
output_schema:
  type: object
  properties:
    cpu_percent: { type: number }
    ram_percent: { type: number }
    ram_used_gb: { type: number }
    disk_percent: { type: number }
    uptime_hours: { type: number }
permissions: [system:read]
```

### browser_action

```yaml
name: browser_action
description: Navegación web automatizada con Playwright
input_schema:
  type: object
  properties:
    action:
      type: string
      enum: [navigate, click, type, screenshot, extract]
    url: { type: string }
    selector: { type: string }
    value: { type: string }
output_schema:
  type: object
  properties:
    success: { type: boolean }
    data: { type: string }
    screenshot: { type: string }
permissions: [browser:execute]
```

### tenant_query

```yaml
name: tenant_query
description: Ejecuta consultas SQL sobre la base de datos del tenant
input_schema:
  type: object
  properties:
    query: { type: string }
    params: { type: array }
output_schema:
  type: object
  properties:
    rows: { type: array }
    columns: { type: array }
    row_count: { type: integer }
permissions: [tenant:read]
```

### notification

```yaml
name: notification
description: Envía una notificación al dashboard del tenant
input_schema:
  type: object
  properties:
    title: { type: string }
    message: { type: string }
    type:
      type: string
      enum: [info, warning, error, success]
    target_user: { type: string }
output_schema:
  type: object
  properties:
    sent: { type: boolean }
    notification_id: { type: string }
permissions: [notification:send]
```

## Registro de Tools

```python
class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool): ...
    def get(self, name: str) -> Optional[Tool]: ...
    def list(self) -> list[Tool]: ...
    def execute(self, name: str, params: dict, tenant_id: str) -> ToolResult: ...
```

## Flujo de Ejecución

```
1. Planner detecta tool_call intent
2. Planner obtiene Tool del ToolRegistry
3. Planner valida input contra input_schema
4. Planner verifica permisos del tenant/usuario
5. Planner ejecuta tool.handler(params)
6. Resultado se valida contra output_schema
7. Resultado se devuelve al planner (y opcionalmente al LLM para post-procesar)
```

## Seguridad

- Cada tool tiene una lista de **permisos** requeridos
- El tenant debe tener el permiso para ejecutar la tool
- Las consultas `tenant_query` usan una conexión de **solo lectura**
- `browser_action` se ejecuta en un **contenedor aislado**
- Todas las ejecuciones se **loguean** con timestamp, tenant, usuario, input, output
