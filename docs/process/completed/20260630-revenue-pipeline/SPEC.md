# SPEC — Revenue Pipeline: Sales Agent Automation

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260630-002` |
| **Fecha** | 2026-06-30 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Automatizar el pipeline de ventas completo: desde que un lead llega hasta que es cliente onboardeado, sin intervención humana en el medio.

---

## 2. Value Driver

revenue, automation, founder-independence

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Sales pipeline model con stages: lead → qualified → proposal → negotiation → won/lost |
| FR2 | Captura automática de leads desde Telegram bot, web forms, y n8n webhooks |
| FR3 | Lead scoring automático basado en nicho, plan potencial, y fuente |
| FR4 | Generación automática de propuestas con productos del catálogo |
| FR5 | Integración con pagos existentes (Mercado Pago, Bitso, SPEI) |
| FR6 | Onboarding automático al recibir pago (crear customer en Neo4j, emitir eventos) |
| FR7 | Dashboard de pipeline: leads en cada stage, revenue potencial, conversion rate |
| FR8 | Eventos emitidos para score, Engram, gamificación (primer_lead, primera_venta) |

---

## 4. Success Criteria

- [ ] Un lead puede entrar por Telegram y llegar a cliente sin intervención humana
- [ ] Lead scoring funciona con datos reales (nicho, fuente, plan)
- [ ] Propuesta generada automáticamente incluye planes y precios correctos
- [ ] Pago procesado vía MP/Bitso/SPEI gatilla onboarding automático
- [ ] Neo4j se actualiza con customer y su pipeline history
- [ ] Dashboard muestra pipelines activos
- [ ] Enterprise Score sube al menos 10 puntos (37 → 47+)

---

## 5. Gherkin Scenarios

Ver `process/active/gherkin/SPEC-20260630-002.feature`

---

## 6. Edge Cases

- [EC1] Lead que ya existe en Neo4j (update vs duplicate)
- [EC2] Pago rechazado después de propuesta enviada
- [EC3] Lead que desaparece (no responde) — timeout y lost
- [EC4] Múltiples fuentes para el mismo lead (Telegram + web form)
- [EC5] Producto sin precio definido

---

## 7. Technical Approach

Crear un nuevo módulo `apps/jarvis/src/core/sales_pipeline.py` con:

- `SalesPipeline` class — Neo4j-backed pipeline model con stages
- `LeadScorer` — scoring por nicho, fuente, plan
- `ProposalGenerator` — genera propuestas desde product catalog
- `SalesAgent` — agente del orquestador que maneja el ciclo completo

Integrar con:
- `apps/webui/routes/` — endpoints para dashboard y captura de leads
- `platforms/telegram/` — comando /vender o /cotizar
- Infraestructura de eventos existente (events.jsonl)
- `payments.py` — reutilizar PaymentOrchestrator
- `sdc_business.py` — reutilizar SDCCustomer, SDCOnboarding
- `gamification.py` — emitir eventos para badges
- `engram.py` — store_learning() al completar cada venta

---

## 8. Dependencies

- Neo4j running (Docker)
- Mercado Pago credentials in .env
- Telegram bot running
- n8n (opcional para webhooks)

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `lead_received` | Nuevo lead capturado |
| `lead_qualified` | Lead supera score threshold |
| `proposal_generated` | Propuesta enviada al lead |
| `proposal_accepted` | Lead acepta propuesta |
| `payment_received` | Pago confirmado |
| `customer_onboarded` | Customer creado en Neo4j |
| `deal_won` | Pipeline completado exitosamente |
| `deal_lost` | Pipeline cerrado sin venta |

---

## 10. Kill Criteria

Si después de 2 semanas no hay al menos 1 lead real capturado automáticamente, abortar y repensar integración.

---

## 11. Scale Criteria

Cuando el pipeline maneje >50 leads/mes, agregar: lead nurturing automático, A/B testing de propuestas, forecasting.
