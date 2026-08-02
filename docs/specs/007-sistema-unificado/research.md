# Research: Sistema Unificado
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| Unified Bridge propio | Control total, 3 bridges (Hermes, OpenClaw, GBrain) | Código propio | ✅ Seleccionado |
| Hermes Agent | Multi-canal, gateway, 86 tools, 29 providers | Dependencia externa | ✅ Gateway de mensajería |
| OpenClaw Gateway | 40+ skills, comunidad, SKILL.md standard | Gateway local | ✅ Gateway de skills |
## Decisión Arquitectónica
- **Selección**: 3 bridges independientes + Human-in-the-Loop para acciones críticas
- **Motivo**: Separación clara de responsabilidades, cada bridge es reemplazable
## Limitaciones
1. Bridges son síncronos — operaciones lentas bloquean
2. Sin cola de mensajes persistente
