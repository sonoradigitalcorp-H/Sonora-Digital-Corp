# Research: Branding y Alma
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| Soul Prompt en system prompt | Visible al LLM, control de identidad | Solo texto | ✅ Prompt principal |
| Mystic Agent en opencode | Configuración, permisos, identidad | Solo CLI | ✅ Config de agente |
| Telegram Bot con alma | Interacción directa con usuarios | Límite de mensajes | ✅ Bot de Mystic |
## Decisión Arquitectónica
- **Selección**: System prompt + opencode agent + Telegram bot tríada de identidad
- **Motivo**: La identidad debe ser consistente en todos los canales
## Limitaciones
1. El prompt se pierde si el LLM no lo respeta
2. No hay verificación de consistencia de identidad entre canales
