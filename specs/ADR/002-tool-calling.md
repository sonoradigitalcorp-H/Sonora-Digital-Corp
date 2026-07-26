---
title: "ADR-002: Llamada de Herramientas (Tool Calling)"
date: 2026-07-25
status: accepted
author: SDC Architecture Team
version: 1.0.0
---

# ADR-002: Llamada de Herramientas

## Contexto

Mystic OS expone herramientas que ejecutan acciones en el mundo real: monitoreo del sistema, navegación web, consultas a base de datos, notificaciones. El riesgo de seguridad es alto si el LLM puede ejecutar herramientas arbitrariamente.

Necesitamos un sistema donde:

- Las herramientas tengan **schemas** y **permisos** explícitos
- El LLM solo **sugiera** herramientas, nunca las ejecute
- El sistema audite cada ejecución
- Los tenants puedan restringir herramientas según su plan

## Decisión

**El Planner ejecuta las tools**. El LLM solo participa en la decisión de **qué tool llamar** (como fallback del clasificador de intents). La ejecución real pasa por el `ToolRegistry`, que valida schema, permisos y tenant scope.

### Arquitectura

```
LLM (o clasificador) → sugiere tool_call con parámetros
       │
       ▼
Planner → ToolRegistry.execute(name, params, tenant_id)
       │
       ├── Valida input_schema
       ├── Verifica permisos
       ├── Ejecuta handler
       ├── Valida output_schema
       └── Devuelve resultado
```

### Alternativas Consideradas

1. **LLM ejecuta tools directamente** (function calling nativo): rápido pero inseguro — el LLM puede alucinar parámetros o llamar tools no autorizadas
2. **Agent loop**: el LLM decide, ejecuta, observa, repite — flexible pero lento, costoso, difícil de auditar
3. **Sistema de plugins**: el LLM llama un middleware que ejecuta — mejora seguridad pero añade latencia sin beneficio real sobre Planner + Registry

## Consecuencias

### Positivas

- **Seguridad**: el LLM nunca ejecuta nada directamente
- **Auditabilidad**: cada ejecución se loguea con timestamp, usuario, input, output
- **Permisos granulares**: cada tool define sus permisos, cada tenant los hereda o restringe
- **Schema validation**: entrada y salida validadas contra JSON Schema antes/después de ejecutar

### Negativas

- **Latencia adicional**: el planner añade ~5-10ms de overhead
- **Complejidad de registro**: cada tool debe declarar input_schema, output_schema, permissions
- **Mantenimiento**: los schemas deben actualizarse si la tool cambia

### Mitigaciones

- El overhead del planner es despreciable comparado con la latencia del LLM (100ms vs 2-10s)
- Los schemas se generan automáticamente con decoradores Python (`@tool`)

## Ejemplo

```python
@tool(
    name="system_monitor",
    description="Obtiene métricas del sistema",
    input_schema={"metric": {"type": "string", "enum": ["cpu", "ram"]}},
    permissions=["system:read"]
)
def system_monitor(metric: str) -> dict:
    # implementación
    pass
```

## Estado

**Aceptado**. Implementación en progreso con las 4 tools canónicas.
