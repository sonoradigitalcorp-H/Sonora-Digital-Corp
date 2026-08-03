# SDC STATUS COMPLETO — Sonora Digital Corp
## Estado del Sistema al 2026-08-02

---

## 1. ULTIMOS 30 COMMITS

```
5db3323 docs: complete blueprint + DR prompt + campaign agent
eb35465 feat(voice): professional greeting flow with full lead data
65fa642 feat(voice): full lead collection + DB save + Mystic notification
505ba03 feat(voice): guided booking flow + WhatsApp confirmation
9f8dbec feat(aztrotech): MVP voice assistant + dashboard + calendar
fe5248b chore: session saved + version tag v0.9.0-jarvis + BLOCKER
115b401 specs: 7 SDD specs complete (023-029) + scores + gherkins
75a440c feat: JARVIS Proactive Engine — SDD Tier 3
527ffdf feat: v1.0.0 — security fixes, test stabilization, documentation
c15e9ef feat: JARVIS voice — microphone + TTS real-time interaction
675ca76 commit: 1893 files + secrets cleaned
cce804d session: 2026-08-02 — System audit, security, automation, JARVIS 3D
35d8925 feat: JARVIS 3D — Three.js interactive dashboard
b0eaabe feat: JARVIS 3D Dashboard + config.yaml bot_token fix
5314aed fix: Playwright audit - 8 critical fixes
13e5903 feat: Facebook automation + cookie import + interactive login
6efad0a feat: Social media automation connected to OpenCode
4ec4354 feat: Social media automation with Playwright anti-loop protection
89b9b08 security: Mystic Shield + rate limiting + secrets cleanup
1a32ed5 feat: White-label provisioning + 92 Gherkin scenarios
3ab137f feat: Bot notificaciones @MysticUnity_bot activo
2e8505f fix: TTS server full path para edge-tts (systemd no tiene ~/.local/bin)
2e34849 feat: skill registry, n8n workflows, auto-improve
bdded96 docs: AGENTS.md actualizado con estado del sistema y metricas
91660fd feat: Redis cache integration en bot (sesiones persistentes)
c7fdc52 fix: lead classifier reglas → 94.4% accuracy (solo-reglas)
e5a6435 feat: RAG knowledge, auto-healing, n8n bridge
64b2608 feat: LLM options, notification bot, 24/7 launcher
6540858 feat: canal Telegram AstroTech + automatización de contenido
3430119 docs: AGENTS.md actualizado con owner/client correctos
```

---

## 2. VERSIONES

| Tag | Fecha | Descripción |
|-----|-------|-------------|
| v1.0.0 | 2026-08-02 | Release estable |
| v0.9.0-jarvis | 2026-08-02 | JARVIS Proactive Engine |

---

## 3. ADRs (19 registros)

| ADR | Fecha | Título |
|-----|-------|--------|
| ADR-20260703-A | 2026-07-03 | Arquitectura base |
| ADR-20260704-ABE-001 | 2026-07-04 | ABE Music integration |
| ADR-20260718-CLONE-SERVICE | 2026-07-18 | Servicio de clonación |
| ADR-20260718-ONBOARDING | 2026-07-18 | Flujo de onboarding |
| ADR-20260719-PRODUCTOS-NUEVOS | 2026-07-19 | Nuevos productos |
| ADR-20260719-SDK-PYTHON | 2026-07-19 | SDK Python |
| ADR-20260719-SKILL-STANDARD | 2026-07-19 | Estándar de skills |
| ADR-20260719-UNIFICACION-ECOSISTEMAS | 2026-07-19 | Unificación de ecosistemas |
| ADR-20260719-WHATSAPP-OS-FASE1 | 2026-07-19 | WhatsApp OS Fase 1 |
| ADR-20260721-SDD-FRAMEWORK | 2026-07-21 | Framework SDD |
| ADR-20260722-001 | 2026-07-22 | Decisión general |
| ADR-20260722-ARQUITECTURA-CORE | 2026-07-22 | Arquitectura core |
| ADR-20260802-AZROTECH-GITHUB-CI | 2026-08-02 | GitHub CI Aztrotech |
| ADR-20260802-AZROTECH-MVP-RAG-MEMORIA | 2026-08-02 | MVP RAG Memoria |
| ADR-20260802-AZROTECH-VOZ-LOCAL | 2026-08-02 | Voz local |
| ADR-20260802-AZROTECH-WHATSAPP-SANDBOX | 2026-08-02 | WhatsApp sandbox |
| ADR-20260802-JARVIS-PROACTIVE | 2026-08-02 | JARVIS Proactive |
| ADR-20260802-SDC-SYSTEM-SESSION | 2026-08-02 | System session |

