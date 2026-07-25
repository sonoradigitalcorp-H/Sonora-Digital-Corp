# Agent Harness — Galaxy Agent (Agent Marketplace)

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: HARNESS-GALAXY-001
**Status**: Preview/Prototype
**Spec**: SPEC-20260723-001

---

> **⚠️ PREVIEW/PROTOTYPE — Especificación para demo y validación**
>
> Este harness define el agente Agent Galaxy que será implementado como prototipo.
> No es producción. Decisiones de producción se abordarán en SPEC separado.
> Fecha objetivo: Q3 2026

---

## 1. Mission

Presentar agentes de IA de Aztro Tech como una experiencia interactiva 3D donde cada agente es un cuerpo celeste en una galaxia, permitiendo a potenciales clientes explorar capacidades visualmente y onboardarse instantáneamente vía su teléfono móvil.

---

## 2. Planet Agents (Capabilities per Celestial Body)

```
Agent Galaxy — 9 Celestial Bodies:

┌─────────────┬──────────────────────────────────────────────────────────┐
│ Planeta     │ Rol / Tema              │ Capacidades                    │
├─────────────┼─────────────────────────┼────────────────────────────────┤
│ Mercurio    │ Velocidad / Agilidad    │ Respuesta rápida, tareas       │
│             │                         │ simples, recordatorios         │
├─────────────┼─────────────────────────┼────────────────────────────────┤
│ Venus       │ Comunicación / Social   │ Redes sociales, contenido,     │
│             │                         │ engagement, marketing          │
├─────────────┼─────────────────────────┼────────────────────────────────┤
│ Tauro       │ Finanzas / Estabilidad  │ Pagos, facturación,            │
│             │                         │ reportes financieros           │
├─────────────┼─────────────────────────┼────────────────────────────────┤
│ Marte       │ Acción / Ventas         │ CRM, ventas, seguimiento       │
│             │                         │ de leads, propuestas           │
├─────────────┼─────────────────────────┼────────────────────────────────┤
│ Júpiter     │ Expansión / Full-Stack  │ Todos los módulos,             │
│             │                         │ multi-tenant, white-label      │
├─────────────┼─────────────────────────┼────────────────────────────────┤
│ Saturno     │ Anillos / Integraciones │ APIs, webhooks,                │
│             │                         │ conexiones externas            │
├─────────────┼─────────────────────────┼────────────────────────────────┤
│ Urano       │ Innovación / Creativo   │ Generación de contenido,       │
│             │                         │ imágenes, música               │
├─────────────┼─────────────────────────┼────────────────────────────────┤
│ Neptuno     │ Profundidad / Knowledge │ RAG, base de conocimiento,     │
│             │                         │ Q&A inteligente                │
├─────────────┼─────────────────────────┼────────────────────────────────┤
│ Plutón       │ Oculto / Admin          │ Dashboard admin, métricas,     │
│             │                         │ configuración del sistema      │
└─────────────┴─────────────────────────┴────────────────────────────────┘
```

---

## 3. Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENT GALAXY — PUBLIC MARKETPLACE                  │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Frontend (3D Galaxy)                      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │    │
│  │  │ GalaxyScene  │  │ AgentCards   │  │ Onboarding   │      │    │
│  │  │ (Three.js)   │─►│ (Yu-Gi-Oh)   │─►│ (QR/Link)    │      │    │
│  │  │ 60fps        │  │ FloatingTxt  │  │ Modal        │      │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │    │
│  └──────────────────────────┬──────────────────────────────────┘    │
│                             │ API calls                            │
│                             ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Backend (FastAPI)                         │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │    │
│  │  │ Galaxy API   │  │ Tenant API   │  │ Voice API    │      │    │
│  │  │ GET /galaxy  │  │ POST/tenants │  │ POST/voice   │      │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │    │
│  │  │ Galaxy       │  │ Tenant       │  │ Voice        │      │    │
│  │  │ Service      │  │ Service      │  │ Service      │      │    │
│  │  │ (datos       │  │ (provision   │  │ (wacli +     │      │    │
│  │  │  galaxy)     │  │  + assign)   │  │  STT/TTS)    │      │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │    │
│  └──────────────────────────┬──────────────────────────────────┘    │
│                             │ tenant provisioning                  │
│                             ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    SDC Integration Layer                     │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │    │
│  │  │ OpenClaw │  │ Hermes   │  │ OpenCode │  │ Engram   │   │    │
│  │  │ (agent   │  │ (MCP     │  │ (skills  │  │ (memory  │   │    │
│  │  │  ops)    │  │  gw)     │  │  +tools) │  │  layers) │   │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │    │
│  └──────────────────────────┬──────────────────────────────────┘    │
│                             │ data                                 │
│                             ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Data Layer (Prototype)                    │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │    │
│  │  │ SQLite       │  │ JSONL Events │  │ tenant_id    │      │    │
│  │  │ (tenants,    │  │ (state/      │  │ (isolation   │      │    │
│  │  │  configs)    │  │  events/)    │  │  key)        │      │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Voice Pipeline                            │    │
│  │  WhatsApp (wacli) → STT (Whisper) → Agent → TTS → WhatsApp  │    │
│  │       ↑                                                      │    │
│  │       └── Extrable a cualquier red social (configurable)     │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Capabilities

