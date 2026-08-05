# Spec 004: Agent Registry

**ID**: 004-agent-registry
**Version**: 1.0.0
**Date**: 2026-08-04
**Author**: Luis Daniel Guerrero Enciso

## Resumen

Catálogo centralizado de todos los agentes disponibles en el sistema Harvis OS.

## Objetivo

Proporcionar un registro único que:
- Conozca todos los agentes disponibles
- Conozca las capacidades de cada agente
- Gestione el estado de los agentes
- Proporcione contratos para integración
- Soporte health checks de agentes

## Contexto

### Servicios Relacionados

| Servicio | Relación |
|----------|----------|
| Dispatcher | Consulta agente disponible |
| Planner | Consulta capacidades |
| Agents | Se registran y reportan estado |
| Event Bus | Escucha eventos de agentes |

### Dependencias

- PostgreSQL (almacenamiento de registros)
- Redis (cache de estado)
- Event Bus (eventos de salud)

## Especificación

### Inputs

```python
# Registro de un agente
class AgentRegistration:
    id: str
    name: str
    description: str
    capabilities: List[str]  # ["code", "git", "test", "deploy"]
    tools_allowed: List[str]  # ["filesystem", "terminal", "browser"]
    max_concurrent: int = 1
    health_endpoint: Optional[str] = None
    metadata: dict = {}
```

### Outputs

```python
# Información completa de un agente
class AgentInfo:
    id: str
    name: str
    description: str
    capabilities: List[str]
    tools_allowed: List[str]
    status: str  # "online", "offline", "busy", "error"
    max_concurrent: int
    current_load: int
    available: bool
    last_health_check: Optional[datetime]
    health_endpoint: Optional[str]
    metadata: dict

# Contrato de integración
class AgentContract:
    agent_id: str
    input_schema: dict  # JSON Schema
    output_schema: dict  # JSON Schema
    events_consume: List[str]
    events_publish: List[str]
    timeout: int
    retry_policy: dict
```

### Comportamiento

1. Agentes se registran al iniciar
2. Registry mantiene estado actualizado
3. Health checks periódicos verifican salud
4. Dispatcher consulta disponibilidad
5. Planner consulta capacidades

### Reglas de Negocio

**Registro Automático**:

```yaml
agents:
  openhands:
    name: "OpenHands"
    description: "Agente autónomo para código, debugging y deploy"
    capabilities:
      - code
      - debug
      - test
      - deploy
      - browser
      - terminal
    tools_allowed:
      - filesystem
      - terminal
      - browser
      - git
    max_concurrent: 2
    health_endpoint: "http://localhost:3000/health"
    timeout: 600
    retry_policy:
      max_retries: 3
      backoff: exponential

  opencode:
    name: "OpenCode"
    description: "IDE interactivo para desarrollo"
    capabilities:
      - code
      - edit
      - refactor
    tools_allowed:
      - filesystem
      - terminal
      - lsp
    max_concurrent: 1
    health_endpoint: "http://localhost:3001/health"
    timeout: 300
    retry_policy:
      max_retries: 2
      backoff: linear

  hermes:
    name: "Hermes"
    description: "Orquestador MCP para integraciones"
    capabilities:
      - mcp
      - integration
      - workflow
    tools_allowed:
      - mcp
      - api
    max_concurrent: 3
    health_endpoint: "http://localhost:3002/health"
    timeout: 120
    retry_policy:
      max_retries: 2
      backoff: linear

  aider:
    name: "Aider"
    description: "Especialista en Git y cambios múltiples"
    capabilities:
      - git
      - commit
      - changelog
      - multi-file
    tools_allowed:
      - filesystem
      - terminal
      - git
    max_concurrent: 1
    health_endpoint: null
    timeout: 300
    retry_policy:
      max_retries: 2
      backoff: linear
```

**Detección de Disponibilidad**:
- Un agente está disponible si: `status == "online" AND current_load < max_concurrent`
- Si el health check falla, el agente se marca como "offline"
- Si el agente está busy, la tarea se encola

### Contrato

```yaml
contract:
  input: AgentRegistration
  output: AgentInfo
  events_consume:
    - agent.heartbeat
    - agent.registered
    - agent.deregistered
  events_publish:
    - agent.status_changed
    - agent.health_check_failed
  tools_allowed:
    - database.query
    - database.insert
    - database.update
    - cache.get
    - cache.set
    - event_bus.publish
```

## Componentes

### RegistryStore

- **Responsabilidad**: Almacena y recupera registros de agentes
- **Inputs**: AgentRegistration
- **Outputs**: AgentInfo
- **Dependencias**: PostgreSQL

### HealthMonitor

- **Responsabilidad**: Verifica salud de agentes periódicamente
- **Inputs**: Health endpoints
- **Outputs**: Estado actualizado
- **Dependencias**: httpx

### CapabilityMatcher