---

## 4. SPECS/SDD (7 completos)

| Spec | Estado | Descripción |
|------|--------|-------------|
| 023-mvp-dia | ✅ | MVP día |
| 024-voice-agent | ✅ | Agente de voz |
| 025-calendar | ✅ | Integración calendario |
| 026-campaign | ✅ | Agente de campañas |
| 027-dashboard | ✅ | Dashboard monitoreo |
| 028-onboarding | ✅ | Flujo onboarding |
| 029-jarvis | ✅ | JARVIS Proactive Engine |

---

## 5. MCPs CONECTADOS (Estado real)

### Activos ✅

| MCP | Puerto | Tipo | Status |
|-----|--------|------|--------|
| Engram | SQLite | Memoria | ✅ 41 memorias |
| Postgres | 5432 | Datos | ✅ 33 leads, 3 users |
| Qdrant | 6333 | Vectores | ✅ 3 collections, 16 puntos |
| Redis | 6379 | Cache | ✅ PONG |
| Hermes | 8643 | Gateway | ✅ v0.16.0 |
| n8n | 5678 | Workflows | ✅ OK |

### Inactivos ❌

| MCP | Puerto | Status |
|-----|--------|--------|
| OpenClaw | 18789 | OFFLINE |

---

## 6. MCP SERVERS DISPONIBLES (40+)

### Core
- engram_mcp.py — Memoria
- postgres_mcp.py — Base de datos
- qdrant_mcp.py — Vectores
- redis_mcp.py — Cache

### IA/LLM
- llm_mcp.py — Llamadas LLM
- rag_mcp.py — RAG pipeline
- voice_clone_mcp.py — Clonación voz
- kokoro_mcp.py — TTS
- whisper_mcp.py — STT

### Business
- crm_mcp.py — CRM
- payments_mcp.py — Pagos
- commissions_mcp.py — Comisiones
- pricing_mcp.py — Pricing
- credit_mcp.py — Créditos

### Automation
- playwright_mcp.py — Browser automation
- wacli_mcp.py — WhatsApp
- twilio_mcp.py — SMS/Voz
- onboarding_mcp.py — Onboarding
- provision_mcp.py — Provisioning

### Content
- content_mcp.py — Generación contenido
- fal_ai_mcp.py — Imágenes
- lora_mcp.py — Fine-tuning
- generate_mcp.py — Generación general
- omnivoice_mcp.py — Voz omnicanal

### Data
- firecrawl_mcp.py — Web scraping
- metabase_mcp.json — Analytics
- neo4j_mcp.json — Graph DB
- hasura_mcp.py — GraphQL
- supabase_mcp.py — Supabase

### Infra
- ffmpeg_mcp.py — Audio
- upload_mcp.py — Upload
- uptime_mcp.json — Monitoreo
- cost_tracker_mcp.py — Costos

---

## 7. VOICE / STT / TTS / STS

### TTS (Text-to-Speech)
```
Status: ✅ OK
Engine: edge-tts
Voice: es-MX-DaliaNeural
Puerto: 8765
```

### STT (Speech-to-Text)
```
Status: ✅ OK
Engine: faster-whisper
Model: small
Language: es
Puerto: 8766
Device: cpu
```

### Voice Pipeline
```
apps/voice/
├── assistant.py      # Asistente de voz
├── stt.py           # Speech-to-Text
├── tts.py           # Text-to-Speech
├── pipeline.py      # Pipeline completo
├── wake_word.py     # Wake word detection
└── whatsapp_agent.py # Agente WhatsApp
```

---

## 8. GATEWAYS

### Hermes Agent Gateway
```
Status: ✅ OK
Version: 0.16.0
Puerto: 8643
Plataforma: hermes-agent
```