```
Capabilities:
- Galaxy Visualization: Render 3D galaxy with 9 orbiting celestial bodies
  Events: galaxy_page_loaded, galaxy_zoom_in, agent_card_viewed
- Agent Cards: Show Yu-Gi-Oh style capability cards with floating text
  Events: agent_card_viewed
- Quick Onboarding: QR code generation + phone-based onboarding flow
  Events: onboarding_started, onboarding_completed, onboarding_failed
- Multi-tenant Provisioning: Create tenant, assign capabilities based on plan
  Events: tenant_created, capabilities_assigned
- Voice STT/TTS Pipeline: Configure and run voice pipeline via WhatsApp
  Events: voice_pipeline_configured, voice_message_received, voice_message_processed, voice_pipeline_error
- OpenClaw Integration: Assign OpenClaw agent operations per tenant
  Events: openclaw_agent_assigned
- Hermes MCP Gateway: Connect tenant to MCP tools and skills
  Events: hermes_gateway_connected
- OpenCode Skills: Provision skills and tools per tenant capabilities
  Events: skills_provisioned

Planet-specific Capabilities (by agent):
- Mercurio: speed-tasks, reminders, quick-responses
  Events: mercurio_task_completed
- Venus: social-media, content-generation, engagement
  Events: venus_content_published
- Tauro: payments, invoicing, financial-reports
  Events: tauro_payment_processed
- Marte: crm, sales, lead-tracking, proposals
  Events: marte_lead_qualified, marte_proposal_generated
- Júpiter: full-stack, multi-tenant, white-label
  Events: jupiter_full_provisioned
- Saturno: api-integrations, webhooks, external-connections
  Events: saturno_integration_connected
- Urano: creative-generation, images, music
  Events: urano_content_created
- Neptuno: rag, knowledge-base, intelligent-qa
  Events: neptuno_knowledge_queried
- Plutón: admin-dashboard, metrics, system-config
  Events: pluton_config_updated
```

---

## 5. Skills

```
Skills:
- galaxy-renderer: Three.js scene setup + particle systems + orbit animations
  Source: apps/agent-galaxy/frontend/src/components/
  Status: [TODO]
- card-animator: Yu-Gi-Oh card generation + floating text animations
  Source: apps/agent-galaxy/frontend/src/components/
  Status: [TODO]
- qr-generator: QR code generation for onboarding links
  Source: apps/agent-galaxy/frontend/src/components/
  Status: [TODO]
- tenant-provisioner: Multi-tenant creation + capability assignment
  Source: apps/agent-galaxy/backend/services/
  Status: [TODO]
- voice-configurator: wacli + STT/TTS setup per tenant
  Source: apps/agent-galaxy/backend/services/
  Status: [TODO]
- openclaw-connector: Assign OpenClaw agent operations to tenant
  Source: skills/ (SDC existing)
  Status: Available
- hermes-gateway: Connect tenant to MCP tools/skills
  Source: apps/hermes/ (SDC existing)
  Status: Available
- opencode-skills: Provision OpenCode skills per tenant
  Source: skills/ (SDC existing)
  Status: Available
- engram-memory: Store tenant memory in appropriate layers
  Source: apps/jarvis/src/core/engram.py (SDC existing)
  Status: Available
```

---

## 6. Policies

