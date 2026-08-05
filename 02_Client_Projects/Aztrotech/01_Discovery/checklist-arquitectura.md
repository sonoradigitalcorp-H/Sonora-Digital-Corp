# Checklist Arquitectura — AstroTech / SDC

## Estado actual de MCPs

### ✅ Ya activos
| MCP | Puerto | Tenant | Estado |
|---|---|---|---|
| OpenClaw Gateway | 18789 | astrotech | ✅ Activo |
| Sonora MCP Gateway | 18989 | astrotech | ✅ Activo |
| Hermes Gateway | 8000/sse | astrotech | ✅ Activo |
| PostgreSQL | 5432 | global | ✅ Docker |
| Redis | 6379 | global | ✅ Docker |
| Neo4j | 7687 | global | ✅ Docker |
| Qdrant | 6333 | global | ✅ Docker |
| n8n | 5678 | global | ✅ Docker |
| Twilio Voice Bridge | 8700 | astrotech | ✅ Código listo |
| FreeSWITCH (Telnyx) | 5060 | global | ✅ Setup listo |
| 22 MCPs en Hermes | — | global | ✅ fetch, git, github, postgres, redis, etc. |

### ❌ Pendientes de implementar
| MCP/Servicio | Prioridad | Documento referencia |
|---|---|---|
| Agent Control MCP | 🔴 Alta | `agent-control-mcp.yaml` |
| Evolution Engine MCP | 🔴 Alta | `evolution-mcp.yaml` |
| Infra MCP | 🔴 Alta | `infra-mystic-mcp.yaml` |
| Twilio → Tenant Routing | 🔴 Alta | `pipeline_voz.feature` |
| CRM MCP (astrotech_crm) | 🟡 Media | `tenants/astrotech/mcp.yaml` |
| Calendar Google (creds) | 🟡 Media | `tenants/astrotech/mcp.yaml` |
| Scraper MCP (inteligencia prospecto) | 🟡 Media | `openclaw_integration.yaml` |

---

## Checklist completo desde documentos

### 1. 🔴 INFRAESTRUCTURA BASE
- [x] VPS OVH activo (149.56.46.173)
- [x] Docker compose con PostgreSQL, Redis, Neo4j, Qdrant, n8n
- [x] OpenClaw Gateway corriendo (:18789)
- [x] Hermes Gateway corriendo (:8000/sse)
- [x] Credenciales Twilio en `.env`
- [x] FreeSWITCH + Telnyx SIP trunk configurado
- [ ] Conectar Twilio Voice Bridge con tenant_id routing
- [ ] Configurar nginx reverse proxy para twilio-voice
- [ ] Certificar SSL para webhooks Twilio

### 2. 🔴 SISTEMA MULTI-TENANT
- [x] Registry.yaml con tenants registrados (astrotech, abe-music, etc.)
- [x] Template de tenant (`config/tenants/_template/`)
- [ ] Auto-creación de tenant al registrarse cliente nuevo
- [ ] PostgreSQL RLS por tenant_id en todas las tablas
- [ ] Redis keys con prefijo `tenant:{uuid}:`
- [ ] Qdrant collections separadas por tenant
- [ ] Neo4j databases separadas por tenant
- [ ] Voice clone storage separado por tenant
- [ ] Rate limiting por paquete (Despertar/Elevar/Soberano/Oráculo)

### 3. 🔴 PIPELINE DE VOZ (Twilio + FreeSWITCH)
- [x] Twilio Voice Bridge server (`apps/twilio-voice/server.py`)
- [x] FreeSWITCH setup con Telnyx
- [ ] Twilio webhook apuntando al VPS (ngrok/SSL)
- [ ] Enrutamiento de llamadas por tenant_id
- [ ] Inbound: FreeSWITCH → Whisper STT → LLM → Kokoro TTS → FreeSWITCH
- [ ] Outbound: campaign trigger → FreeSWITCH → llamar → pipeline
- [ ] Detección de tono (urgencia, enojo, feliz)
- [ ] Reconocimiento de cliente recurrente (desviación de tono)
- [ ] Latencia objetivo: <2.5s total pipeline

### 4. 🔴 CRM + LEADS + CAMPANAS
- [x] CRM skill con capability.yaml + handler
- [ ] Integrar Twilio con CRM (crear lead al recibir llamada)
- [ ] Scoring BANT automático post-llamada
- [ ] Embudo cold → warm → hot
- [ ] Campañas outbound para cold/warm leads
- [ ] Campaña de adopción (primera semana post-onboarding)
- [ ] Campaña de educación tecnológica (semana 1-2)
- [ ] Notificación a César: lead calificado
- [ ] Conversación fluida: audio first, texto fallback

