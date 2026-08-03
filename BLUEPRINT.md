# BLUEPRINT — Sonora Digital Corp (SDC)
## Arquitectura Completa del Sistema

**Fecha**: 2026-08-02
**Versión**: 1.0.0
**Autor**: Luis Daniel Guerrero Enciso

---

## 1. VISIÓN GENERAL

Sonora Digital Corp es una plataforma de agentes IA que ofrece:
- **Agentes de conversación** (WhatsApp, Telegram, Instagram, Facebook)
- **Automatizaciones** (flujos de negocio)
- **Software a medida** (CRM, ERP, apps)
- **Clonación de voz** (TTS/STT local)
- **Marketing automation** (campañas multi-canal)

### Clientes Activos
| Cliente | Tier | Servicios |
|---------|------|-----------|
| Aztrotech (César) | partner_pro | Chat, agents, rag, crm, scheduling |
| ABE Music (Abraham) | partner_pro | Chat, agents, rag, music, booking |
| Nathy Conta | pro | Chat, agents, rag, cfdi, sat, nominas |
| El Joyero | basic | Chat, agents, rag |

---

## 2. ARQUITECTURA DEL SISTEMA

### 2.1 Capas Concéntricas (6 capas)

```
┌─────────────────────────────────────────────┐
│  kernel/        ← Capa 0: Identidad         │
│  infra/         ← Capa 1: Infraestructura   │
│  apps/          ← Capa 2: Servicios Core    │
│  products/      ← Capa 3: Productos SDC     │
│  tenants/       ← Capa 4: Clientes          │
│  portal/        ← Capa Visual: Grimoire 3D  │
│  ops/           ← Capa Transversal: Playbooks│
│  state/         ← Capa Transversal: Estado   │
└─────────────────────────────────────────────┘
```

### 2.2 Stack Tecnológico

```yaml
# Infraestructura
database: PostgreSQL 15
cache: Redis 7
vectors: Qdrant (384-dim, Cosine)
workflows: n8n
messaging: Hermes Agent Gateway

# IA/LLM
models:
  default: deepseek/deepseek-v4-flash
  reasoning: z-ai/glm-5.2
  premium: moonshotai/kimi-k2.7-code
  embeddings: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# Frontend
framework: Vue 3 + Vite
styling: Tailwind CSS
3d: Three.js
animations: GSAP
voice: Web Speech API

# Backend
api: FastAPI (Python)
bot: python-telegram-bot
tts: edge-tts (DaliaNeural)
stt: faster-whisper

# DevOps
containers: Docker Compose
ci/cd: GitHub Actions
monitoring: Custom dashboard
```

---

## 3. ESTRUCTURA DE ARCHIVOS

### 3.1 Raíz del Proyecto

```
sonora-digital-corp/
├── kernel/                    # Capa 0: Constitución
│   ├── SOUL.md               # Identidad del sistema
│   ├── OMEGA-PROMPT.md       # Prompt maestro
│   ├── 000-governance.md     # Gobernanza
│   ├── 010-agent-rules.md    # Reglas de agentes
│   ├── 020-data-policy.md    # Política de datos
│   ├── 030-security.md       # Seguridad
│   └── 040-evolution.md      # Evolución
│
├── infra/                     # Capa 1: Infraestructura
│   ├── docker-compose.yml    # Servicios core
│   ├── fleet.yml             # Configuración de flota
│   └── systemd/              # Servicios systemd
│
├── apps/                      # Capa 2: Servicios Core
│   ├── core/                 # Motor del sistema
│   ├── hermes/               # Agent Gateway
│   ├── grimoire/             # Portal 3D
│   ├── monitor/              # Monitoreo
│   └── voice/                # Voz (TTS/STT)
│
├── products/                  # Capa 3: Productos SDC
│   ├── mystika/              # Producto principal
│   ├── clon-digital/         # Clonación de voz
│   ├── agent-marketplace/    # Marketplace de agentes
│   └── omnivoice/            # Voz omnicanal
│
├── tenants/                   # Capa 4: Clientes
│   ├── Aztrotech/            # César Holguín
│   ├── abe-music/            # Abraham Ortega
│   └── hermosillo-contabilidad/ # Nathy Conta
│
├── skills/                    # Habilidades reutilizables
│   ├── mcp/                  # MCP servers
│   ├── calendar/             # Google Calendar
│   ├── voice/                # Voz
│   ├── rag/                  # RAG
│   └── social-automation/    # Redes sociales
│
├── config/                    # Configuración
│   ├── tenants.json          # Registro de tenants
│   ├── tenant-routing.yaml   # Routing por teléfono
│   └── registry.json         # Capacidades del sistema
│
├── scripts/                   # Scripts utilitarios
│   ├── test/                 # Tests
│   ├── deploy/               # Deploy
│   ├── automation/           # Automatización
│   └── voice/                # Voz
│
├── docs/                      # Documentación
│   ├── adrs/                 # Architecture Decision Records
│   └── specs/                # Especificaciones
│
├── state/                     # Estado del sistema
│   ├── engram/               # Memoria unificada
│   ├── events/               # Eventos
│   └── social/               # Estado de redes
│
└── tests/                     # Suite de tests
    ├── unit/                 # Tests unitarios
    ├── gherkin/              # BDD tests
    └── integration/          # Tests de integración
```

