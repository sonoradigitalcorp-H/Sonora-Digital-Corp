# Research: SDC Business Layer
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| Mercado Pago | Líder LatAm, SPEI, OXXO, suscripciones | Fees por transacción | ✅ Pagos principales |
| Stripe | Internacional, API excelente | No optimizado para México | ⏸️ Alternativa |
| Bitso + SPEI | Crypto + transferencias, bajos fees | Volumen bajo | ⏸️ Complemento |
## Decisión Arquitectónica
- **Selección**: Mercado Pago (principal) + Bitso/SPEI (alternativo) + Stripe (futuro)
- **Motivo**: Optimizado para clientes México/LatAm
## Limitaciones
1. Sin webhook de Mercado Pago en producción aún
2. Precios en MXN fijos — sin conversión automática
