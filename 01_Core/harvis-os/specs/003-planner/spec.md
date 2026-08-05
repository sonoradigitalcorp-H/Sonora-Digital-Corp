# Spec 003: Planner

**ID**: 003-planner
**Version**: 1.0.0
**Date**: 2026-08-04
**Author**: Luis Daniel Guerrero Enciso

## Resumen

Motor de planificación que divide objetivos complejos en tareas ejecutables y secuenciadas.

## Objetivo

Convertir objetivos de alto nivel en planes de ejecución que los agentes puedan seguir:
- Dividir tareas complejas en subtareas manejables
- Establecer dependencias entre tareas
- Priorizar y secuenciar ejecución
- Manejar errores y reintentos

## Contexto

### Servicios Relacionados

| Servicio | Relación |
|----------|----------|
| Dispatcher | Recibe tareas clasificadas |
| Agent Registry | Consulta capacidades de agentes |
| Event Bus | Publica planes y resultados |
| Memory System | Consulta contexto previo |

### Dependencias

- Agent Registry (capacidades de agentes)
- Memory System (contexto histórico)
- Event Bus (comunicación)

## Especificación

### Inputs

```python
# Tarea del Dispatcher lista para ser planificada
class TaskToPlan:
    id: str
    category: str
    content: str
    assigned_agent: str
    confidence: float
    user_context: dict = {}
```

### Outputs

```python
# Plan de ejecución con tareas secuenciadas
class ExecutionPlan:
    id: str
    task_id: str
    objective: str
    steps: List[PlanStep]
    estimated_duration: int  # segundos
    required_agents: List[str]
    dependencies: List[str]
    created_at: datetime

class PlanStep:
    id: str
    order: int
    description: str
    agent: str
    action: str
    inputs: dict
    expected_output: str
    dependencies: List[str]  # IDs de steps previos
    retry_policy: dict
    timeout: int
```

### Comportamiento

1. Recibe tarea clasificada del Dispatcher
2. Consulta contexto en Memory System
3. Analiza complejidad de la tarea
4. Divide en steps usando reglas o LLM
5. Establece dependencias entre steps
6. Estima duración
7. Valida que cada step tiene agente capaz
8. Publica evento `plan.created`

### Reglas de Negocio

**División Determinista** (Principio II):

```yaml
# Patrones de división conocidos
known_patterns:
  crud:
    trigger: "CRUD|crear.*tabla|endpoint.*REST"
    steps:
      - description: "Definir esquema"
        agent: planner
      - description: "Crear migración"
        agent: openhands
      - description: "Implementar modelo"
        agent: openhands
      - description: "Crear endpoints"
        agent: openhands
      - description: "Escribir tests"
        agent: openhands
      - description: "Documentar API"
        agent: openhands

  bugfix:
    trigger: "bug|error|fix|arreglar"
    steps:
      - description: "Reproducir bug"
        agent: openhands
      - description: "Identificar causa raíz"
        agent: openhands
      - description: "Implementar fix"
        agent: openhands
      - description: "Escribir test de regresión"
        agent: openhands
      - description: "Verificar fix"
        agent: openhands

  refactor:
    trigger: "refactor|mejorar|optimizar"
    steps:
      - description: "Analizar código actual"
        agent: openhands
      - description: "Diseñar nueva estructura"
        agent: planner
      - description: "Implementar cambios"
        agent: openhands
      - description: "Ejecutar tests existentes"
        agent: openhands
      - description: "Actualizar documentación"
        agent: openhands
```

**Fallback a LLM**:
- Si el patrón no es conocido, usar LLM para generar plan
- LLM genera pasos; sistema valida que cada paso tiene agente capaz
- Plan generado por LLM requiere validación antes de ejecutar

### Contrato

```yaml
contract:
  input: TaskToPlan
  output: ExecutionPlan
  events_consume:
    - task.created
    - task.classified
  events_publish:
    - plan.created
    - plan.approved
    - plan.rejected
    - step.completed
    - step.failed
  tools_allowed:
    - memory.query
    - agent_registry.query
    - event_bus.publish
```

## Componentes

### PlanEngine

- **Responsabilidad**: Genera planes de ejecución
- **Inputs**: TaskToPlan
- **Outputs**: ExecutionPlan
- **Dependencias**: PatternMatcher, LLMPlanner

### PatternMatcher

- **Responsabilidad**: Identifica patrones conocidos
- **Inputs**: Contenido de tarea
- **Outputs**: Patrón matcheado o None
- **Dependencias**: known_patterns.yaml

### LLMPlanner

