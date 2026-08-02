# SDC Blueprint — Estructura Limpia del Proyecto

**Fecha:** 2026-08-02
**Repo:** `sonora-digital-corp/`

---

## Árboles de Carpetas (sin duplicados)

```
sonora-digital-corp/
│
├── kernel/                          ← Capa 0: Identidad, reglas, constitución
│   ├── SOUL.md, OMEGA-PROMPT.md, MANIFESTO.md
│   ├── AI-ETHICS.md, TRUTH.md, CONTRATO.md
│   ├── 000-governance.md, 010-agent-rules.md
│   ├── 020-data-policy.md, 030-security.md, 040-evolution.md
│   └── *.yaml (standards: mission, vision, principles, etc.)
│
├── infra/                           ← Capa 1: Infraestructura SSOT
│   ├── docker-compose.yml (+ vps, data, omnivoice, scrapers)
│   ├── fleet.yml, Dockerfile
│   ├── monitoring/ (prometheus, grafana, dashboards)
│   ├── nginx/, neo4j/, qdrant/, supabase/
│   ├── telegram/ (Node.js bot server)
│   ├── mcp-server/ (Python MCP gateway)
│   ├── migrations/ (SQL)
│   ├── systemd/ (25 service/timer units)
│   └── observability/ (grafana dashboards + alerts)
│
├── apps/                            ← Capa 2: Servicios core
│   ├── core/                        ← Motor principal (engine, planner, router, agents)
│   ├── whatsapp/                    ← WhatsApp responders + dispatch + order_store
│   ├── voice/                       ← Voice assistant (JARVIS)
│   ├── frontends/                   ← UIs (agentic-os, dashboard, landing, etc.)
│   ├── grimoire/                    ← Grimoire 3D (Three.js)
│   ├── hermes/                      ← Hermes agent
│   ├── sonora_engine/               ← FastAPI engine
│   ├── twilio-voice/                ← Twilio voice server
│   ├── telegram_scheduler/          ← Telegram scheduler
│   ├── monitor/                     ← System monitor dashboards
│   ├── openclaw_edge/               ← OpenClaw edge client
│   ├── SIGNAL/                      ← SIGNAL app (Next.js)
│   ├── stt/, tts/                   ← Speech-to-text/text-to-speech
│   ├── instagram/, tiktok/, youtube/, spotify/  ← Platform integrations
│   ├── webui/                       ← Web UI
│   └── evolution/                   ← Auto-evolution system
│
├── products/                        ← Capa 3: Lo que SDC vende
│   ├── call-system/                 ← AI call system
│   ├── voice-service/               ← Voice service
│   ├── clon-digital/                ← Digital clone product
│   ├── agent-marketplace/           ← Agent marketplace
│   ├── social/                      ← Social media engine
│   ├── notifier/                    ← Notification system
│   ├── order_tracker/               ← Order tracking
│   ├── cyber_diagnosis/             ← Cyber diagnosis tool
│   ├── mystika/                     ← Mystika product
│   ├── ce_son/                      ← CE-Son product
│   ├── affiliates/                  ← Affiliate system
│   ├── marketing/                   ← Marketing tools
│   └── archive/                     ← Productos archivados (2,651 archivos)
│
├── clients/                         ← Capa 4: Clientes externos
│   ├── r1/                          ← R1 (Ce-Son)
│   ├── Abe Music Group/             ← ABE Music
│   ├── Cesar Delivery/              ← Cesar Delivery
│   ├── Hermosillo Contability Corp./ ← Hermosillo Contabilidad
│   └── Joyeria/                     ← Joyería
│
├── tenants/                         ← Entornos multi-tenant
│   ├── Aztrotech/                   ← AZTROTECH (activo)
│   ├── abe-music/                   ← ABE Music tenant
│   └── hermosillo-contabilidad/     ← Hermosillo Contabilidad tenant
│
├── skills/                          ← Skills, tools, packs
│   ├── mcp/ (servers/)              ← MCP tools (24 servidores)
│   ├── hermes/                      ← Hermes skills
│   ├── process/                     ← Process skills
│   ├── opencode/                    ← OpenCode config
│   ├── templates/                   ← Skill templates
│   ├── tests/                       ← Skill tests
│   └── *.skill.md                   ← 40+ skill definitions
│
├── config/                          ← Configuración SSOT
│   ├── tenants/ (_template, abe-music, aztrotech, etc.)
│   ├── agents/ (registry.yaml)
│   ├── n8n/ (7 workflows)
│   ├── n8n-sdc/ (37 workflows)
│   ├── n8n-workflows/ (5 workflows)
│   ├── secrets/ (.age encrypted)
│   └── *.yaml, *.json, *.toml      ← System configs
│
├── docs/                            ← Documentación
│   ├── adrs/ (68+ Architecture Decision Records)
│   ├── specs/ (22 feature specifications)
│   ├── planning/ (blueprint, SLA, tiers)
│   ├── process/ (active + completed specs)
│   ├── reference/ (auth, configs, types, utils)
│   └── *.md                         ← Architecture, security, methodology docs
│
├── tests/                           ← Suite de tests
│   ├── unit/ (35+ test files)
│   ├── ce_son/ (order_store tests)
│   ├── gherkin/ (25+ BDD features)
│   ├── evals/ (structural, promptfoo, redteam)
│   ├── e2e/, integration/, quality/
│   └── playwright/ (browser tests)
│
├── scripts/                         ← Scripts operacionales
│   ├── deploy-*.sh                  ← Deployment
│   ├── backup.py, healthcheck.sh    ← Operations
│   ├── provision-tenant.sh          ← Tenant provisioning
│   ├── engram_autocapture.py        ← Memory autocapture
│   ├── social_automation.py         ← Social media
│   └── sdc-doctor.py, preflight.py  ← Validation
│
├── ops/                             ← Capa transversal: Operaciones
│   ├── playbooks/                   ← Recetas paso a paso
│   ├── runbooks/                    ← Procedimientos operacionales
│   └── state/                       ← Estado vivo del sistema
│       ├── engram*.db               ← Memoria persistente
│       ├── events/                  ← Sistema de eventos
│       ├── whatsapp/                ← WhatsApp state
│       ├── memory/                  ← Memoria del sistema
│       └── *.json, *.py             ← Registry, skills, knowledge
│
├── sdc-brain-vault/                 ← Obsidian knowledge vault
│   ├── Blueprint/, Dashboard/, Decisions/
│   ├── Graph/, People/, Projects/, Sessions/, Templates/
│
├── capabilities/                    ← Catálogo de capacidades
│   └── catalog/ (engine.py, manager.py, models.py, registry.yaml)
│
├── portal/                          ← Grimoire 3D (Three.js)
│   └── index.html
│
├── state/                           ← State SSOT (mínimo)
│   └── logs/events.jsonl
│
├── reference/                       ← Experimentos de referencia
│   └── experimentos/ (brain-v1, portal-v2-templates)
│
├── Makefile                         ← Comandos dev
├── opencode.json                    ← Config OpenCode
├── pyproject.toml, requirements.txt ← Python deps
├── AGENTS.md, CLAUDE.md             ← Agent instructions
└── .env.example, .gitignore         ← Config templates
```

