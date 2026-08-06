# Spec 005: Event Bus

**ID**: 005-event-bus
**Version**: 1.0.0
**Date**: 2026-08-04
**Author**: Luis Daniel Guerrero Enciso

## Resumen

Sistema de comunicación asíncrona entre componentes de Harvis OS usando Redis Streams.

## Objetivo

Proporcionar un medio de comunicación desacoplado que:
- Permita comunicación asíncrona entre componentes
- Soporte múltiples consumidores por evento
- Garantice entrega al menos una vez
- Proporcione persistencia de eventos
- Soporte replay de eventos para debugging

## Contexto

### Servicios Relacionados

| Servicio | Relación |
|----------|----------|
| Dispatcher | Publica task.created, task.classified |
| Planner | Publica plan.created, plan.approved |
| Agents | Publican task.completed, task.failed |
| Registry | Publica agent.status_changed |
| Memory System | Escucha eventos para contexto |

### Dependencias

- Redis ( Streams)

## Especificación

### Inputs

```python
# Evento a publicar
class Event:
    id: str  # UUID único
    type: str  # "task.created", "plan.approved", etc.
    source: str  # Componente que genera el evento
    payload: dict  # Datos del evento
    metadata: dict = {}  # Datos adicionales
    timestamp: datetime

# Suscripción a eventos
class EventSubscription:
    consumer_id: str
    event_types: List[str]  # Tipos de eventos a escuchar
    group: str = "default"  # Consumer group
    callback: str  # URL o nombre de función
```

### Outputs

```python
# Evento procesado
class ProcessedEvent:
    event: Event
    status: str  # "delivered", "failed", "retry"
    consumer_id: str
    processed_at: datetime
    error: Optional[str] = None
```

### Comportamiento

1. Componentes publican eventos al Event Bus
2. Event Bus persiste eventos en Redis Streams
3. Consumidores se suscriben a tipos de eventos
4. Consumer Groups garantizan entrega sin duplicados
5. Eventos fallidos se reintenta con backoff
6. Eventos se retienen por 7 días para replay

### Reglas de Negocio

**Tipos de Eventos**:

```yaml
event_types:
  # Tareas
  task.created:
    description: "Nueva tarea creada por Dispatcher"
    required_fields: ["task_id", "category", "assigned_agent"]
    consumers: ["planner", "registry"]
    
  task.classified:
    description: "Tarea clasificada por Dispatcher"
    required_fields: ["task_id", "category", "confidence"]
    consumers: ["planner"]
    
  task.started:
    description: "Tarea comenzó a ejecutarse"
    required_fields: ["task_id", "agent_id"]
    consumers: ["dispatcher", "registry"]
    
  task.completed:
    description: "Tarea completada exitosamente"
    required_fields: ["task_id", "agent_id", "result"]
    consumers: ["dispatcher", "planner", "memory"]
    
  task.failed:
    description: "Tarea falló"
    required_fields: ["task_id", "agent_id", "error"]
    consumers: ["dispatcher", "planner"]

  # Planes
  plan.created:
    description: "Nuevo plan generado"
    required_fields: ["plan_id", "task_id", "steps_count"]
    consumers: ["dispatcher"]
    
  plan.approved:
    description: "Plan aprobado por usuario"
    required_fields: ["plan_id", "approved_by"]
    consumers: ["planner"]
    
  plan.rejected:
    description: "Plan rechazado"
    required_fields: ["plan_id", "reason"]
    consumers: ["planner"]

  # Steps
  step.started:
    description: "Step de plan comenzó"
    required_fields: ["plan_id", "step_id", "agent_id"]
    consumers: ["planner"]
    
  step.completed:
    description: "Step de plan completado"
    required_fields: ["plan_id", "step_id", "result"]
    consumers: ["planner"]
    
  step.failed:
    description: "Step de plan falló"
    required_fields: ["plan_id", "step_id", "error"]
    consumers: ["planner"]

  # Agentes
  agent.registered:
    description: "Agente registrado"
    required_fields: ["agent_id", "capabilities"]
    consumers: ["dispatcher"]
    
  agent.status_changed:
    description: "Estado de agente cambió"
    required_fields: ["agent_id", "old_status", "new_status"]
    consumers: ["dispatcher", "planner"]
    
  agent.health_check_failed:
    description: "Health check de agente falló"
    required_fields: ["agent_id", "error"]
    consumers: ["registry"]

  # Sistema
  system.started:
    description: "Sistema Harvis iniciado"
    required_fields: ["version"]
    consumers: ["all"]
    
  system.error:
    description: "Error del sistema"
    required_fields: ["error", "component"]
    consumers: ["all"]
```

**Políticas de Retención**:

```yaml
retention:
  default:
    max_len: 10000
    max_age_days: 7
  tasks:
    max_len: 50000
    max_age_days: 30
  system:
    max_len: 1000
    max_age_days: 90
```

**Reintentos**:

```yaml
retry_policy:
  max_retries: 3
  backoff:
    initial: 1  # segundos
    multiplier: 2
    max: 60
  dead_letter_queue: true
```

### Contrato

```yaml
contract:
  input: Event
  output: ProcessedEvent
  events_consume: []  # Event Bus consume todos los eventos
  events_publish: []  # Event Bus publica eventos recibidos
  tools_allowed:
    - redis.xadd
    - redis.xreadgroup
    - redis.xack
    - redis.xlen
```