### 3.2 Estructura de un Tenant

```
tenants/Aztrotech/
├── config.yaml               # Configuración del tenant
├── AGENTS.md                 # Reglas del agente
├── bot/                      # Bot de Telegram
│   ├── main.py               # Entry point
│   ├── handlers/             # Handlers de mensajes
│   ├── conversation_engine.py # Motor de conversación
│   ├── lead_classifier.py    # Clasificador de leads
│   ├── rag_retriever.py      # RAG retriever
│   ├── token_tracker.py      # Tracker de tokens
│   └── notification_bot.py   # Bot de notificaciones
├── web/                      # Frontend
│   ├── voice-app/            # Asistente de voz
│   ├── dashboard/            # Dashboard de monitoreo
│   └── static/               # Archivos estáticos
├── skills/                   # Skills del tenant
│   ├── calendar/             # Google Calendar
│   ├── campaign-agent/       # Agente de campañas
│   └── social-automation/    # Redes sociales
├── knowledge/                # Base de conocimiento
│   ├── faq.md                # Preguntas frecuentes
│   ├── catalog.md            # Catálogo de servicios
│   └── services.md           # Guía de servicios
├── tests/                    # Tests del tenant
│   ├── gherkin/              # BDD tests
│   └── run_gherkin.py        # Runner de tests
└── docs/                     # Documentación
    ├── CREDENCIALES-PENDIENTES.md
    └── VOICE-PLATFORM-PLAN.md
```

---

## 4. MCPs (Model Context Protocols)

### 4.1 MCPs Core

| MCP | Puerto | Estado | Función |
|-----|--------|--------|---------|
| Engram | SQLite | ✅ | Memoria unificada (41 memorias) |
| Postgres | 5432 | ✅ | Datos persistentes |
| Qdrant | 6333 | ✅ | Vectores RAG (3 collections) |
| Redis | 6379 | ✅ | Cache de sesiones |
| Hermes | 8643 | ✅ | Agent Gateway |
| n8n | 5678 | ✅ | Workflows |
| OpenClaw | 18789 | ❌ | Gateway (offline) |

### 4.2 MCPs Disponibles (40+)

```yaml
# Core
engram_mcp.py          # Memoria
postgres_mcp.py        # Base de datos
qdrant_mcp.py          # Vectores
redis_mcp.py           # Cache

# IA/LLM
llm_mcp.py             # Llamadas a LLM
rag_mcp.py             # RAG pipeline
voice_clone_mcp.py     # Clonación de voz
kokoro_mcp.py          # TTS
whisper_mcp.py         # STT

# Business
crm_mcp.py             # CRM
payments_mcp.py        # Pagos
commissions_mcp.py     # Comisiones
pricing_mcp.py         # Pricing

# Automation
playwright_mcp.py      # Browser automation
wacli_mcp.py           # WhatsApp
twilio_mcp.py          # SMS/Voz
n8n-mcp.json           # Workflows

# Content
content_mcp.py         # Generación de contenido
fal_ai_mcp.py          # Imágenes
lora_mcp.py            # Fine-tuning
generate_mcp.py        # Generación general

# Data
firecrawl_mcp.py       # Web scraping
metabase-mcp.json      # Analytics
neo4j_mcp.json         # Graph DB
hasura_mcp.py          # GraphQL

# Infra
ffmpeg_mcp.py          # Procesamiento de audio
upload_mcp.py          # Upload de archivos
uptime-mcp.json        # Monitoreo
```

