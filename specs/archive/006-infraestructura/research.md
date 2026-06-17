# Research: Infraestructura y Seguridad
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| Docker Compose | Aislamiento, reproducible, 4 servicios | Overhead de recursos | ✅ Orquestación principal |
| Systemd | Init nativo, restart automático | Config manual | ✅ Gestión de procesos |
| UFW | Simple, efectivo | Limitado vs iptables | ✅ Firewall |
## Decisión Arquitectónica
- **Selección**: Docker (servicios) + Systemd (procesos) + Localhost-only + UFW
- **Motivo**: Seguridad por defecto, todos los servicios en localhost
## Limitaciones
1. Sin Redis, el cacheo es in-memory
2. Sin autenticación multi-factor
