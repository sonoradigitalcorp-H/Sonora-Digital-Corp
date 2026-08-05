# Spec 002: Dispatcher

**ID**: 002-dispatcher
**Version**: 1.0.0
**Date**: 2026-08-04
**Author**: Luis Daniel Guerrero Enciso

## Resumen

Punto único de entrada del sistema Harvis OS. Recibe todas las peticiones, las clasifica y las rutea al agente apropiado.

## Objetivo

Eliminar al humano como cuello de botella proporcionando un sistema automático de:
- Recepción de peticiones desde múltiples fuentes
- Clasificación determinista de tareas
- Routing a agentes apropiados
- Tracking de estado de tareas

## Contexto

### Servicios Relacionados

| Servicio | Relación |
|----------|----------|
| Telegram Bot | Adapter de entrada |
| Web UI | Adapter de entrada |
| CLI | Adapter de entrada |
| Planner | Siguiente paso en el flujo |
| Agent Registry | Consulta de agentes disponibles |
| Event Bus | Publicación de eventos |

### Dependencias

- Redis (colas y cache)
- PostgreSQL (estado de tareas)
- Agent Registry (consulta de agentes)

## Especificación

### Inputs

```python
# Petición entrante desde cualquier fuente
class IncomingRequest:
    source: str  # "telegram", "web", "cli", "api"
    user_id: str
    content: str
    metadata: dict = {}
    timestamp: datetime
```

### Outputs

```python
# Tarea clasificada lista para ser procesada
class ClassifiedTask:
    id: str  # UUID único
    request: IncomingRequest
    category: str  # "code", "git", "query", "deploy", "review", "other"
    priority: str  # "high", "medium", "low"
    assigned_agent: str  # Nombre del agente
    confidence: float  # 0.0 - 1.0
    routing_reason: str  # Razón del routing
    created_at: datetime
```

### Comportamiento

1. Recibe request desde cualquier adapter
2. Valida formato y contenido
3. Clasifica la tarea usando reglas deterministas
4. Consulta Agent Registry para agente disponible
5. Publica evento `task.created`
6. Retorna ClassifiedTask con agente asignado

### Reglas de Negocio

**Routing Determinista** (Principio II):

```yaml
routing_rules:
  code:
    patterns:
      - "código|code|programar|implementar|escribir|crear|desarrollar"
      - "función|function|clase|class|endpoint|api"
      - "bug|error|fix|arreglar|corregir"
    agent: openhands
    priority: high
    confidence: 0.9

  git:
    patterns:
      - "git|commit|branch|merge|push|pull|repo"
      - "changelog|versión|release"
    agent: aider
    priority: medium
    confidence: 0.85

  query:
    patterns:
      - "consultar|buscar|query|select|leer|ver|mostrar"
      - "¿qué|cuál|cuánto|dónde|cuándo"
    agent: data_agent
    priority: low
    confidence: 0.8

  deploy:
    patterns:
      - "deploy|desplegar|publicar|subir|lanzar"
      - "docker|container|servidor|server"
    agent: openhands
    priority: high
    confidence: 0.85

  review:
    patterns:
      - "revisar|review|audit|verificar|validar"
      - "prueba|test|testing"
    agent: openhands
    priority: medium
    confidence: 0.8

  other:
    patterns:
      - ".*"  # fallback
    agent: planner
    priority: low
    confidence: 0.5
```

**Fallback a LLM** (solo cuando confidence < 0.6):
- Si el routing determinista no es seguro, usar LLM local para clasificar
- El LLM sugiere categoría; el sistema confirma con reglas
- Nunca confiar 100% en el LLM para routing

### Contrato

```yaml
contract:
  input: IncomingRequest
  output: ClassifiedTask
  events_consume:
    - telegram.message
    - web.request
    - cli.command
  events_publish:
    - task.created
    - task.classified
    - task.routing_error
  tools_allowed:
    - agent_registry.query
    - event_bus.publish
    - cache.get
    - cache.set
```

## Componentes

### AdapterManager

- **Responsabilidad**: Gestiona múltiples fuentes de entrada
- **Inputs**: Requests desde adapters
- **Outputs**: IncomingRequest normalizado
- **Dependencias**: Telegram adapter, Web adapter, CLI adapter

### TaskClassifier

- **Responsabilidad**: Clasifica tareas usando reglas deterministas
- **Inputs**: IncomingRequest
- **Outputs**: Categoría + confidence
- **Dependencias**: routing_rules.yaml

### AgentRouter

- **Responsabilidad**: Asigna agente basado en categoría
- **Inputs**: Categoría clasificada
- **Outputs**: Agente asignado
- **Dependencias**: Agent Registry