---

## 5. PIPELINES

### 5.1 Pipeline de Conversación

```
Mensaje usuario
    ↓
Shield (rate limit, anti-abuse)
    ↓
Identidad Resolver (cross-canal)
    ↓
EmERGE Memory (contexto previo)
    ↓
RAG Retriever (conocimiento)
    ↓
Emotion Analyzer (señal emocional)
    ↓
Lead Classifier (cold/warm/hot)
    ↓
Prompt Builder (guardrails)
    ↓
LLM Call (deepseek/glm/kimi)
    ↓
Guardrails Post-LLM
    ↓
Persist (Postgres + Engram)
    ↓
Notificar si lead hot
    ↓
Respuesta al usuario
```

### 5.2 Pipeline de Voz

```
Audio usuario
    ↓
STT (faster-whisper)
    ↓
Texto transcrito
    ↓
Pipeline de conversación
    ↓
TTS (edge-tts DaliaNeural)
    ↓
Audio respuesta
    ↓
Envío a Telegram/WhatsApp
```

### 5.3 Pipeline de Campañas

```
Leads en DB
    ↓
Segmentación (cold/warm/hot)
    ↓
Geolocalización (prefijo teléfono)
    ↓
Personalización de mensajes
    ↓
Programación de envíos
    ↓
Envío multi-canal (WhatsApp/Email)
    ↓
Tracking de respuestas
    ↓
Actualización de scores
    ↓
Reporte a César
```

---

## 6. CONFIGURACIONES YAML/JSON

### 6.1 tenants.json

```json
{
  "tenants": {
    "sdc-core": {
      "name": "Sonora Digital Corp",
      "tier": "enterprise",
      "rate_limit": 1000,
      "features": ["chat", "agents", "rag", "voice", "content"]
    },
    "abe-fenix": {
      "name": "ABE Fenix",
      "tier": "partner_pro",
      "rate_limit": 200,
      "features": ["chat", "agents", "rag", "music", "booking"]
    },
    "nathy-conta": {
      "name": "Nathy Conta",
      "tier": "pro",
      "rate_limit": 200,
      "features": ["chat", "agents", "rag", "cfdi", "sat", "nominas"]
    }
  }
}
```

### 6.2 tenant-routing.yaml

```yaml
routing:
  - phone: "+5216623538272"
    tenant: sdc_master
    type: admin
    name: "Luis Daniel"
  
  - phone: "+5216622681111"
    tenant: nathy_conta
    type: client
    name: "Nathy"

default:
  type: unknown
  action: "send_welcome"
```

### 6.3 config.yaml (Aztrotech)

```yaml
tenant_id: aztrotech
display_name: "Aztrotech"
owner: "César Holguín"
language: "es"
timezone: "America/Hermosillo"

models:
  default: deepseek/deepseek-v4-flash
  reasoning: z-ai/glm-5.2
  premium: moonshotai/kimi-k2.7-code

channels:
  telegram:
    enabled: true
    bot_token: "${AZTROTECH_BOT_TOKEN}"
    owner_chat_id: "5738935134"

audio_first:
  enabled: true
  tts_provider: local-edge
  tts_voice: es-MX-DaliaNeural

rag:
  chunk_size: 512
  chunk_overlap: 64
  top_k: 5
  min_score: 0.65
```

---

## 7. GITHUB ACTIONS

### 7.1 CI/CD Workflows

```yaml
# aztrotech-ci.yml
name: Aztrotech CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: make test
      - name: Run lint
        run: make lint
      - name: Run evals
        run: make eval
```

### 7.2 Workflows Activos

| Workflow | Trigger | Función |
|----------|---------|---------|
| ci.yml | push/PR | Tests + lint + eval |
| aztrotech-ci.yml | push/PR | Tests de Aztrotech |
| deploy.yml | merge main | Deploy a VPS |
| backup.yml | daily | Backup de DB |
| agent-alerts.yml | on-call | Alertas de agentes |
| automation-validate.yml | push | Validación de automatizaciones |

---

## 8. ADRs (Architecture Decision Records)

### 8.1 ADRs Existentes

| ADR | Fecha | Decisión |
|-----|-------|----------|
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