- **Responsabilidad**: Genera planes para tareas no conocidas
- **Inputs**: TaskToPlan + contexto
- **Outputs**: PlanStep[]
- **Dependencias**: Ollama (local LLM)

### DependencyResolver

- **Responsabilidad**: Calcula dependencias entre steps
- **Inputs**: PlanStep[]
- **Outputs**: PlanStep[] con dependencias resueltas
- **Dependencias**: Ninguna

## API

### Crear Plan

```
POST /api/v1/plans
```

**Request**:
```json
{
  "task_id": "uuid-1234",
  "content": "Crear API REST para gestión de usuarios"
}
```

**Response**:
```json
{
  "id": "plan-5678",
  "task_id": "uuid-1234",
  "objective": "Crear API REST completa para usuarios",
  "steps": [
    {
      "id": "step-1",
      "order": 1,
      "description": "Definir esquema de usuario",
      "agent": "openhands",
      "dependencies": []
    },
    {
      "id": "step-2",
      "order": 2,
      "description": "Crear migración",
      "agent": "openhands",
      "dependencies": ["step-1"]
    }
  ],
  "estimated_duration": 1800,
  "required_agents": ["openhands"]
}
```

### Aprobar Plan

```
POST /api/v1/plans/{plan_id}/approve
```

### Rechazar Plan

```
POST /api/v1/plans/{plan_id}/reject
```

**Request**:
```json
{
  "reason": "Falta paso de testing"
}
```

## Eventos

### plan.created

```json
{
  "type": "plan.created",
  "payload": {
    "plan_id": "plan-5678",
    "task_id": "uuid-1234",
    "steps_count": 5,
    "estimated_duration": 1800
  },
  "timestamp": "2026-08-04T12:00:00Z"
}
```

### plan.approved

```json
{
  "type": "plan.approved",
  "payload": {
    "plan_id": "plan-5678",
    "approved_by": "user"
  },
  "timestamp": "2026-08-04T12:05:00Z"
}
```

### step.completed

```json
{
  "type": "step.completed",
  "payload": {
    "plan_id": "plan-5678",
    "step_id": "step-1",
    "duration": 300,
    "result": "success"
  },
  "timestamp": "2026-08-04T12:10:00Z"
}
```

## Testing

### Casos de Prueba

| ID | Descripción | Input | Output Esperado |
|----|-------------|-------|-----------------|
| TC-001 | Plan CRUD conocido | "Crear tabla de usuarios" | Plan con 6 steps |
| TC-002 | Plan bugfix conocido | "Arreglar error de login" | Plan con 5 steps |
| TC-003 | Plan desconocido | Texto complejo | Plan generado por LLM |
| TC-004 | Tarea trivial | "Haz commit" | Plan con 1 step |
| TC-005 | Tarea ambigua | "Mejora el código" | Plan con steps de análisis |

### Casos Límite

- Tarea vacía debe rechazarse
- Agente no disponible debe causar replanificación
- LLM no disponible debe usar plan por defecto
- Dependencias circulares deben detectarse

## Observabilidad

### Logs

- `[Planner] Analizando tarea: id={task_id}`
- `[Planner] Patrón encontrado: {pattern}`
- `[Planner] Plan generado: steps={steps_count}`
- `[Planner] LLM usado para planificación`
- `[Planner] Error en planificación: {error}`

### Métricas

- `planner_tasks_received_total`
- `planner_plans_created_total`
- `planner_pattern_matches_total`
- `planner_llm_fallbacks_total`
- `planner_planning_duration_seconds`

## Constitution Check

### Principio I: Orquestación Única
- [x] Planner recibe del Dispatcher
- [x] No comunica directamente con usuario

### Principio II: Separación Determinista vs LLM
- [x] Patrones conocidos son deterministas
- [x] LLM solo para patrones nuevos
- [x] Plan LLM requiere validación

### Principio III: Local-first
- [x] Patrones son locales
- [x] LLM es local (Ollama)

### Principio IV: Testing
- [x] Tests de patrones definidos
- [x] Tests de LLM fallback definidos

### Principio V: Trazabilidad
- [x] Cada plan tiene ID único
- [x] Cada step se registra
- [x] Decisiones de planificación auditables

## Referencias

- LangGraph documentation
- State machines patterns
- Joaquín Ruiz - Separación Determinista vs LLM

## Cambios

| Versión | Fecha | Autor | Cambio |
|---------|-------|-------|--------|
| 1.0.0 | 2026-08-04 | Luis Daniel Guerrero Enciso | Versión inicial |