### TaskTracker

- **Responsabilidad**: Rastrea estado de tareas
- **Inputs**: ClassifiedTask
- **Outputs**: Estado actualizado
- **Dependencias**: PostgreSQL

## API

### Crear Tarea

```
POST /api/v1/tasks
```

**Request**:
```json
{
  "source": "telegram",
  "user_id": "12345",
  "content": "Crea una función para validar emails"
}
```

**Response**:
```json
{
  "id": "uuid-1234",
  "category": "code",
  "priority": "high",
  "assigned_agent": "openhands",
  "confidence": 0.9,
  "routing_reason": "Pattern match: código|code|programar"
}
```

### Consultar Estado

```
GET /api/v1/tasks/{task_id}
```

**Response**:
```json
{
  "id": "uuid-1234",
  "status": "in_progress",
  "assigned_agent": "openhands",
  "created_at": "2026-08-04T12:00:00Z",
  "updated_at": "2026-08-04T12:05:00Z"
}
```

### Listar Tareas

```
GET /api/v1/tasks?status=pending&limit=10
```

## Eventos

### task.created

```json
{
  "type": "task.created",
  "payload": {
    "task_id": "uuid-1234",
    "category": "code",
    "assigned_agent": "openhands"
  },
  "timestamp": "2026-08-04T12:00:00Z"
}
```

### task.classified

```json
{
  "type": "task.classified",
  "payload": {
    "task_id": "uuid-1234",
    "category": "code",
    "confidence": 0.9,
    "routing_reason": "Pattern match"
  },
  "timestamp": "2026-08-04T12:00:00Z"
}
```

### task.routing_error

```json
{
  "type": "task.routing_error",
  "payload": {
    "task_id": "uuid-1234",
    "error": "No agent available for category",
    "fallback": "planner"
  },
  "timestamp": "2026-08-04T12:00:00Z"
}
```

## Testing

### Casos de Prueba

| ID | Descripción | Input | Output Esperado |
|----|-------------|-------|-----------------|
| TC-001 | Clasificar tarea de código | "Crea una función" | category=code, agent=openhands |
| TC-002 | Clasificar tarea de git | "Haz commit" | category=git, agent=aider |
| TC-003 | Clasificar tarea ambigua | "Arregla esto" | category=code, confidence=0.7 |
| TC-004 | Fallback a LLM | Texto complejo | category=other, agent=planner |
| TC-005 | Tarea sin contenido | "" | Error de validación |
| TC-006 | Agente no disponible | Agent offline | Reasignar o encolar |

### Casos Límite

- Mensaje vacío debe rechazarse
- Usuario desconocido debe manejarse
- Agente offline debe causar reasignación
- Confidence baja debe usar LLM como fallback

## Observabilidad

### Logs

- `[Dispatcher] Request recibida: source={source}, user={user_id}`
- `[Dispatcher] Tarea clasificada: id={task_id}, category={category}`
- `[Dispatcher] Routing a agente: agent={agent}, confidence={confidence}`
- `[Dispatcher] Error de routing: error={error}`

### Métricas

- `dispatcher_requests_total`
- `dispatcher_classification_duration_seconds`
- `dispatcher_routing_success_total`
- `dispatcher_routing_error_total`
- `dispatcher_agent_assignment_total`

## Constitution Check

### Principio I: Orquestación Única
- [x] Dispatcher es el ÚNICO punto de entrada
- [x] No hay comunicación directa usuario-agente
- [x] Flujo: Usuario → Dispatcher → Planner → Agente

### Principio II: Separación Determinista vs LLM
- [x] Routing principal es determinista (patterns)
- [x] LLM solo como fallback para ambigüedad
- [x] Interfaz determinista→LLM es explícita

### Principio III: Local-first
- [x] Clasificación es local (sin API)
- [x] LLM local para fallback
- [x] Datos no salen del sistema

### Principio IV: Testing
- [x] Tests de clasificación definidos
- [x] Tests de routing definidos
- [x] Tests de edge cases definidos

### Principio V: Trazabilidad
- [x] Cada task tiene UUID único
- [x] Cada routing se registra con razón
- [x] Historial de clasificaciones consultable

## Referencias

- Joaquín Ruiz - Separación Determinista vs LLM
- Redis Streams documentation
- PostgreSQL documentation

## Cambios

| Versión | Fecha | Autor | Cambio |
|---------|-------|-------|--------|
| 1.0.0 | 2026-08-04 | Luis Daniel Guerrero Enciso | Versión inicial |
