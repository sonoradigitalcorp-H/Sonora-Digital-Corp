# Tasks — Zamora Evolution

---

## Fase 1: Fundación de Automatización

### T1.1 Conectar Zamora con n8n
**FR**: FR1
**Archivos**: `mcp/tools/zamora.js`, `infra/n8n/zamora-lead-workflow.json`
**Verificación**: POST a booking endpoint → lead en n8n → WhatsApp confirmation
**Detalle**:
- Crear workflow n8n `zamora-lead-capture` con webhook trigger
- Workflow: Webhook → Format Lead → WhatsApp Send (Evolution API) → Telegram Notify → Store in JSON
- Añadir MCP tool `zamora_lead_capture` en `zamora.js`
- Endpoint POST `/api/zamora/booking` en `zamora_router.py`

### T1.2 Implementar captura de leads
**FR**: FR1
**Archivos**: `apps/webui/routes/zamora_router.py`, `apps/jarvis/src/core/zamora.py`
**Verificación**: Lead creado → persistido → notificación enviada
**Detalle**:
- Añadir método `capture_lead()` en `ZamoraStudio`
- Añadir endpoint `POST /api/zamora/booking` que valida datos, crea lead, trigger n8n
- Añadir modelo `Lead` como dataclass frozen

### T1.3 Conectar Engram + Neo4j para memoria de clientes
**FR**: FR7
**Archivos**: `apps/jarvis/src/core/zamora.py`
**Verificación**: Cliente consultado → historial recuperado desde Neo4j
**Detalle**:
- Añadir dependencia de `Engram` y `Neo4jStore` en `ZamoraStudio`
- En `capture_lead()`: guardar en Engram + Neo4j
- Añadir método `get_client_history(client_id)` que consulta Neo4j

---

## Fase 2: Agente IA + Pagos

### T2.1 Configurar Hermes agent para Zamora
**FR**: FR2
**Archivos**: `.hermes/config.yaml`, `mcp/tools/zamora.js`
**Verificación**: Mensaje WhatsApp → Hermes → respuesta con datos de Zamora
**Detalle**:
- Registrar skill de Zamora en Hermes (system prompt con servicios, pricing)
- Añadir MCP tools: `zamora_agent_chat`, `zamora_agent_status`
- Configurar webhook de WhatsApp para rutear a Hermes

### T2.2 Implementar pagos recurrentes con Stripe
**FR**: FR5
**Archivos**: `apps/webui/routes/zamora_router.py`, `data/zamora-payments.json`
**Verificación**: Checkout Stripe → pago exitoso → plan activo → webhook confirmación
**Detalle**:
- Añadir endpoint `POST /api/zamora/create-checkout-session`
- Añadir endpoint `POST /api/zamora/webhook` (Stripe webhook)
- Añadir método `create_subscription(plan_name, customer_email)` en `ZamoraStudio`
- Persistir suscripciones en `data/zamora-payments.json`

### T2.3 Implementar Mercado Pago como fallback
**FR**: FR5
**Archivos**: `apps/webui/routes/zamora_router.py`
**Verificación**: Checkout MP → pago exitoso → plan activo
**Detalle**:
- Similar a T2.2 pero con SDK de Mercado Pago
- Endpoint `POST /api/zamora/mp-create-preference`
- Endpoint `POST /api/zamora/mp-webhook`

---

## Fase 3: Dashboard Cliente + Admin

### T3.1 Sistema de autenticación para clientes
**FR**: FR3
**Archivos**: `apps/webui/routes/zamora_router.py`
**Verificación**: Login con email + código → sesión JWT válida
**Detalle**:
- Login sin password: enviar código por email/WhatsApp
- JWT token con expiración
- Middleware de autenticación

### T3.2 Dashboard de cliente
**FR**: FR3
**Archivos**: `apps/webui/static/zamora-dashboard.html`
**Verificación**: Cliente autenticado ve su plan, entregables, métricas
**Detalle**:
- Página HTML con: plan activo, progreso de entregables, historial de pagos
- Fetch a `/api/zamora/client/{id}/dashboard`
- Diseño Apple-style consistente con zamora-system.html

### T3.3 Panel admin con KPIs
**FR**: FR6
**Archivos**: `apps/webui/static/zamora-admin.html`
**Verificación**: Admin autenticado ve leads, revenue, conversiones
**Detalle**:
- Tabla de leads con estado (nuevo/contactado/calificado/cliente)
- Revenue total + revenue por plan
- Tasa de conversión lead → cliente
- Contenido generado (fotos/videos)

---

## Fase 4: Contenido Automatizado

### T4.1 Workflow n8n de contenido visual
**FR**: FR4
**Archivos**: `infra/n8n/zamora-content-workflow.json`
**Verificación**: Trigger → imagen generada con FLUX → entregada
**Detalle**:
- Workflow n8n: Cron semanal → media_image (FLUX) → guardar → notificar
- Usar MCP tool `media_image` ya existente

### T4.2 Landing dinámica con datos en vivo
**FR**: FR8
**Archivos**: `apps/webui/static/zamora-system.html`
**Verificación**: Landing muestra portfolio real, servicios desde API, testimoniales dinámicos
**Detalle**:
- Mejorar skeleton loading con transiciones suaves
- Portfolio real desde API (empty state actual → contenido cuando exista)
- Testimonios desde API admin

---

## Fase 5: Pull-Requests y Despliegue

### T5.1 Commit + Push
**Verificación**: `git status` limpio, `git log` muestra commits
**Detalle**:
- Commits atómicos por fase
- Push a `main`

### T5.2 Sync a VPS
**Verificación**: Servicios recargados, endpoints responden
**Detalle**:
- `scripts/sync-to-vps.sh` o rsync manual
- Verificar health endpoints
