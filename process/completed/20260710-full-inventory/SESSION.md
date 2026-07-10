# SESSION 2026-07-10 — Inventario Completo + Gap Analysis

## Resumen
Sesión de inventario total del ecosistema Sonora Digital Corp. Se catalogaron 3,045+ archivos fuente en 18 categorías. Se identificaron gaps críticos en Sub-OS prompts, cognitive kernel stubs, y documentación de producto.

---

## 1. INVENTARIO COMPLETO

### 1.1 Landing Pages / Web Pages
| # | Path | Status |
|---|------|--------|
| 1 | `sdc-architecture-blueprint.html` | ✅ Completo |
| 2 | `mission-control/index.html` | ⚠️ Parcial (dashboard SPA) |
| 3 | `products/index.html` | ⚠️ Parcial |
| 4 | `products/abe-music-os-presentation.html` | ✅ Completo |
| 5 | `products/abe-portfolio/index.html` | ✅ Completo |
| 6 | `products/booking/index.html` | ⚠️ Parcial |
| 7 | `products/content-studio/dashboard.html` | ✅ Completo (creado esta sesión) |
| 8 | `products/landing-artista/index.html` | ⚠️ Parcial |
| 9 | `products/yami/www/` (4 HTML + manifest + sw.js) | ✅ Completo |
| 10 | `apps/SIGNAL/` (3 HTML) | ✅ Completo |
| 11 | `apps/abe-service/avatar/index.html` | ✅ Completo (creado esta sesión) |
| 12 | `apps/abe-service/pwa/` (index.html, estado.html, manifest.json, sw.js) | ✅ Completo |
| 13 | `apps/guardian/static/scoreboard.html` | ✅ Completo |
| 14 | `apps/webui/static/` (35+ HTML) | ✅ Completo |
| 15 | `clients/abe-music/` (3 HTML) | ⚠️ Parcial |
| 16 | `clients/azrec/` (landing + 5 product pages) | ⚠️ Parcial |
| 17 | `docs/` (index.html, mission-control.html, presentacion.html, SYSTEM-MAP.html, SONORA-EVOLUTION.html) | ✅ Completo |
| 18 | `frontends/abe/` (index.html + 5 portal pages) | ⚠️ Parcial |
| 19 | `frontends/dashboard/` (4 HTML) | ⚠️ Parcial |
| 20 | `frontends/landing/` (3 HTML) | ⚠️ Parcial |
| 21 | `mcp/gateway/` (18 HTML) | ✅ Completo |
| 22 | `ref/` (6 HTML) | ✅ Completo |
| 23 | `products/` presentations (5 reveal.js) | ✅ Completo |

**Total: ~80+ HTML pages**

### 1.2 Apps (`apps/`)
| App | Nivel | Status | Descripción |
|-----|-------|--------|-------------|
| SIGNAL | Producto | ✅ Producción | Next.js artista intelligence (29 pages, 20+ API routes, 5 providers) |
| abe-service | Core | ✅ Producción | ABE Music OS backend (FastAPI): PWA, contratos, revenue, CRM, RAG, chat, distro, sync, voice |
| act | Kernel N4 | ⚠️ Parcial | Level 4 Cognitive Kernel: healer, monitor, notifier, hermes_client |
| agent_metrics | Core | ❌ Needs work | Simple test metrics |
| agents | Core | ❌ Stub | Solo `__init__.py` |
| brain | Core | ⚠️ Parcial | Knowledge brain: ingesta engram, events, hermes, lecciones, Neo4j, truth |
| control | Kernel N7 | 🔴 Stub | Level 7 — solo `__init__.py` |
| decide | Kernel N3 | ⚠️ Parcial | Execution queue, scheduler, checkpoint, economics |
| economics | Core | ❌ Needs work | Basic stub |
| google-mcp | Core | ⚠️ Parcial | Google MCP connector |
| guardian | Core | ✅ Completo | Truth Guardian: compliance, drift, health, Telegram |
| hermes | Core | ✅ Completo | MCP bridge, multi-connector, publisher, YouTube scraper |
| jarvis | Core | ✅ Completo | Core OS: 18 agent modules, Neo4j, brain graph, RAG, LLM, orchestrator, sales, voice |
| learn | Kernel N6 | 🔴 Stub | Solo `__init__.py` + heuristics stub |
| learning | Core | ❌ Needs work | Duplicado de learn |
| measure | Kernel N5 | ⚠️ Parcial | Scoreboard + control HTML |
| observe | Kernel N1 | 🔴 Stub | Solo `__init__.py` |
| understand | Kernel N2 | 🔴 Stub | Solo `__init__.py` |
| voice | Core | ❌ Needs work | Whisper + TTS pipeline |
| webui | Core | ✅ Completo | FastAPI + WebSocket (:5174), 35+ static HTML |
| cache/data/logs/state | Core | ⚠️ Run-time | Directorios de datos |