```
Policies:
- Every tenant MUST have a unique tenant_id (UUID v4)
- Capabilities are assigned based on plan: explorador < conquistador < imperio < jupiter
- Voice pipeline MUST degrade gracefully if wacli is unavailable
- Tenant data MUST never be accessible by another tenant (tenant_id isolation)
- Onboarding session MUST be recoverable via unique link if interrupted
- All events MUST be emitted to state/events/events.jsonl
- 3D rendering MUST fallback to 2D if WebGL is not available
- No tenant may access admin capabilities (Plutón) unless explicitly assigned
- OpenClaw, Hermes, and OpenCode integrations MUST use existing SDC infrastructure
- Prototype mode: SQLite is acceptable; production requires PostgreSQL
```

---

## 7. Memory Scope

```
Memory Scope:
  Read: Layer 1 (Working), Layer 2 (Task), Layer 3 (Project), Layer 4 (Customer)
  Write: Layer 1 (Working), Layer 2 (Task), Layer 3 (Project), Layer 4 (Customer), Layer 6 (Historical)
  
  Memory Keys:
    galaxy:session:{session_id}     — Onboarding session state (Layer 2)
    tenant:{tenant_id}:config       — Tenant configuration (Layer 3)
    tenant:{tenant_id}:capabilities — Assigned capabilities (Layer 3)
    tenant:{tenant_id}:voice        — Voice pipeline config (Layer 3)
    galaxy:metrics:{date}           — Daily usage metrics (Layer 5)
    galaxy:lessons                  — Lessons learned (Layer 6)
```

---

## 8. Approval Requirements

```
Approval Requirements:
- tenant creation: none (self-service)
- capability assignment: none (based on plan rules)
- voice pipeline setup: none (auto-configured)
- OpenClaw agent assignment: none (auto-assigned by plan)
- admin access (Plutón): approve (founder only in prototype)
- production deployment: approve + security review
```

---

## 9. Failure Modes

```
Failure Modes:
- WebGL not available: 3D galaxy fails to render
- wacli disconnected: WhatsApp voice pipeline broken
- STT API rate limited: Whisper API returns 429
- TTS provider down: ElevenLabs unavailable
- SQLite write lock: concurrent tenant creation contention
- Onboarding timeout: session expires before completion
- Mobile device OOM: Three.js crashes on low-memory device
- Cross-tenant data leak: bug allows tenant A to see tenant B data
- QR code generation fails: library error or network issue
```

---

## 10. Recovery Procedures

```
Recovery Procedures:
- WebGL not available: activate 2D fallback automatically, show message
- wacli disconnected: attempt reconnect (3 retries), fallback to text mode, alert ops
- STT API rate limited: queue messages, retry with exponential backoff, max 5 retries
- TTS provider down: fallback to text response, retry TTS in background
- SQLite write lock: retry with 100ms backoff, max 3 retries
- Onboarding timeout: session preserved for 24h, user resumes via unique link
- Mobile device OOM: detect low memory, reduce texture resolution, disable particles
- Cross-tenant data leak: emergency audit, revoke access, fix bug, notify affected tenants
- QR code generation fails: fallback to direct link display, retry QR generation
```

---

## 11. Metrics

```
Metrics:
- galaxy_load_time: Given page load When galaxy renders Then time to interactive
  Target: < 3 seconds
- onboarding_completion_rate: Given onboarding started When completed Then %
  Target: > 70%
- onboarding_duration: Given onboarding started When completed Then time
  Target: < 3 minutes
- tenant_activation_rate: Given tenant created When first voice message sent Then %
  Target: > 50% within 24h
- voice_pipeline_success_rate: Given voice message sent When processed Then %
  Target: > 90%
- fps_performance: Given galaxy rendered When measured Then frames per second
  Target: ≥ 30fps (mobile), ≥ 60fps (desktop)
- cross_tenant_isolation: Given tenant A data When tenant B queries Then 0 results
  Target: 100% (zero leaks)
```

---

## 12. Tests

```gherkin
Feature: Galaxy Agent
  Scenario: Render galaxy with 9 celestial bodies
    Given the galaxy data contains 9 agents
    When the frontend loads
    Then 9 celestial bodies are visible orbiting in 3D space

  Scenario: Onboard a new tenant via QR
    Given I am viewing the galaxy
    When I scan the QR code and complete onboarding
    Then a new tenant is created
    And capabilities are assigned based on my plan
    And I receive my agent via WhatsApp

  Scenario: Multi-tenant isolation
    Given tenant A and tenant B exist
    When tenant A queries their configuration
    Then only tenant A's data is returned
    And tenant B's data is not accessible

  Scenario: Voice pipeline end-to-end
    Given a tenant has voice configured
    When they send a voice message via WhatsApp
    Then STT converts audio to text
    And TTS generates an audio response
    And the response is delivered via WhatsApp

  Scenario: Graceful degradation — no WebGL
    Given a browser without WebGL
    When the galaxy page loads
    Then a 2D fallback view is displayed
    And onboarding still works
```

