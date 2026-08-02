# SPEC — Zamora Evolution: De Landing Estática a Producto Automatizado

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260709-ZAMORA-EVO` |
| **Fecha** | 2026-07-09 |
| **Autor** | Mystic / SDD Pipeline |
| **Tier** | 3 |
| **Estado** | borrador |
| **Score requerido** | >=75 |

---

## 1. Objetivo

Evolucionar Alejandro Zamora Brand Studio de una landing page estática con API CRUD a un producto automatizado con pipeline de leads, agente IA, dashboard de cliente, integración WhatsApp, y contenido generado por IA — conectado al ecosistema SDC (n8n, MCP, Hermes, Engram).

---

## 2. Value Driver

**Revenue**: Convertir visitantes en clientes via automatización de leads + follow-up
**Automation**: Eliminar trabajo manual de atención, contenido y seguimiento
**Founder-Independence**: El sistema opera 24/7 sin intervención de Alejandro

---

## 3. Functional Requirements

| FR# | Descripción | Prioridad |
|-----|-------------|-----------|
| FR1 | Pipeline de captura de leads: booking form → n8n → WhatsApp/Email → CRM | Alta |
| FR2 | Agente IA real conectado vía Hermes Gateway que atiende clientes 24/7 en WhatsApp/Web | Alta |
| FR3 | Dashboard de cliente con login: progreso, entregables, métricas | Alta |
| FR4 | Generación automatizada de contenido visual (fotos/videos) usando media.js | Media |
| FR5 | Portal de pagos recurrente conectado a Stripe/Mercado Pago para los 3 planes | Alta |
| FR6 | Panel admin con KPIs: leads, conversiones, revenue, contenido generado | Media |
| FR7 | Memoria entre sesiones vía Engram + Neo4j para seguimiento de clientes | Media |
| FR8 | Landing page dinámica con datos en vivo desde API y portfolio real | Baja |
| FR9 | Automatización de contenido en redes sociales vía viral-engine.js | Baja |
| FR10 | Notificaciones automáticas al dueño sobre leads nuevos, pagos, hitos | Media |

---

## 4. Success Criteria

- [ ] Lead capture → n8n workflow responde en < 30s con confirmación WhatsApp
- [ ] Agente IA puede responder preguntas sobre servicios/precios y agendar llamada
- [ ] Cliente puede login y ver su progreso en dashboard
- [ ] Pagos recurrentes funcionales con Stripe para plan Conquistador
- [ ] Admin panel muestra leads, revenue, conversiones actualizados en tiempo real
- [ ] Contenido visual generado automáticamente para redes

---

## 5. Gherkin Scenarios

Ver `gherkin/SPEC-20260709-ZAMORA-EVO.feature`

---

## 6. Edge Cases

- [EC1] Lead duplicado: mismo email/celular → actualizar lead existente, no duplicar
- [EC2] Pago fallido: notificar al cliente + reintentar 3 veces antes de cancelar plan
- [EC3] Agente IA sin contexto: si Engram no responde, fallback a respuestas genéricas
- [EC4] WhatsApp token expira: alertar al admin + pausar notificaciones
- [EC5] Cliente cancela plan: degradar a plan gratuito, mantener datos 30 días

---

## 7. Technical Approach

### Arquitectura

```
Landing (zamora-system.html)
       │
       ▼
FastAPI Router (/api/zamora/*)
       │
       ├──► n8n Workflow (lead → WhatsApp → CRM)
       ├──► Hermes Gateway (agente IA 24/7)
       ├──► Stripe/Mercado Pago (pagos recurrentes)
       ├──► MCP Tools (media.js, viral-engine.js, content-engine.js)
       └──► Engram + Neo4j (memoria de clientes)
```

### Archivos a crear/modificar

| Archivo | Acción | FR |
|---------|--------|----|
| `mcp/tools/zamora.js` | Modificar: añadir tools de lead management, agente, pagos | FR1, FR2, FR5 |
| `apps/webui/routes/zamora_router.py` | Modificar: endpoints para booking, login, dashboard | FR1, FR3, FR6 |
| `apps/jarvis/src/core/zamora.py` | Modificar: conectar a Engram, Neo4j, n8n | FR1, FR7 |
| `apps/webui/static/zamora-system.html` | Modificar: login, dashboard cliente, estado en vivo | FR3, FR8 |
| `infra/n8n/zamora-lead-workflow.json` | Crear: workflow de captura de leads | FR1 |
| `infra/n8n/zamora-content-workflow.json` | Crear: workflow de contenido automatizado | FR4 |
| `data/zamora-payments.json` | Crear: registro de pagos/suscripciones | FR5 |
| `process/active/SPEC-20260709-ZAMORA-EVO/` | Crear: SDD artifacts | — |

### Stack

- n8n (ya corriendo en Docker, 33 workflows)
- Hermes Gateway (:8643) para agente IA vía Telegram/WhatsApp
- MCP Gateway (:8000) para tools de contenido/media
- Engram + Neo4j para memoria persistente
- Stripe API + Mercado Pago API para pagos
- WebSocket para dashboard en vivo

---

## 8. Dependencies

- n8n corriendo en `sdc-prod:5678` (OK, ya activo)
- Hermes Gateway operativo (OK, ya activo)
- Stripe account keys en `.env`
- Mercado Pago access token en `.env`
- WhatsApp Business API token (Evolution API)
- Neo4j contenedor corriendo (OK, ya activo)
- Engram pipeline funcional

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `zamora.lead.captured` | Nuevo lead desde booking form |
| `zamora.lead.qualified` | Lead calificado como cliente potencial |
| `zamora.payment.completed` | Pago recurrente exitoso |
| `zamora.payment.failed` | Pago recurrente fallido |
| `zamora.content.generated` | Contenido visual generado automáticamente |
| `zamora.agent.engaged` | Usuario interactúa con agente IA |
| `zamora.plan.changed` | Cliente cambia de plan |

---

## 10. Kill Criteria

- Si n8n no está accesible después de 3 intentos de conexión
- Si Stripe/Mercado Pago no pueden configurarse por falta de API keys
- Si el agente IA tiene latencia > 10s en respuestas

---

## 11. Scale Criteria

- Cuando se superen 100 leads/mes → migrar a bases dedicadas
- Cuando el agente IA tenga > 1000 conversaciones/mes → considerar fine-tuning
- Cuando el revenue mensual supere $5,000 MXN → contratar hosting dedicado