## Componentes

### EventBus

- **Responsabilidad**: Core del sistema de eventos
- **Inputs**: Event para publicar
- **Outputs**: Confirmación de publicación
- **Dependencias**: Redis

### EventConsumer

- **Responsabilidad**: Consume y procesa eventos
- **Inputs**: Eventos desde Redis Streams
- **Outputs**: ProcessedEvent
- **Dependencias**: EventBus

### EventStore

- **Responsabilidad**: Almacena eventos para replay
- **Inputs**: Eventos procesados
- **Outputs**: Eventos históricos
- **Dependencias**: Redis

### DeadLetterQueue

- **Responsabilidad**: Maneja eventos fallidos
- **Inputs**: Eventos después de max_retries
- **Outputs**: Eventos para inspección manual
- **Dependencias**: Redis

## API

### Publicar Evento

```
POST /api/v1/events
```

**Request**:
```json
{
  "type": "task.created",
  "source": "dispatcher",
  "payload": {
    "task_id": "uuid-1234",
    "category": "code",
    "assigned_agent": "openhands"
  }
}
```

**Response**:
```json
{
  "id": "event-5678",
  "type": "task.created",
  "published_at": "2026-08-04T12:00:00Z"
}
```

### Consultar Eventos

```
GET /api/v1/events?type=task.created&limit=10
```

**Response**:
```json
{
  "events": [
    {
      "id": "event-5678",
      "type": "task.created",
      "source": "dispatcher",
      "payload": {},
      "timestamp": "2026-08-04T12:00:00Z"
    }
  ]
}
```

### Replay de Eventos

```
POST /api/v1/events/replay
```

**Request**:
```json
{
  "from": "2026-08-04T00:00:00Z",
  "to": "2026-08-04T12:00:00Z",
  "types": ["task.created", "task.completed"]
}
```

### Estadísticas

```
GET /api/v1/events/stats
```

**Response**:
```json
{
  "total_events": 1500,
  "events_by_type": {
    "task.created": 500,
    "task.completed": 450
  },
  "pending_events": 10,
  "failed_events": 5
}
```

## Eventos del Propio Event Bus

### event.published

```json
{
  "type": "event.published",
  "payload": {
    "event_id": "event-5678",
    "event_type": "task.created",
    "source": "dispatcher"
  },
  "timestamp": "2026-08-04T12:00:00Z"
}
```

### event.consumed

```json
{
  "type": "event.consumed",
  "payload": {
    "event_id": "event-5678",
    "consumer_id": "planner",
    "duration_ms": 150
  },
  "timestamp": "2026-08-04T12:00:01Z"
}
```

### event.failed

```json
{
  "type": "event.failed",
  "payload": {
    "event_id": "event-5678",
    "consumer_id": "planner",
    "error": "Timeout",
    "attempt": 3
  },
  "timestamp": "2026-08-04T12:00:30Z"
}
```

## Testing

### Casos de Prueba

| ID | Descripción | Input | Output Esperado |
|----|-------------|-------|-----------------|
| TC-001 | Publicar evento válido | Event | Confirmación |
| TC-002 | Consumir evento | Suscripción | Evento entregado |
| TC-003 | Múltiples consumidores | Event + 2 suscripciones | 2 entregas |
| TC-004 | Consumer group | Event + group | Solo 1 entrega |
| TC-005 | Evento fallido reintento | Event + callback falla | 3 reintentos |
| TC-006 | Dead letter queue | Event + 3 fallos | En DLQ |
| TC-007 | Replay de eventos | Rango de tiempo | Eventos entregados |

### Casos Límite

- Evento sin tipo válido debe rechazarse
- Redis caído debe causar buffer local
- Consumer lento no debe bloquear otros
- Evento duplicado debe detectarse

## Observabilidad

### Logs

- `[EventBus] Evento publicado: type={type}, id={id}`
- `[EventBus] Evento consumido: type={type}, consumer={consumer}`
- `[EventBus] Evento fallido: type={type}, error={error}`
- `[EventBus] Dead letter: event_id={id}`

### Métricas

- `eventbus_published_total`
- `eventbus_consumed_total`
- `eventbus_failed_total`
- `eventbus_latency_seconds`
- `eventbus_queue_depth`
- `eventbus_dlq_depth`

## Constitution Check

### Principio I: Orquestación Única
- [x] Event Bus es infraestructura, no punto de entrada
- [x] Componentes se comunican a través de eventos

### Principio II: Separación Determinista vs LLM
- [x] Event Bus es 100% determinista
- [x] No usa LLM

### Principio III: Local-first
- [x] Redis es local
- [x] Eventos no salen del sistema

### Principio IV: Testing
- [x] Tests de publicación definidos
- [x] Tests de consumo definidos
- [x] Tests de reintentos definidos

### Principio V: Trazabilidad
- [x] Cada evento tiene ID único
- [x] Cada procesamiento se registra
- [x] Replay permite auditar

## Referencias

- Redis Streams documentation
- Event-driven architecture patterns
- Consumer groups patterns

## Cambios

| Versión | Fecha | Autor | Cambio |
|---------|-------|-------|--------|
| 1.0.0 | 2026-08-04 | Luis Daniel Guerrero Enciso | Versión inicial |