---

## 13. API Endpoints

```
Galaxy:
  GET    /api/galaxy                     — Get galaxy data (all 9 agents)
  GET    /api/galaxy/{agent_name}        — Get specific agent details
  GET    /api/galaxy/{agent_name}/cards  — Get capability cards for agent

Onboarding:
  POST   /api/onboard                    — Start onboarding (creates session)
  GET    /api/onboard/{session_id}       — Get onboarding session status
  POST   /api/onboard/{session_id}/complete — Complete onboarding

Tenants:
  POST   /api/tenants                    — Create new tenant
  GET    /api/tenants/{tenant_id}        — Get tenant configuration
  PUT    /api/tenants/{tenant_id}        — Update tenant capabilities
  DELETE /api/tenants/{tenant_id}        — Delete tenant

Voice:
  POST   /api/voice/config               — Configure STT/TTS for tenant
  GET    /api/voice/config/{tenant_id}   — Get voice configuration
  POST   /api/voice/process              — Process voice message (STT → TTS)
  GET    /api/voice/status/{tenant_id}   — Voice pipeline health

Health:
  GET    /health                         — Health check
  GET    /health/voice                   — Voice pipeline health check
  GET    /health/db                      — Database health check
```

---

## 14. Configuration

```yaml
# config/agent-galaxy.yaml
agent_galaxy:
  planets:
    - name: "Mercurio"
      color: "#B5B5B5"
      orbit_radius: 3.0
      orbit_speed: 0.8
      plan: "explorador"
      capabilities: ["speed-tasks", "reminders", "quick-responses"]
    - name: "Venus"
      color: "#FFD700"
      orbit_radius: 4.5
      orbit_speed: 0.6
      plan: "conquistador"
      capabilities: ["social-media", "content-generation", "engagement"]
    - name: "Tauro"
      color: "#2E8B57"
      orbit_radius: 6.0
      orbit_speed: 0.5
      plan: "conquistador"
      capabilities: ["payments", "invoicing", "financial-reports"]
    - name: "Marte"
      color: "#DC143C"
      orbit_radius: 7.5
      orbit_speed: 0.4
      plan: "conquistador"
      capabilities: ["crm", "sales", "lead-tracking", "proposals"]
    - name: "Júpiter"
      color: "#DAA520"
      orbit_radius: 10.0
      orbit_speed: 0.3
      plan: "imperio"
      capabilities: ["full-stack", "multi-tenant", "white-label", "all-modules"]
    - name: "Saturno"
      color: "#F4A460"
      orbit_radius: 12.5
      orbit_speed: 0.25
      plan: "imperio"
      capabilities: ["api-integrations", "webhooks", "external-connections"]
    - name: "Urano"
      color: "#87CEEB"
      orbit_radius: 15.0
      orbit_speed: 0.2
      plan: "imperio"
      capabilities: ["creative-generation", "images", "music"]
    - name: "Neptuno"
      color: "#4169E1"
      orbit_radius: 17.5
      orbit_speed: 0.15
      plan: "imperio"
      capabilities: ["rag", "knowledge-base", "intelligent-qa"]
    - name: "Plutón"
      color: "#8B4513"
      orbit_radius: 20.0
      orbit_speed: 0.1
      plan: "admin"
      capabilities: ["admin-dashboard", "metrics", "system-config"]

  voice:
    stt_provider: "openai"  # openai | local
    tts_provider: "elevenlabs"  # elevenlabs | local
    default_channel: "whatsapp"  # whatsapp | telegram | web
    fallback_channel: "telegram"

  onboarding:
    session_timeout_minutes: 1440  # 24 hours
    default_plan: "explorador"
    plans:
      explorador: ["Mercurio"]
      conquistador: ["Mercurio", "Venus", "Tauro", "Marte"]
      imperio: ["Mercurio", "Venus", "Tauro", "Marte", "Júpiter", "Saturno", "Urano", "Neptuno"]
      admin: ["Plutón"]

  database:
    type: "sqlite"  # sqlite (prototype) | postgres (production)
    path: "data/agent-galaxy.db"

  events:
    output: "state/events/events.jsonl"
```