### 1.3 PWAs
| Path | Status |
|------|--------|
| `apps/abe-service/pwa/manifest.json` + app.js + index.html + estado.html + style.css + icons | ✅ Completo |
| `apps/webui/static/manifest.json` | ✅ Completo |
| `products/yami/www/manifest.json` + sw.js | ✅ Completo |

**Total: 3 PWAs** — ABE Music, WebUI (Mystic), Yami

### 1.4 MCPs
| Componente | Archivos | Status |
|------------|----------|--------|
| `mcp/servers/` | 8 configs (metabase, n8n, neo4j, paperclip, postgres, qdrant, redis, uptime) | ✅ Completo |
| `mcp/tools/` | 30+ .js (abe, brain, hermes, approvals, billing, content, files, knowledge-graph, music-providers, payments, sales, score, skills, voice, zamora, sdc, app) | ✅ Completo |
| `mcp/gateway/` | 18 HTML + 2 JS HTTP server | ✅ Completo |
| `mcp/auth/` | JWT + middleware | ✅ Completo |
| `mcp/registry/` | Capability + skill registry + learning loop | ✅ Completo |
| `mcp/scheduler/` | Scheduler + auto-heal + self-improve | ✅ Completo |
| `mcp/sandbox/` | Execution sandbox | ✅ Completo |
| `mcp/providers/` | Provider manager + router + docker runner | ✅ Completo |
| `mcp/plugins/` | Plugin manager (109 lines) | ✅ Completo |
| `mcp/security/` | Security audit + soul policies (200+ lines) | ✅ Completo |
| `mcp/swarm/` | Swarm engine (73 lines) + samples | ✅ Completo |
| `mcp/workflow/` | Engine + 6 workflows | ✅ Completo |
| `mcp/alerts/` | Alerting system (82 lines) | ✅ Completo |
| `mcp/achievements/` | Gamification (97 lines) | ✅ Completo |
| `mcp/chaos/` | Chaos monkey (97 lines) | ✅ Completo |
| `mcp/cli/` | sdc + sonora CLI | ✅ Completo |
| `mcp/templates/` | Template engine (75 lines) | ✅ Completo |
| `mcp/adk/` | ADK adapter + 34 agent YAMLs | ✅ Completo |
| `mcp/sdk/` | Sonora client SDK | ✅ Completo |
| `mcp/scripts/` | Watchdog 24/7 | ✅ Completo |
| `mcp/Dockerfile` + `package.json` + `mcp-ecosystem.json` | ✅ Completo |

### 1.5 CLIs
| Path | Status |
|------|--------|
| `mcp/cli/sdc` | ✅ Completo |
| `mcp/cli/sonora` | ✅ Completo |
| `scripts/` (103 entries) | ⚠️ Mixed |

### 1.6 Skills
| Path | Status |
|------|--------|
| `skills/audit-security.skill.md` | ✅ Completo |
| `skills/capture-knowledge.skill.md` | ✅ Completo |
| `skills/deploy-code.skill.md` | ✅ Completo |
| `skills/monitor-service.skill.md` | ✅ Completo |
| `skills/plan-strategy.skill.md` | ✅ Completo |
| `skills/presentar.md` | ✅ Completo |
| `skills/qualify-lead.skill.md` | ✅ Completo |
| `skills/resolve-ticket.skill.md` | ✅ Completo |
| `skills/spawn-agent.skill.md` | ✅ Completo |
| `skills/track-finance.skill.md` | ✅ Completo |
| `skills/validate-quality.skill.md` | ✅ Completo |
| `skills/SKILL-TEMPLATE.md` | ✅ Completo |
| `skills/process/` (8 skills: auto-doc, gsd, sdd-*) | ✅ Completo |
| `capabilities/*/skills/` (8 Python handlers) | ✅ Completo |

