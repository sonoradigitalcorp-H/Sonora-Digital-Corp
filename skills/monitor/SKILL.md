---
name: monitor
description: System health monitoring, auto-repair, and alerts via Prometheus + Grafana. Use for checking system status, health, or incidents.
version: 1.0.0
updated: 2026-07-13
---

# Monitor Skill

System monitoring, auto-repair, and alerting via Prometheus + Grafana + Engram.

## Tools que usa
- `hasura_query` — verificar servicios
- `engram_save` — registrar incidentes
- `engram_search` — historial de incidentes

## Pipeline (cada 5 min)
1. Verificar health de cada endpoint
2. Si alguno falla → intentar restart
3. Registrar en Engram
4. Si 3 intentos fallan → alerta

## Ejemplo
```
Status del sistema y últimas alertas
```