---

## Duplicados Eliminatorios

| Duplicado | Ubicación 1 | Ubicación 2 | Acción |
|-----------|-------------|-------------|--------|
| `process/` | `process/` (raíz) | `docs/process/` | Mantener `docs/process/`, eliminar `process/` raíz |
| `adrs/` | `adrs/` (raíz, 13 files) | `docs/adrs/` (68+ files) | Mantener `docs/adrs/`, eliminar `adrs/` raíz |
| `ops/kernel/` | `ops/kernel/` (copia) | `kernel/` (original) | Eliminar `ops/kernel/` |
| `ops/capabilities/` | `ops/capabilities/` | `capabilities/` | Eliminar `ops/capabilities/` |
| `state/` | `state/` (casi vacío) | `ops/state/` (real) | Mantener `ops/state/`, eliminar `state/` raíz |

---

## Conteos por Directorio

| Directorio | Archivos | Descripción |
|------------|----------|-------------|
| `apps/` | 24,631 | Core services (bulk: frontends/node_modules) |
| `tenants/` | 4,338 | Tenant environments |
| `products/` | 3,286 | Product implementations |
| `docs/` | 635 | Documentation |
| `clients/` | 493 | Client environments |
| `skills/` | 400 | Skills, tools, packs |
| `config/` | 288 | Configuration |
| `scripts/` | 269 | Operational scripts |
| `tests/` | 241 | Test suite |
| `ops/` | 224 | Operations |
| `infra/` | 179 | Infrastructure |
| `kernel/` | 30 | Governance |
| `sdc-brain-vault/` | 26 | Knowledge vault |
| `capabilities/` | 5 | Capability catalog |
| **TOTAL** | **~35,603** | |

---

## Directorios Vacíos (36+)

`config/wacli/`, `ops/recovery/`, `scripts/backend/`, `scripts/infra/`, `scripts/product/`, `scripts/quality/`, `scripts/tenant/`, `skills/hermes/`, `state/social/`, `sdc-brain-vault/Canvas/`, `sdc-brain-vault/Learnings/`, `sdc-brain-vault/Observations/`, `sdc-brain-vault/Sessions/`, `tenants/abe-music/avatar-engine/`, `tenants/Aztrotech/docs/`, `tenants/Aztrotech/memory/`, `tenants/Aztrotech/workflows/`, `tenants/hermosillo-contabilidad/data/`, `tenants/hermosillo-contabilidad/logs/`, `products/voice-service/domain/`, `products/voice-service/prompts/`, `products/voice-service/sdd/`, `products/agent-marketplace/migrations/`, `products/cyber_diagnosis/templates/`, `products/notifier/templates/`, `apps/core/mcp/`

---

## Symlinks Rotos (7)

| Symlink | Target roto |
|---------|-------------|
| `apps/monitor/events.txt` | `/home/ubuntu/sonora-digital-corp/state/logs/events.jsonl` |
| `products/catalog/mystik-ai` | `../production/mystik` |
| `tests/gherkin/clone-person.feature` | Target missing |
| `tests/gherkin/generate-video.feature` | Target missing |
| `tests/gherkin/manage-crm.feature` | Target missing |
| `tests/gherkin/process-payment.feature` | Target missing |
| `tests/gherkin/search-knowledge.feature` | Target missing |
| `tests/gherkin/sync-artist-data.feature` | Target missing |