**Total: 20+ skills**

### 1.7 Tools
| Path | Status |
|------|--------|
| `tools/README.md` | ✅ Completo |
| `tools/mcp/` (hermes, openclaw, brain, skills, agent-converse) | ✅ Completo |
| `tools/system/` (files, commands, voice, memory, mcp, healthcheck, search, tests, docker, user) | ✅ Completo |
| `tools/business/` (payments, sales, content, media, music, viral, mysticverse, zamora, approvals, billing, store, design-tools, generator, intake, webhooks, score, music-providers) | ✅ Completo |
| `tools/abe/` (abe, abe-connect, abe-hub, abe-store) | ✅ Completo |
| `mcp/tools/` (30 .js implementations) | ✅ Completo |
| `apps/jarvis/src/core/tools/` (4 files: definitions, executors, router) | ✅ Completo |

**Capas**: definitions → registry → implementations → executor router → ADK bridge

### 1.8 Prompts
| Path | Status |
|------|--------|
| `constitution/OMEGA-PROMPT.md` | ✅ Completo (master system prompt) |
| `constitution/SOUL.md` | ✅ Completo (identidad del sistema) |
| `evolution/prompts/` | ❌ Vacio |
| `capabilities/*/prompts/` (8 dirs) | 🔴 Todos vacios |
| **`prompts/prompts/OS/`** (10 Sub-OS prompts) | 🔴 **NO EXISTE** — referenciado en AGENTS.md |
| `evolution/prompt_updater.py` | ✅ Completo |

### 1.9 Skill Registry
| Path | Status |
|------|--------|
| `mcp/registry/skill-registry.js` | ✅ Completo |
| `capabilities/index.yaml` | ✅ Completo |
| `config/registry.json` | ✅ Completo |

### 1.10 Agent Registry
| Path | Status |
|------|--------|
| `agents/registry.yaml` | ✅ 11 agentes con capabilities |
| `agents/capabilities/` | ✅ 8 definiciones |
| `agents/policies/` | ✅ 7 policies (deny-all por defecto) |
| `mcp/adk/agents/` | ✅ 34 agent YAMLs para ABE Music |
| `apps/agents/` | 🔴 Stub (solo __init__.py) |

### 1.11 Sub-Agents
| Path | Status |
|------|--------|
| `process/has/HAS-005-agent-ecosystem.md` | ✅ Spec de arquitectura de agentes |
| No hay configuración formal de sub-agents | ❌ Ausente |

### 1.12 AGENTS.md
✅ Existe, 315 líneas. Contiene: personas, machines, estructura, comandos, servicios, revenue, learnings, protocolo, session HTML, Sub-OS architecture, agentes opencode, comandos rápidos, close session, auto-doc, templates, cognitive kernel.

❌ **Bug**: Referencia `prompts/prompts/OS/` que no existe.

### 1.13 Docs / Manuals
| Path | Status |
|------|--------|
| `docs/PROTOCOLO.md` | ✅ Protocolo de construcción |
| `docs/ARQUITECTURA.md` | ✅ Arquitectura general |
| `docs/BLUEPRINT.md` | ✅ Blueprint del sistema |
| `docs/RECOVERY-MANUAL.md` | ✅ Recovery manual |
| `docs/SECURITY-RUNBOOK.md` | ✅ Security runbook |
| `docs/STACK-LOCK.md` | ✅ Stack lock docs |
| `docs/MAPA-SDC.md` | ✅ Mapa del ecosistema |
| `docs/MCP-HACKS-ANALISIS.md` | ✅ MCP analysis |
| `docs/OPENCLAW-HERMES-ANALISIS.md` | ✅ OpenClaw analysis |
| `docs/STRATEGIC-AUDIT-v2.md` | ✅ Strategic audit |
| `docs/VPS-DEPLOY.md` | ✅ VPS deploy guide |
| `docs/VERCEL-SETUP.md` | ✅ Vercel setup |
| `docs/INDEX.md` | ✅ Docs index |
| `products/content-studio/API.md` | ✅ Creado esta sesión (20 tools) |
| `products/omnivoice/README.md` | ✅ README básico |
| `manuals/` | 🔴 **NO EXISTE** — no hay manuales de usuario/admin |

