# Research: Mysticverse
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| DigitalTwinPipeline propio | Control total, face/voice/personality | Desarrollo interno | ✅ Pipeline propio |
| Fal.ai | Generación imágenes/video, API simple | Costo por uso | ✅ Imagen + video |
| Telegram Bot API | Gratis, bots, webhooks | Límite 32KB mensajes | ✅ Bot de ventas |
## Decisión Arquitectónica
- **Selección**: Pipeline propio + Fal.ai + Telegram Bot + KYC manual
- **Motivo**: Nicho adulto requiere control total de datos e identidad
## Limitaciones
1. Face training requiere muestras de video de alta calidad
2. KYC es semi-automático — revisión humana necesaria