### 5. 🔴 AGENT CONTROL MCP
- [ ] `restart_agent` — reinicio graceful/force
- [ ] `update_knowledge_base` — actualizar KB con sanitización
- [ ] `pause_outbound_campaign` — pausar/reanudar campañas
- [ ] `get_agent_status` — estado completo para dashboard 3D
- [ ] `scale_agent` — escalar instancias concurrentes

### 6. 🔴 EVOLUTION ENGINE MCP
- [ ] `propose_prompt_change` — analizar transcripciones fallidas
- [ ] `trigger_ab_test` — A/B testing con análisis estadístico
- [ ] `analyze_call_sentiment` — análisis de sentimiento/emoción
- [ ] `get_evolution_history` — historial de evolución del agente
- [ ] Auto-mejora: 20% tráfico variante, 24h duración, >0.90 confianza

### 7. 🟡 INFRA MCP
- [ ] `rotate_api_keys` — rotación automática cada 30 días
- [ ] `verify_backup_integrity` — probar restauración de backups
- [ ] `scale_workers` — escalar workers Celery
- [ ] `get_infra_health` — dashboard completo de infraestructura
- [ ] `emergency_restart` — reinicio de emergencia de servicios

### 8. 🟡 ONBOARDING AUTOMATIZADO
- [ ] Formulario de registro: nombre empresa, actividad, clientes/mes, teléfono
- [ ] Creación automática de tenant al completar registro
- [ ] Clon de voz: subir 30s audio → procesar → activar
- [ ] Configuración KB: FAQ, servicios, precios del cliente
- [ ] Activar número virtual DID
- [ ] Campaña de adopción (día 1-7): "prueba tu agente"
- [ ] Campaña de educación (día 8-14): "cómo sacarle provecho"
- [ ] Forzar uso: notificaciones diarias de actividad
- [ ] Conversión trial → pago: día 14

### 9. 🟡 3D DASHBOARD (Soberano+)
- [ ] Three.js + React Three Fiber bundle
- [ ] Escenario 3D según rol del negocio
- [ ] Avatar con 7 estados (dormido, despierto, llamada, procesando, etc.)
- [ ] HUD overlay con métricas en tiempo real
- [ ] WebSocket para estado del agente (<500ms latencia)
- [ ] Sonido ambiente según estado
- [ ] Orbit controls (rotar cámara)

### 10. 🟡 PACKAGING Y VENTAS
- [x] Planes definidos: Despertar/Elevar/Soberano/Oráculo
- [x] Pricing con márgenes (70%/50%/55%)
- [x] Partnership: Visionario/Arquitecto/Guardián
- [x] Presentación para César (HTML + PDF)
- [ ] Portal de autoservicio para registro
- [ ] Pasarela de pago (MercadoPago + Bitso crypto)
- [ ] Facturación automatizada
- [ ] Dashboard de César: leads, ingresos, clientes activos

### 11. 🟡 SEGURIDAD Y CUMPLIMIENTO
- [ ] KYC estándar para clientes Elevar+
- [ ] KYC NSFW para creadores de contenido
- [ ] Términos de uso aplicables por paquete
- [ ] Privacidad de datos (PII masking)
- [ ] SLA por paquete (99.0%/99.5%/99.9%/99.95%)
- [ ] Política de uso indebido
- [ ] Reserva de uso / limitación de responsabilidad

---

## Conexiones críticas (Twilio → Campaigns → Leads → Tenant)

```
Llamada entrante (PSTN)
    │
    ▼
Twilio Voice Bridge (:8700)
    │
    ├── ¿Nuevo cliente? → Crear lead en CRM (tenant_id)
    │
    ├── Whisper STT → transcripción
    │
    ├── LLM (DeepSeek/GLM-5.2) → respuesta + scoring
    │
    ├── Kokoro/Edge TTS → respuesta de voz
    │
    └── FreeSWITCH → reproduce al cliente
            │
            ▼
    Post-llamada:
    ├── Scoring BANT → lead calificado / no calificado
    ├── Si es calificado → notificar a César
    ├── Si es frío → agregar a campaña outbound
    └── Todo → guardar en Qdrant + PostgreSQL (tenant_astrotech)
```

## Orden de implementación sugerido

| Sprint | Qué | Depende de |
|---|---|---|
| **1** | Twilio → Tenant routing + Lead creation | Infra base ✅ |
| **2** | Outbound campaigns + Cold/Warm scoring | Sprint 1 |
| **3** | Agent Control MCP + Evolution Engine | Sprint 2 |
| **4** | Onboarding automático + Tenant auto-provision | Sprint 3 |
| **5** | 3D Dashboard (Soberano) | Sprint 4 |
| **6** | Portal + Facturación + Pasarela de pago | Sprint 5 |