### 1.14 Products
| Producto | Status | Puertos |
|----------|--------|---------|
| **content-studio** | ✅ Completo | :8765 (MCP), :8766 (TTS), :8768 (storage) |
| **omnivoice** | ✅ Completo | :3900 (API) |
| **open-notebook** | ✅ Completo | :8502 (UI), :5055 (API) |
| **google-mcp** | ⚠️ Parcial | - |
| **SIGNAL** | ✅ Producción | Next.js app |
| **yami** | ✅ Completo | PWA con manifest |
| **abe-portfolio** | ✅ Completo | Landing page |
| **booking** | ⚠️ Parcial | Landing page |
| **mystika** | ⚠️ En desarrollo | NFTs / metaverse |
| **chatbot** | ⚠️ Parcial | - |

### 1.15 Process
| Componente | Status |
|------------|--------|
| `process/has/` | ✅ 11 specs (HAS-000 through HAS-011) |
| `process/completed/` | ✅ 36 entries (SPECs + session dirs) |
| `process/active/` | ✅ SPECs activos |
| `process/templates/` | ✅ Templates |
| `process/CONDUCT.md` | ✅ Code of conduct |

### 1.16 Config
| Path | Status |
|------|--------|
| `config/registry.json` | ✅ |
| `config/machines.json` | ✅ |
| `config/mcp/` | ✅ 3 configs |
| `config/generated/` | ✅ Auto-generated from fleet.yml |

### 1.17 Scripts
| Script | Status |
|--------|--------|
| `scripts/up.sh` | ✅ Start all services |
| `scripts/deploy.sh` | ✅ Deploy presentations |
| `scripts/close-session.sh` | ✅ Session close automation |
| `scripts/constitution-gate.py` | ✅ 6-gate constitution check |
| `scripts/evolution-cron.sh` | ✅ Evolution engine cron |
| `scripts/sync-to-vps.sh` | ✅ Rsync to VPS |
| `scripts/install-sync-cron.sh` | ✅ Sync cron installer |
| `scripts/ver.sh` | ✅ Open service URLs |
| `scripts/fork-product.sh` | ✅ Fork to standalone repo |
| `scripts/check-capability.py` | ✅ Capability checker |

### 1.18 Infra
| Componente | Status |
|------------|--------|
| `infra/docker-compose.yml` | ✅ (core) |
| `infra/docker-compose.products.yml` | ✅ (products) |
| `infra/` + monitoreo | ✅ |

---

## 2. GAP ANALYSIS

### 🔴 CRITICAL — No existen

| Gap | Impacto | Solución |
|-----|---------|----------|
| `prompts/prompts/OS/` (10 Sub-OS prompts) | AGENTS.md referencia paths rotos. Sin estos prompts, los agentes opencode no tienen identidad de Sub-OS. | Crear 10 archivos .md |
| `capabilities/*/prompts/` (8 dirs vacios) | Capabilities sin prompts = agentes sin contexto especializado | Poblar cada dir con su prompt |
| `apps/observe/` (Level 1 Kernel) | Cognitive Kernel incompleto — no hay collectors pipeline | Implementar observe |
| `apps/understand/` (Level 2 Kernel) | No hay truth/knowledge processing pipeline | Implementar understand |
| `apps/control/` (Level 7 Kernel) | No hay dashboard unificado de control | Implementar control |
| `manuals/` | No hay manuales de usuario ni admin para productos | Crear directorio + manuales |

### ⚠️ IMPORTANTE — Parcial / Needs Work

| Gap | Detalle |
|-----|---------|
| `apps/learn/` (Level 6) | Solo heuristics.py stub + evolution/ |
| `apps/act/` (Level 4) | Tiene agent modules pero incompleto |
| `apps/measure/` (Level 5) | Tiene scoreboard HTML pero implementación parcial |
| `apps/agents/` | Solo `__init__.py` |
| `apps/economics/` | Stub básico |
| `apps/voice/` | Pipeline parcial |
| `apps/learning/` | Duplicado, necesita merge o cleanup |
| `evolution/prompts/` | Directorio vacío |

### ✅ COMPLETO — Fortalezas del ecosistema

