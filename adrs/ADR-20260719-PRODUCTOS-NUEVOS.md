# ADR — Productos Nuevos: Notifier, Order Tracker, Affiliates

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260719-PRODUCTOS-NUEVOS` |
| **Fecha** | 2026-07-19 |
| **Spec** | SPEC-20260719-UNIFICACION (FR-01..FR-09) |
| **Estado** | activo |

## Contexto
Durante la Fase 1 de WhatsApp OS se identificaron 3 vacíos estratégicos: no existía un motor de notificaciones, no había rastreo de entregas de servicios, y no había portal de afiliados. Se decidió crear 3 productos completos para llenar estos vacíos.

## Decisión
1. **Notifier**: API + worker que lee eventos del bus y entrega notificaciones via WhatsApp, Telegram, Email según reglas configurables. Puerto :6200.
2. **Order Tracker**: API + WebSocket que rastrea servicios en estados queued→processing→completed→delivered. Puerto :6300.
3. **Affiliates**: API con referidos (REF-XXXXXX), comisiones tokens/MXN, pagos, leaderboard. Puerto :6400.

## Opciones Consideradas
| Opción | Pros | Contras |
|--------|------|---------|
| **Productos separados (elegido)** | Independientes, cada uno con su ciclo de vida | 3 puertos, 3 APIs |
| Producto monolítico unificado | Una sola API | Acoplamiento, difícil de escalar |
| Extender sonora_engine | Sin nuevos servicios | Mezcla lógica de dominios distintos |

## Consecuencias
- Positivas: 43 tests nuevos, cada producto con FastAPI + tests
- Positivas: Registrados en `products/registry.yaml` con features y precios
- Pendiente: Integrar con notifier rules para delivery alerts

## Lecciones
- Directorios con guión (`order-tracker`) no son importables en Python
- FastAPI requiere ordenar rutas específicas antes de wildcards `/{id}`
