# Orchestrator

Coordina la comunicación entre agentes y la ejecución de pipelines.

## Componentes

- **Redis pub/sub**: Comunicación en tiempo real entre agentes
- **n8n workflows**: Pipelines programados (CRON) y bajo demanda
- **Systemd timers**: Pipelines críticos del sistema

## Canales Redis

Ver `redis-channels.md` para la lista completa.

## Pipelines programados

Ver `cron-pipelines.md` para horarios y descripciones.
