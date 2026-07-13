# Cron Pipelines

## Daily Content Pipeline
- **Schedule**: `0 6 * * *` (diario 6:00 AM)
- **Workflow**: `flows/daily-content.json`
- **Triggered by**: n8n CRON
- **Description**: Genera contenido para todos los artistas activos del día

## Self-Improvement Pipeline
- **Schedule**: `0 12 * * 0` (domingo 12:00 PM)
- **Workflow**: `flows/self-improvement.json`
- **Triggered by**: n8n CRON
- **Description**: Evalúa prompts de la semana, identifica fallos, mejora templates

## Watchdog Pipeline
- **Schedule**: `*/5 * * * *` (cada 5 minutos)
- **Workflow**: `flows/watchdog.json`
- **Triggered by**: n8n CRON
- **Description**: Monitorea servicios, auto-repara si es posible, alerta si no

## On-Demand Pipelines
- **Onboarding Artist**: Webhook desde OpenCode command `/agregar-artista`
- **Generate Campaign**: Webhook desde OpenCode command `/generar-campaña`