---

## 15. Database Schema (Prototype)

```
SQLite (Prototype):
─────────────────────────────────────────────────
Table: tenants
  tenant_id       TEXT PRIMARY KEY    -- UUID v4
  name            TEXT NOT NULL
  plan            TEXT NOT NULL       -- explorador | conquistador | imperio | admin
  created_at      TEXT NOT NULL       -- ISO 8601
  status          TEXT NOT NULL       -- active | suspended | deleted

Table: tenant_capabilities
  id              INTEGER PRIMARY KEY
  tenant_id       TEXT NOT NULL       -- FK → tenants
  capability      TEXT NOT NULL
  enabled         INTEGER DEFAULT 1

Table: onboarding_sessions
  session_id      TEXT PRIMARY KEY    -- UUID v4
  tenant_id       TEXT                -- FK → tenants (nullable until complete)
  agent_choice    TEXT NOT NULL       -- Planet name
  status          TEXT NOT NULL       -- started | completed | expired
  created_at      TEXT NOT NULL
  expires_at      TEXT NOT NULL

Table: voice_config
  tenant_id       TEXT PRIMARY KEY    -- FK → tenants
  stt_provider    TEXT NOT NULL
  tts_provider    TEXT NOT NULL
  channel         TEXT NOT NULL       -- whatsapp | telegram | web
  configured_at   TEXT NOT NULL

Table: events (JSONL — not SQLite)
─────────────────────────────────────────────────
File: state/events/events.jsonl
  Each line: {"event": "...", "tenant_id": "...", "timestamp": "...", "data": {...}}
```

---

## 16. Implementation Roadmap

```
Sprint 1 (Galaxy Foundation):
  - FastAPI backend scaffolding
  - Galaxy data service (9 agents)
  - Frontend Three.js scene setup
  - Basic orbiting celestial bodies

Sprint 2 (Cards + Interaction):
  - Yu-Gi-Oh style agent cards
  - Floating text animations
  - Zoom + hover interactions
  - 2D fallback for non-WebGL browsers

Sprint 3 (Onboarding):
  - QR code generation
  - Onboarding flow (phone-based)
  - Tenant creation + capability assignment
  - Session recovery

Sprint 4 (Voice + Integration):
  - wacli integration
  - STT/TTS pipeline
  - OpenClaw + Hermes + OpenCode integration
  - Multi-tenant isolation tests

Sprint 5 (Polish + Demo):
  - Performance optimization (mobile)
  - Event emission completeness
  - Error handling + graceful degradation
  - Demo preparation
```

---

## 17. Observability

```
Observability:
- Health endpoints: GET /health, GET /health/voice, GET /health/db
- Metrics: galaxy_load_time, onboarding_completion_rate, voice_pipeline_success_rate, fps_performance
- Events: state/events/events.jsonl
- Logs: state/logs/harnesses/galaxy-agent-harness.log
- Log level: INFO
- Tracing: via MCP Gateway (LangFuse when available)
- Alerts: voice_pipeline_error, onboarding_failed, cross_tenant_isolation_violation
```

---

## 18. Dependencies

```
Dependencies:
- Three.js + React Three Fiber + drei: external (npm)
- FastAPI: Python package
- wacli: external tool (WhatsApp CLI)
- OpenAI Whisper API: external (STT)
- ElevenLabs API: external (TTS)
- OpenClaw: internal (SDC) — agent operations
- Hermes: internal (SDC) — MCP gateway
- OpenCode: internal (SDC) — skills + tools
- Engram: internal (SDC) — memory system
- SQLite: external (Python built-in)
- QR code library: external (npm: qrcode)
```

---

## Validation Checklist

- [x] Mission is one sentence, measurable
- [x] All 9 planet agents defined with capabilities
- [x] Architecture diagram describes data flow
- [x] All capabilities map to events
- [x] DB schema defined (SQLite prototype)
- [x] API endpoints documented
- [x] All failure modes have recovery procedures
- [x] Observability endpoints defined
- [x] Implementation roadmap defined
- [x] Preview/Prototype mode explicitly stated
- [x] OpenClaw, Hermes, OpenCode referenced as integrations
- [ ] **[ ] No code exists yet — Preview/Prototype**
