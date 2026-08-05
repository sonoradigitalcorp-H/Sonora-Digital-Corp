# Spec 001: Harvis Core

**ID**: 001-harvis-core
**Version**: 1.0.0
**Date**: 2026-08-04
**Author**: Luis Daniel Guerrero Enciso

## Resumen

Kernel del sistema operativo Harvis OS. Proporciona la base para todos los componentes del sistema.

## Objetivo

Establecer el núcleo compartido que todos los componentes de Harvis OS utilizarán para:
- Configuración centralizada
- Logging y observabilidad
- Gestión de estado
- Utilidades comunes

## Contexto

### Servicios Relacionados

| Servicio | Relación |
|----------|----------|
| Dispatcher | Usa Core para configuración |
| Planner | Usa Core para logging |
| Agents | Usa Core para contratos |
| Event Bus | Usa Core para tipos de eventos |

### Dependencias

- Python 3.11+
- Redis (cache y colas)
- PostgreSQL (estado persistente)
- pydantic (modelos de datos)

## Especificación

### Inputs

```python
# Configuración del sistema
class HarvisConfig:
    redis_url: str = "redis://localhost:6379"
    postgres_url: str = "postgresql://localhost/harvis"
    log_level: str = "INFO"
    mcp_timeout: int = 30000
    agent_registry_url: str = "http://localhost:8001"
```

### Outputs

```python
# Estado del sistema
class SystemStatus:
    version: str
    uptime: float
    agents_online: int
    tasks_processed: int
    last_health_check: datetime
```

### Comportamiento

1. Carga configuración desde variables de entorno o archivo
2. Inicializa conexiones a servicios dependientes
3. Expone utilidades comunes para logging, métricas y trazabilidad
4. Proporciona health check endpoint

### Reglas de Negocio

- La configuración SIEMPRE se carga desde variables de entorno primero
- Los defaults son seguros para desarrollo local
- El sistema MUST poder arrancar sin servicios externos (degraded mode)

### Contrato

```yaml
contract:
  input: HarvisConfig
  output: SystemStatus
  events_consume: []
  events_publish:
    - system.started
    - system.health_check
    - system.error
  tools_allowed:
    - config.get
    - config.set
    - health.check
```

## Componentes

### ConfigManager

- **Responsabilidad**: Carga y gestiona configuración
- **Inputs**: Variables de entorno, archivo config.yaml
- **Outputs**: Objeto HarvisConfig
- **Dependencias**: pydantic, pyyaml

### Logger

- **Responsabilidad**: Logging estructurado y trazabilidad
- **Inputs**: Mensajes, contexto, nivel
- **Outputs**: Logs escritos a stdout y archivo
- **Dependencias**: structlog

### MetricsCollector

- **Responsabilidad**: Recopila métricas del sistema
- **Inputs**: Eventos, mediciones
- **Outputs**: Métricas en formato Prometheus
- **Dependencias**: prometheus-client

### HealthChecker

- **Responsabilidad**: Verifica salud del sistema
- **Inputs**: Ping de servicios
- **Outputs**: Estado de cada servicio
- **Dependencias**: Todos los servicios

## API

### Health Check

```
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600,
  "services": {
    "redis": "connected",
    "postgres": "connected",
    "dispatcher": "online"
  }
}
```

### Metrics

```
GET /metrics
```

**Response**:
```
# HELP harvis_tasks_total Total tasks processed
# TYPE harvis_tasks_total counter
harvis_tasks_total{status="success"} 150
harvis_tasks_total{status="error"} 5
```

## Eventos

### system.started

```json
{
  "type": "system.started",
  "payload": {
    "version": "1.0.0",
    "config": "production"
  },
  "timestamp": "2026-08-04T12:00:00Z"
}
```

### system.health_check

```json
{
  "type": "system.health_check",
  "payload": {
    "status": "healthy",
    "services": {}
  },
  "timestamp": "2026-08-04T12:00:00Z"
}
```

## Testing

### Casos de Prueba

| ID | Descripción | Input | Output Esperado |
|----|-------------|-------|-----------------|
| TC-001 | Configuración por defecto | Sin variables | Config válida |
| TC-002 | Configuración desde env | Variables seteadas | Config con valores |
| TC-003 | Health check healthy | Todos los servicios OK | status=healthy |
| TC-004 | Health check degraded | Redis caído | status=degraded |

### Casos Límite

- Configuración inválida debe lanzar error claro
- Servicios no disponibles deben reportarse como degraded, no crash
- Logs no deben contener secrets

## Observabilidad

### Logs

- `[HarvisCore] Sistema iniciado: version={version}`
- `[HarvisCore] Health check: status={status}`
- `[HarvisCore] Error en configuración: {error}`

### Métricas

- `harvis_uptime_seconds`
- `harvis_tasks_total`
- `harvis_errors_total`
- `harvis_service_status`

## Constitution Check

### Principio I: Orquestación Única
- [x] Core no es punto de entrada; es infraestructura compartida
- [x] No comunica directamente con usuarios

### Principio II: Separación Determinista vs LLM
- [x] Toda la lógica de Core es determinista
- [x] No usa LLM

### Principio III: Local-first
- [x] Configuración local
- [x] Datos locales

### Principio IV: Testing
- [x] Tests de configuración
- [x] Tests de health check
- [x] Tests de logging

### Principio V: Trazabilidad
- [x] Cada evento se registra
- [x] Health checks son auditables

## Referencias

- structlog documentation
- prometheus-client documentation
- Pydantic documentation

## Cambios

| Versión | Fecha | Autor | Cambio |
|---------|-------|-------|--------|
| 1.0.0 | 2026-08-04 | Luis Daniel Guerrero Enciso | Versión inicial |