---

## 9. SPECS Y SDD

### 9.1 Software Design Documents (SDD)

| Spec | Estado | Descripción |
|------|--------|-------------|
| 023-mvp-dia | ✅ | MVP día |
| 024-voice-agent | ✅ | Agente de voz |
| 025-calendar | ✅ | Integración calendario |
| 026-campaign | ✅ | Agente de campañas |
| 027-dashboard | ✅ | Dashboard monitoreo |
| 028-onboarding | ✅ | Flujo onboarding |
| 029-jarvis | ✅ | JARVIS Proactive Engine |

### 9.2 Metodologías

- **SDD (Software Design Documents)**: Especificación antes de código
- **BDD (Behavior-Driven Development)**: Tests Gherkin
- **TDD (Test-Driven Development)**: Tests antes de código
- **ADR (Architecture Decision Records)**: Decisiones documentadas
- **Soul/Kernel**: Constitución del sistema

---

## 10. PRODUCTOS EN PRODUCCIÓN

### 10.1 Productos Activos

| Producto | Estado | Clientes |
|----------|--------|----------|
| Empleado Digital | ✅ | Aztrotech, ABE |
| Sistema de Ventas | ✅ | Aztrotech |
| Voice Assistant | ✅ | Aztrotech |
| Dashboard | ✅ | Internal |
| Campaign Agent | ✅ | Aztrotech |

### 10.2 Métricas

```yaml
lead_accuracy: 100% (24/24 casos)
llm_response_time: 2.5s
cost_per_message: $0.0001
active_users: 3
leads_captured: 33
conversations: 20
```

---

## 11. DUPLICADOS Y ERRORES

### 11.1 Duplicados Eliminados

- `web/voice-assistant/` → eliminado (duplicado de `voice-app/`)
- `__pycache__/` → eliminados de todos los directorios
- `*.pyc` → eliminados

### 11.2 Errores Conocidos

| Error | Estado | Solución |
|-------|--------|----------|
| OpenClaw offline | ❌ | Revisar servicio |
| WhatsApp re-auth | ⏳ | Necesita QR |
| Google Calendar creds | ⏳ | Necesita Service Account |
| SMTP creds | ⏳ | Necesita App Password |

---

## 12. RESUMEN EJECUTIVO

### Estado del Sistema

| Componente | Estado | Puerto |
|------------|--------|--------|
| Voice Assistant | ✅ | 8770 |
| Dashboard | ✅ | 9090 |
| TTS Server | ✅ | 8765 |
| Bot Telegram | ✅ | - |
| Notif Bot | ✅ | - |
| Postgres | ✅ | 5432 |
| Qdrant | ✅ | 6333 |
| Redis | ✅ | 6379 |
| Hermes | ✅ | 8643 |
| n8n | ✅ | 5678 |

### Últimos Commits

```
eb35465 feat(voice): professional greeting flow
65fa642 feat(voice): full lead collection + DB save
505ba03 feat(voice): guided booking flow
9f8dbec feat(aztrotech): MVP voice assistant
```

### Próximos Pasos

1. Activar Google Calendar credentials
2. Activar SMTP para emails
3. Deploy a VPS cuando esté disponible
4. Conectar OpenClaw MCP
5. Crear canal de Telegram para César

---

## 13. BIBLIOGRAFÍA

### Documentación Interna

- `kernel/SOUL.md` — Identidad del sistema
- `kernel/OMEGA-PROMPT.md` — Prompt maestro
- `docs/adrs/` — Architecture Decision Records
- `AGENTS.md` — Reglas por tenant
- `Makefile` — Comandos de desarrollo

### Tecnologías

- [FastAPI](https://fastapi.tiangolo.com/) — API framework
- [Qdrant](https://qdrant.tech/) — Vector database
- [Hermes](https://github.com/hermes-agent) — Agent gateway
- [Edge-TTS](https://github.com/rany2/edge-tts) — Text to speech
- [FastEmbed](https://qdrant.tech/documentation/fastembed/) — Embeddings

### Referencias

- ElevenLabs — Voice agents platform
- OpenAI — LLM APIs
- Telegram Bot API — Bot framework
- WhatsApp Business API — Messaging

---

**Documento generado automáticamente por SDC Blueprint Generator**
**Última actualización**: 2026-08-02 19:30 MST