### OpenClaw Gateway
```
Status: ❌ OFFLINE
Puerto: 18789
```

---

## 9. AGENTIC OS

### Estructura
```
apps/core/          # Motor del sistema
apps/hermes/        # Agent Gateway
apps/grimoire/      # Portal 3D
apps/monitor/       # Monitoreo
apps/voice/         # Voz (TTS/STT)
apps/evolution/     # Auto-evolución
apps/SIGNAL/        # Señales
```

### Capacidades
- Motor de conversación multi-tenant
- RAG-first pipeline
- Memoria unificada (Engram)
- Lead scoring automático
- Multi-canal (WhatsApp, Telegram, Instagram)
- Voz local (TTS/STT)
- Dashboard de monitoreo

---

## 10. DASHBOARD

### Status
```
URL: http://localhost:9090
Status: ✅ OK
```

### Métricas
```
Modelos: 1 (deepseek-v4-flash)
Leads: 33
Usuarios: 3
Conversaciones: 3
Embeddings: 16 puntos
```

### Endpoints
- `GET /api/stats` — Estadísticas completas
- `GET /api/health` — Health check

---

## 11. TOOLS DISPONIBLES

### Scripts
- eval_niches.py — Evaluación de nichos
- eval_prompts.py — Evaluación de prompts
- ask_provider.py — Consulta a proveedores

### Skills
- generate-video — Generación de video
- search-knowledge — Búsqueda de conocimiento
- publish-track — Publicación de tracks

### MCP Tools
- content_mcp.py — Contenido
- supabase_mcp.py — Supabase
- lora_mcp.py — Fine-tuning
- ffmpeg_mcp.py — Audio
- onboarding_mcp.py — Onboarding

---

## 12. TENANTS

| Tenant | Owner | Tier | Status |
|--------|-------|------|--------|
| sdc-core | Luis Daniel | enterprise | ✅ |
| abe-fenix | Abraham Ortega | partner_pro | ✅ |
| free | Free Tier | free | ✅ |
| joyeria_el-joyero | El Joyero | basic | ✅ |
| nathy-conta | Nathy | pro | ✅ |

---

## 13. SERVICIOS SYSTEMD

| Servicio | Status | Puerto |
|----------|--------|--------|
| sdc-aztrotech-bot | ✅ active | - |
| sdc-aztrotech-notif | ✅ active | - |
| sdc-aztrotech-tts | ✅ active | :8765 |
| sdc-aztrotech-voice | ✅ active | :8770 |
| sdc-aztrotech-dashboard | ✅ active | :9090 |

---

## 14. DOCKER

| Container | Status | Puerto |
|-----------|--------|--------|
| infra-postgres-1 | ✅ Up 30h | 5432 |
| infra-qdrant-1 | ✅ Up 30h | 6333 |
| infra-redis-1 | ✅ Up 30h | 6379 |
| infra-n8n-1 | ✅ Up 30h | 5678 |

---

## 15. GITHUB ACTIONS

| Workflow | Trigger | Función |
|----------|---------|---------|
| ci.yml | push/PR | Tests + lint |
| aztrotech-ci.yml | push/PR | Tests Aztrotech |
| deploy.yml | merge | Deploy VPS |
| backup.yml | daily | Backup DB |
| agent-alerts.yml | on-call | Alertas |
| automation-validate.yml | push | Validación |

---

## 16. RESUMEN EJECUTIVO

### Estado General: ✅ OPERACIONAL

| Componente | Estado |
|------------|--------|
| Core | ✅ Operacional |
| Voice | ✅ Operacional |
| Dashboard | ✅ Operacional |
| Bot Telegram | ✅ Operacional |
| Notificaciones | ✅ Operacional |
| TTS | ✅ Operacional |
| STT | ✅ Operacional |
| Memoria | ✅ Operacional |
| RAG | ✅ Operacional |
| Hermes | ✅ Operacional |
| n8n | ✅ Operacional |
| OpenClaw | ❌ Offline |

### Pendiente
1. OpenClaw: reconectar
2. Google Calendar: configurar credentials
3. SMTP: configurar credentials
4. VPS: deploy cuando esté disponible