- **Responsabilidad**: Encuentra agentes con capacidades requeridas
- **Inputs**: Lista de capacidades requeridas
- **Outputs**: Lista de agentes disponibles
- **Dependencias**: RegistryStore

### LoadBalancer

- **Responsabilidad**: Distribuye carga entre agentes disponibles
- **Inputs**: Tarea a asignar
- **Outputs**: Agente seleccionado
- **Dependencias**: CapabilityMatcher

## API

### Registrar Agente

```
POST /api/v1/agents
```

**Request**:
```json
{
  "id": "openhands",
  "name": "OpenHands",
  "capabilities": ["code", "debug", "test"],
  "tools_allowed": ["filesystem", "terminal"],
  "max_concurrent": 2
}
```

**Response**:
```json
{
  "id": "openhands",
  "status": "registered",
  "registered_at": "2026-08-04T12:00:00Z"
}
```

### Consultar Agente

```
GET /api/v1/agents/{agent_id}
```

**Response**:
```json
{
  "id": "openhands",
  "name": "OpenHands",
  "status": "online",
  "current_load": 1,
  "available": true,
  "capabilities": ["code", "debug", "test"]
}
```

### Listar Agentes Disponibles

```
GET /api/v1/agents?capability=code&status=online
```

**Response**:
```json
{
  "agents": [
    {
      "id": "openhands",
      "name": "OpenHands",
      "status": "online",
      "current_load": 1,
      "max_concurrent": 2,
      "available": true
    }
  ]
}
```

### Health Check

```
GET /api/v1/agents/{agent_id}/health
```

**Response**:
```json
{
  "agent_id": "openhands",
  "status": "healthy",
  "uptime": 3600,
  "last_check": "2026-08-04T12:00:00Z"
}
```

## Eventos

### agent.registered

```json
{
  "type": "agent.registered",
  "payload": {
    "agent_id": "openhands",
    "capabilities": ["code", "debug"]
  },
  "timestamp": "2026-08-04T12:00:00Z"
}
```

### agent.status_changed

```json
{
  "type": "agent.status_changed",
  "payload": {
    "agent_id": "openhands",
    "old_status": "online",
    "new_status": "busy"
  },
  "timestamp": "2026-08-04T12:05:00Z"
}
```

### agent.health_check_failed

```json
{
  "type": "agent.health_check_failed",
  "payload": {
    "agent_id": "openhands",
    "error": "Connection refused",
    "consecutive_failures": 3
  },
  "timestamp": "2026-08-04T12:10:00Z"
}
```

## Testing

### Casos de Prueba

| ID | Descripción | Input | Output Esperado |
|----|-------------|-------|-----------------|
| TC-001 | Registrar agente | AgentRegistration | AgentInfo registrado |
| TC-002 | Consultar agente existente | agent_id | AgentInfo completa |
| TC-003 | Consultar agente inexistente | agent_id | 404 Not Found |
| TC-004 | Listar por capacidad | capability=code | Lista de agentes |
| TC-005 | Health check exitoso | agent_id | status=healthy |
| TC-006 | Health check fallido | agent_id | status=offline |
| TC-007 | Agente llena capacidad | agent available=false | No se asigna |

### Casos Límite

- Dos agentes con mismo ID debe rechazarse
- Agente sin health endpoint debe manejarse
- Health check timeout debe marcar agente offline
- Load balancing round-robin debe ser justo

## Observabilidad

### Logs

- `[Registry] Agente registrado: id={agent_id}`
- `[Registry] Estado cambiado: agent={agent_id}, status={status}`
- `[Registry] Health check fallido: agent={agent_id}, error={error}`
- `[Registry] Agente offline: agent={agent_id}`

### Métricas

- `registry_agents_total`
- `registry_agents_online_total`
- `registry_health_checks_total`
- `registry_health_check_failures_total`
- `registry_agent_load`

## Constitution Check

### Principio I: Orquestación Única
- [x] Registry es infraestructura, no punto de entrada
- [x] Dispatcher y Planner consultan Registry

### Principio II: Separación Determinista vs LLM
- [x] Registro es determinista
- [x] Health checks son deterministas
- [x] No usa LLM

### Principio III: Local-first
- [x] Datos locales en PostgreSQL
- [x] Health checks locales

### Principio IV: Testing
- [x] Tests de registro definidos
- [x] Tests de health check definidos
- [x] Tests de load balancing definidos

### Principio V: Trazabilidad
- [x] Cada registro tiene timestamp
- [x] Cambios de estado se registran
- [x] Health checks son auditables

## Referencias

- Service Registry patterns
- Health check patterns
- Load balancing algorithms

## Cambios

| Versión | Fecha | Autor | Cambio |
|---------|-------|-------|--------|
| 1.0.0 | 2026-08-04 | Luis Daniel Guerrero Enciso | Versión inicial |