| Área | Detalle |
|------|---------|
| Core OS (jarvis) | 18 agent modules, Neo4j, RAG, LLM, orchestrator, voice |
| ABE Service | PWA, revenue ledger, CRM, RAG, chat, distro, contracts |
| MCP Ecosystem | 30+ tools, 8 servers, 4 bridges, gateway, registry, scheduler, sandbox, ADK, SDK, workflow |
| Guardian | Compliance, drift detection, health checks, Telegram alerts |
| Hermes | MCP bridge, YouTube scraper, publisher, thumbnails |
| WebUI | 35+ static HTML dashboards, FastAPI + WebSocket |
| SIGNAL | Artist intelligence platform (Next.js, 5 providers) |
| PWAs | 3 PWAs (ABE, Mystic, Yami) |
| Tests | 78 tests (5 suites) en el core |
| CLI | sdc + sonora commands |
| Skills | 20+ skill definitions + template |
| Tools | Layered architecture (defs → registry → impls → router → ADK) |
| Products | content-studio (20 tools), omnivoice, open-notebook forkeados |
| Constitution | OMEGA-PROMPT + SOUL + 16 YAMLs + HAS architecture |
| Process | HAS-000 to HAS-011, 36 completed sessions, close-session automation |
| GitHub | 3 repos product separados + monorepo principal |
| Monitoring | Cron sync, watchdog, healthchecks, evolution engine |
| Gaming | 3 ABE Music artists tracked ($479k+ revenue) |

---

## 3. PROXIMOS PASOS RECOMENDADOS

### Prioridad 1 — Arreglar referencias rotas
- [ ] Crear `prompts/prompts/OS/` con 10 Sub-OS prompts
- [ ] Actualizar AGENTS.md para que los paths sean correctos

### Prioridad 2 — Completar Cognitive Kernel
- [ ] Implementar `apps/observe/` (Level 1): collectors pipeline
- [ ] Implementar `apps/understand/` (Level 2): truth + knowledge processing
- [ ] Completar `apps/act/` (Level 4): agent execution
- [ ] Completar `apps/learn/` (Level 6): heuristics + evolution
- [ ] Implementar `apps/control/` (Level 7): unified dashboard

### Prioridad 3 — Prompt Library
- [ ] Poblar `capabilities/*/prompts/` con prompts especializados
- [ ] Poblar `evolution/prompts/` con prompts de evolucion
- [ ] Crear `prompts/library/` como repositorio central de prompts

### Prioridad 4 — Documentación
- [ ] Crear `manuals/` con manual de usuario y admin para cada producto
- [ ] Completar `README.md` para cada capability

### Prioridad 5 — Limpieza
- [ ] Merge `apps/learning/` → `apps/learn/` o eliminar duplicado
- [ ] Completar módulos parciales en mcp/ (plugins, security, swarm, alerts, achievements, chaos, templates)
- [ ] Evaluar y consolidar frontends/ redundantes

---

## 4. PRODUCTOS FORKEADOS (esta sesión)

| Producto | Repo GitHub | Commit |
|----------|-------------|--------|
| content-studio | `sonoradigitalcorp-H/content-studio` | `146e61d` |
| omnivoice | `sonoradigitalcorp-H/omnivoice` | `b3b5112` |
| open-notebook | `sonoradigitalcorp-H/open-notebook` | `571a16b` |

## 5. SERVICIOS ACTIVOS

| Puerto | Servicio | Dominio | Status |
|--------|----------|---------|--------|
| 5174 | Web UI | Core | ✅ |
| 5180 | ABE Service + PWA | Core | ✅ |
| 8000 | Hermes MCP | Core | ✅ |
| 8080 | Evolution Dashboard | Core | ✅ |
| 8088 | Guardian + Scoreboard | Core | ✅ |
| 8502 | Open Notebook UI | Producto | ✅ |
| 5055 | Open Notebook API | Producto | ✅ |
| 3900 | OmniVoice | Producto | ✅ |
| 8765 | Content Server MCP | Producto | ✅ |
| 8766 | Edge TTS API | Producto | ✅ |
| 8768 | Content Storage (nginx) | Producto | ✅ |
| 18789 | OpenClaw Gateway | Core | ✅ |
| 6333 | Qdrant | Core | ✅ |
| 7687 | Neo4j | Core | ✅ |
| 5678 | n8n | Core | ✅ |

---

*Documento generado: 2026-07-10*
