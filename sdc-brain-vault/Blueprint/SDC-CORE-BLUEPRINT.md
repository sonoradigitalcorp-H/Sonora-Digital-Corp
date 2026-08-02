# SDC CORE BLUEPRINT — Arquitectura Completa
## Skills · Tools · MCPs · CLI · Orquestador · Agentes · SubAgentes

| Versión | Fecha | Entradas |
|---------|-------|----------|
| 1.0.0 | 2026-07-18 | 23 MCP servers · 70+ scripts · 20+ agents · 1340+ tests |

---

## ÍNDICE

1. [Arquitectura General](#1-arquitectura-general)
2. [Orquestadores](#2-orquestadores)
3. [MCP Ecosystem (23 servers)](#3-mcp-ecosystem)
4. [Skills (55 OpenClaw + SDD)](#4-skills)
5. [CLI Scripts (70+)](#5-cli-scripts)
6. [Agentes OpenCode (20+)](#6-agentes-opencode)
7. [Agent Registry (10)](#7-agent-registry)
8. [Pipelines (10)](#8-pipelines)
9. [Bases de Datos](#9-bases-de-datos)
10. [Infraestructura](#10-infraestructura)
11. [Memorias](#11-memorias)
12. [Seguridad](#12-seguridad)
13. [Productos](#13-productos)
14. [Alias de Shell](#14-alias-de-shell)

---

## 1. Arquitectura General

```
USUARIOS (WhatsApp · Telegram · Web · API)
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    OPENCLAW GATEWAY (:18789)                  │
│  Routing: chat_id → tenant_id → agent                       │
│  Skills: 55 (browser, payments, social, media, clone, etc)  │
│  Plugins: whatsapp, telegram, browser, canvas, memory-core  │
│  Canales: WhatsApp (wacli), Telegram (bot), Web             │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    OPENCODE (CLI / Agent)                     │
│  Agente Principal: Mystic                                    │
│  SubAgentes: 20+ (sdd*, sales, dev, support, security, etc) │
│  Orquestador SDD: spec→design→apply→verify→archive           │
│  Memoria: Engram (SQLite WAL, 360+ obs)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    MCP GATEWAY (:18989)                       │
│  108+ tools · 23 Python servers · 34 JS tools                │
│  Autenticación: JWT (RS256, 1h expiry)                       │
└────┬──────────┬──────────┬──────────┬──────────┬────────────┘
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐
│ FAL.ai │ │ Qdrant │ │ Neo4j  │ │ Supabase│ │  OpenRouter│
│ GPU    │ │ Vectors│ │ Graphs │ │ Storage│ │  LLM API   │
└────────┘ └────────┘ └────────┘ └────────┘ └────────────┘
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────┐
│                    BASES DE DATOS                            │
│  PostgreSQL · SQLite (Engram · Clone · Cost · Tenants)      │
│  Qdrant (vectors) · Neo4j (graph) · Redis (cache)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Orquestadores

### 2.1 OpenClaw Gateway (Puerto 18789)
```
Type: Service (systemd o docker)
Versión: 2026.7.1
Plugins: 10 (browser, canvas, device-pair, file-transfer, 
         memory-core, ollama, phone-control, talk-voice, 
         telegram, whatsapp)
Skills: 55 (ver sección 4)
Auth: token-based
Canales: WhatsApp, Telegram, Web
```

### 2.2 OpenCode (CLI Agent)
```
Type: CLI (opencode)
Agente Principal: Mystic (primary)
SubAgentes: 20+ (ver sección 6)
Provider: opencode-go (deepseek-v4-flash-free)
Fallback: openrouter (gpt-4o-mini, claude-3.5-sonnet, gemini-2.5-flash)
Memoria: Engram MCP
```

### 2.3 SDD Pipeline Orchestrator
```
Fases: 1-MISSION → 2-CONSTITUTION → 3-RESEARCH → 4-ARCHITECTURE
       → 5-SIMULATION → 6-SPECIFICATION → 7-IMPLEMENTATION
       → 8-VERIFICATION → 9-OBSERVABILITY → 10-EVOLUTION
Tiers: 0 (typo) · 1 (quick fix) · 2 (feature, score≥60) · 3 (platform, score≥75)
Gates: Sync → Constitution → Tests → Lint → Score → ADR
SubAgents: sdd-spec → sdd-design → sdd-apply → sdd-verify → sdd-archive
```

---

## 3. MCP Ecosystem (23 Servers)

### 3.1 Core Memory

| Server | Tools | Puerto | Propósito |
|--------|-------|--------|-----------|
| `engram_mcp.py` | mem_save, mem_search, mem_context, mem_stats, mem_delete, mem_update, mem_suggest_topic_key, mem_save_prompt, mem_session_summary, mem_get_observation, mem_session_start, mem_session_end | 7437 | Memoria persistente del agente |

### 3.2 Clone Service (7 servers)

| Server | Tools | Propósito |
|--------|-------|-----------|
| `lora_mcp.py` | `validate_photos`, `train_lora`, `check_face_quality` | Entrenamiento LoRA facial |
| `voice_clone_mcp.py` | `validate_audio`, `clone_voice`, `list_voices`, `generate_tts` | Clonación de voz |
| `generate_mcp.py` | `gen_photo`, `gen_video`, `gen_tts` | Generación de contenido |
| `credit_mcp.py` | `create_pack`, `consume_credit`, `get_credits` | Sistema de créditos |
| `ffmpeg_mcp.py` | `ffmpeg_convert`, `ffmpeg_assemble`, `ffmpeg_multiformat` | Post-procesamiento video/audio |

### 3.3 Enterprise (5 servers)

| Server | Tools | Propósito |
|--------|-------|-----------|
| `cost_tracker_mcp.py` | `log_cost`, `get_tenant_costs`, `get_all_tenants_summary`, `calculate_llm_cost`, `calculate_fal_cost` | Tracking de costos reales |
| `pricing_mcp.py` | `get_price`, `get_price_from_cost`, `get_industries` | Pricing dinámico |
| `provision_mcp.py` | `create_tenant`, `list_tenants`, `tenant_stats` | Provisioning multi-tenant |
| `commissions_mcp.py` | `register_partner`, `register_deal`, `partner_summary`, `list_partners`, `partner_projection` | Comisiones de partners |

### 3.4 AI/LLM (3 servers)

| Server | Tools | Propósito |
|--------|-------|-----------|
| `llm_mcp.py` | `llm_chat`, `llm_complete` | OpenRouter LLM (con prompt filter) |
| `rag_mcp.py` | `rag_search`, `rag_index` | RAG queries sobre Qdrant |
| `omnivoice_mcp.py` | `omnivoice_speak`, `omnivoice_clone`, `omnivoice_list_voices` | Interfaz OmniVoice |

### 3.5 Data/Storage (3 servers)

| Server | Tools | Propósito |
|--------|-------|-----------|
| `supabase_mcp.py` | signup, login, get_user, list_users, list_buckets, create_bucket, list_files, upload_file, delete_file, get_public_url | Supabase Auth + Storage |
| `firecrawl_mcp.py` | crawl, scrape | Web crawling |
| `upload_mcp.py` | upload | File upload |

### 3.6 Payments (2 servers)

| Server | Tools | Propósito |
|--------|-------|-----------|
| `mercadopago_mcp.py` | create_payment, process_webhook | Mercado Pago |
| `payments_mcp.py` | create, process | Payment processing |

### 3.7 Content/Media (3 servers)

| Server | Tools | Propósito |
|--------|-------|-----------|
| `content_mcp.py` | manage_content | Content management |
| `whisper_mcp.py` | transcribe | Speech-to-text |
| `playwright_mcp.py` | browse, screenshot | Browser automation |
| `openlovable_mcp.py` | lovable_generate_page, lovable_clone_site, lovable_extract_brand, lovable_edit_page | Generación de React pages via AI |
| `hasura_mcp.py` | query, mutate | Hasura GraphQL |

---

## 4. Skills (55 OpenClaw + SDD)

### 4.1 En OpenClaw (55 skills activos)

```
Business:     stripe, supabase, fal-ai, paymentsdb, meta-ads, 
              brevo, ghost-cms, whop-cli
Communication: discord, slack, imsg, trello, wacli, voice-call
Content:      blogwatcher, obsidian, summarize, songsee, canvas, 
              diagram-maker, meme-maker, notion, clawhub, clawpify
AI/Dev:       coding-agent, gemini, model-usage, gog, sag, 
              spotify-player, video-frames
Productivity: taskflow, taskflow-inbox-triage, healthcheck, gsd,
              close-loop, learning-loop, reflect, agent-evolver,
              skill-creator, github, gh-issues
Utility:      browser-use, linux-desktop, mcporter, comfyui,
              canva-connect, playwright, sherpa-onnx-tts, posthog
SDC Custom:   clone-service (nuevo, flujo completo de clon publicitario)
```

### 4.2 SDD Skills (archivos .skill.md)

| Skill | Archivo | Descripción |
|-------|---------|-------------|
| `deploy-code` | `skills/deploy-code.skill.md` | Automatización de deploys |
| `clone-service` | `skills/clone-service.skill.md` | Servicio de clon publicitario |
| `track-finance` | `skills/track-finance.skill.md` | Finanzas |
| `validate-quality` | `skills/validate-quality.skill.md` | Calidad |
| `capture-knowledge` | `skills/capture-knowledge.skill.md` | Conocimiento |
| `plan-strategy` | `skills/plan-strategy.skill.md` | Estrategia |
| `audit-security` | `skills/audit-security.skill.md` | Seguridad |
| `qualify-lead` | `skills/qualify-lead.skill.md` | Leads |
| `monitor-service` | `skills/monitor-service.skill.md` | Monitoreo |
| `resolve-ticket` | `skills/resolve-ticket.skill.md` | Tickets |
| `spawn-agent` | `skills/spawn-agent.skill.md` | Creación de agentes |

---

## 5. CLI Scripts (70+)

### 5.1 Productos

| Script | Descripción |
|--------|-------------|
| `scripts/clone_pipeline.py` | Pipeline completo de clon service (create-pack → validate → train → generate → status) |
| `scripts/pricing_engine.py` | Calculadora de pricing dinámico por industria/volumen/partner |
| `scripts/packages.py` | Muestra planes enterprise wholesale (--enterprise, --calculate-deal) |
| `scripts/commissions.py` | Tracking de deals y comisiones de partners |
| `scripts/demo_provision.py` | Crea demos de 7 días para cierre de ventas |
| `scripts/test_real_pipeline.py` | Test de pipeline real contra FAL.ai (costos reales) |
| `scripts/client_analyzer.py` | Análisis 3AM de clientes + sugerencias proactivas |
| `scripts/feed_memory.py` | Alimenta Engram, vectores y grafos con datos de sesión |
| `scripts/test_clone_flow.sh` | Test automatizado del flujo completo de clone service |
| `scripts/provision_tenant.py` | Provisiona tenant enterprise (crea Engram, bucket, Qdrant, Neo4j) |

### 5.2 Orquestación SDD

| Script | Descripción |
|--------|-------------|
| `scripts/constitution-gate.py` | 6-gate constitution check (Policy, Security, Cost, Compliance, Quality, Knowledge) |
| `scripts/close-session.sh` | Auto-doc + cleanup post-sesión |
| `scripts/auto-doc.py` | Generación automática de documentos SDD |
| `scripts/engram_autocapture.py` | Auto-captura de comandos, env, git, procesos → Engram |
| `scripts/engram_bashrc.sh` | Bash hooks para auto-capture |
| `scripts/plan-gate.py` | Planning Gate |
| `scripts/verify-gate.py` | Verification Gate |

### 5.3 DevOps

| Script | Descripción |
|--------|-------------|
| `scripts/up.sh` | Levanta todos los servicios Docker (core + products) |
| `scripts/down.sh` | Baja todos los servicios |
| `scripts/deploy.sh` | Deploy a GitHub Pages |
| `scripts/deploy-all.sh` | Abre 5 sistemas en Chrome kiosk |
| `scripts/sync-to-vps.sh` | Sync local → VPS (git push + rsync) |
| `scripts/backup.sh` | Backup de directorios (7-day retention) |
| `scripts/volume-backup.sh` | Backup de volúmenes Docker (14-day) |
| `scripts/secure-backup.sh` | Backup con secrets sanitizados |
| `scripts/healthcheck.sh` | Healthcheck del sistema |
| `scripts/git-sync.sh` | Pre-session git sync gate |
| `scripts/ssl-auto.sh` | SSL automation con Let's Encrypt |
| `scripts/setup-systemd.sh` | Instala servicios systemd |

### 5.4 Business Intelligence

| Script | Descripción |
|--------|-------------|
| `scripts/presentar.py` | Genera presentación reveal.js de la sesión |
| `scripts/weekly-executive-report.py` | Reporte ejecutivo semanal |
| `scripts/dashboard-salud.py` | Dashboard de salud del sistema |
| `scripts/monitor.py` | Monitor de servicios |
| `scripts/abe-daemon.py` | ABE Music daemon |
| `scripts/abe-telegram-bot.py` | ABE Telegram bot |
| `scripts/finops.sh` | FinOps (costos) |
| `scripts/social_automation.py` | Automatización de redes sociales |
| `scripts/seed-neo4j-arquitectura.py` | Seed Neo4j con arquitectura |
| `scripts/seed-qdrant.py` | Seed Qdrant con vectores |

---

## 6. Agentes OpenCode (20+)

### 6.1 Primary

| Agent | Modo | Rol | Tools Clave |
|-------|------|-----|-------------|
| **Mystic** | primary | Orquestador principal del sistema | read, edit, bash, glob, grep, task, webfetch, todowrite — TODO permitido |

### 6.2 SubAgentes Core

| Agent | Modo | Rol |
|-------|------|-----|
| **hermes** | subagent | Gateway multi-canal (Telegram, WhatsApp, Desktop) |
| **openclaw** | subagent | 55 skills especializadas (browser, payments, social, media) |
| **sdd** | subagent | SDD Orchestrator — coordina 6 fases |
| **sdd-spec** | subagent | Spec Agent — genera especificaciones SDD |
| **sdd-design** | subagent | Design Agent — crea plan.md + tasks.md |
| **sdd-apply** | subagent | Apply Agent — ejecuta implementación |
| **sdd-verify** | subagent | Verify Agent — constitution + checklist + tests |
| **sdd-archive** | subagent | Archive Agent — documenta resultados |

### 6.3 Operating Systems (10 OS)

| Agent | Rol | Área |
|-------|-----|------|
| **sales** | Sales OS | Lead gen, qualification, proposals, pipeline |
| **dev** | Dev OS | Software delivery, CI/CD, architecture, tests |
| **support** | Support OS | Tickets, SLAs, client satisfaction |
| **agent-os** | Agent OS | Harness lifecycle, skill registry, MCP governance |
| **knowledge** | Knowledge OS | 7-layer memory, ADRs, knowledge capture |
| **finance** | Finance OS | FinOps, revenue tracking, ROI, invoicing |
| **security** | Security OS | Secrets, audit, incident response, compliance |
| **ops** | Ops OS | Infrastructure, monitoring, recovery, scaling |
| **quality** | Quality OS | Test frameworks, process audits, evaluations |
| **strategy** | Strategy OS | Initiatives, enterprise score, quarterly planning |

### 6.4 Role-Specific

| Agent | Rol | Área |
|-------|-----|------|
| **builder** | Builder | Implementa features, escribe código, crea archivos |
| **reviewer** | Reviewer | Code review, seguridad, calidad |
| **social** | Social | Publica contenido en redes sociales |
| **content** | Content | Blogs, diseños, presentaciones, ghost CMS |
| **music** | Music | Beats, letras, portadas, distribución |

---

## 7. Agent Registry (9+1 agentes)

| Agent | Tenant | Role | Tools Clave | Triggers |
|-------|--------|------|-------------|----------|
| **creator-agent** | sdc | Build and deploy AI companies | lovable, hasura, upload, engram | command:/crear-empresa |
| **quality-agent** | sdc | Evaluate prompts and pipelines | llm, engram_search, rag | event:pipeline:end |
| **monitor-agent** | sdc | System self-care | engram_save, telegram_notify | cron:*/5 |
| **ceo-agent** | abe-music | Business owner | hasura, engram, rag, llm | command:/dashboard |
| **marketing-agent** | abe-music | Brand strategy | rag, llm, engram, firecrawl | cron:08:00 |
| **content-agent** | abe-music | Content factory | rag, llm, video, tts, whisper | cron:06:00 |
| **sales-agent** | abe-music | Sell products | stripe, supabase, engram | event:stripe |
| **support-agent** | abe-music | Customer service | rag, engram, llm, omnivoice | event:ticket:new |
| **voice-agent** | abe-music | Voice interface | omnivoice, whisper, llm, rag | always:available |
| **clone-agent** 🆕 | **sdc** | **Clone publicitario** | **validate,train,clone,gen,credit** | **event:clone:** |

---

## 8. Pipelines (10)

| # | Pipeline | Script/Server | Tests | Estado |
|---|----------|---------------|-------|--------|
| 1 | **Reception** — Recibir fotos/audio del cliente | `lora_mcp.py`, `voice_clone_mcp.py` | 16 | ✅ |
| 2 | **Training** — Entrenar LoRA + clonar voz | `lora_mcp.py`, `voice_clone_mcp.py` | 11 | ✅ |
| 3 | **Generation** — Generar fotos/videos/TTS | `generate_mcp.py` | 18 | ✅ |
| 4 | **Delivery** — FFmpeg + Supabase upload | `ffmpeg_mcp.py` | 11 | ✅ |
| 5 | **Credits** — Consumir créditos por asset | `credit_mcp.py`, `clone_pipeline.py` | 12 | ✅ |
| 6 | **Cost Intelligence** — Track costos reales | `cost_tracker_mcp.py` | 12 | ✅ |
| 7 | **Pricing** — Pricing dinámico | `pricing_mcp.py`, `pricing_engine.py` | 14 | ✅ |
| 8 | **Provisioning** — Multi-tenant <5s | `provision_mcp.py`, `provision_tenant.py` | 17 | ✅ |
| 9 | **Commissions** — Deals + partner markup | `commissions_mcp.py`, `commissions.py` | 13 | ✅ |
| 10 | **Security** — Prompt filter + URL + FFmpeg | `prompt_filter.py`, `url_validator.py` | 64 | 🆕 |
| | **TOTAL** | | **215** | ✅ |

**Meta-pipeline**: SDD (SPEC → Gherkin → TDD → Implementation)

---

## 9. Bases de Datos

### 9.1 Mapa Completo

| DB | Tipo | Localización | Propósito | Tamaño Est. |
|----|------|-------------|-----------|-------------|
| PostgreSQL 15 | Relacional | VPS (:5432) | Datos core del sistema | ~2GB |
| Engram | SQLite WAL | Local (~/.engram/) | Memoria persistente (360+ obs) | ~8MB |
| Clone Service | SQLite | Local (data/) | Créditos, clientes, assets | ~1MB |
| Cost Tracker | SQLite | Local (data/) | Costos reales por operación | ~1MB |
| Tenants | SQLite | Local (data/) | Partners y clientes enterprise | ~1MB |
| Commissions | SQLite | Local (data/) | Deals, comisiones, proyecciones | ~1MB |
| Vector Memory | SQLite | Local (data/) | 71 entries, búsqueda semántica | ~1MB |
| Graph Memory | SQLite | Local (data/) | 71 nodes, 665 edges, relaciones | ~1MB |
| Demo | SQLite | Local (data/) | Demos de 7 días | ~1MB |
| Qdrant | Vectorial | VPS (:6333) | Búsqueda semántica | ~300MB |
| Neo4j 5.19 | Grafo | VPS (:7687) | Relaciones entre entidades | ~500MB |
| Redis 7 | KV/Cache | VPS (:6379) | Caché, colas, rate limits | ~100MB |

### 9.2 Esquemas SQLite

```
data/clone_service.db:    clients, photos, audio, assets
data/cost_tracker.db:     cost_log
data/tenants.db:          tenants, partners
data/commissions.db:      partners, deals, payments
data/vector_memory.db:    vectors
data/graph_memory.db:     nodes, edges
data/demo.db:             demos
```

---

## 10. Infraestructura

### 10.1 Máquinas

| Máquina | IP | OS | RAM | Rol |
|---------|-----|-----|-----|-----|
| **sdc-prod** (OVH VPS) | `149.56.46.173` | Ubuntu 26.04 | 11GB | Servidor principal (producción) |
| **mysticpc** (Local) | Dinámica (MX) | Linux | — | Desarrollo (Luis Daniel) |

### 10.2 Puertos Clave

| Puerto | Servicio | Container |
|--------|----------|-----------|
| 18789 | OpenClaw Gateway | systemd |
| 18989 | MCP Gateway | systemd |
| 7437 | Engram | systemd |
| 5432 | PostgreSQL | Docker |
| 7687 | Neo4j Bolt | Docker |
| 7474 | Neo4j HTTP | Docker |
| 6333 | Qdrant HTTP | Docker |
| 6334 | Qdrant gRPC | Docker |
| 6379 | Redis | Docker |
| 5678 | n8n | Docker |
| 3000 | LangFuse | Docker |
| 8000 | Hermes MCP | Docker |
| 3900 | OmniVoice | Docker |
| 8765 | Content Server | Docker |
| 8766 | Edge TTS | Docker |
| 9090 | WhatsApp WACLI | Docker |
| 11434 | Ollama | systemd |

### 10.3 Docker Volumes

```
pg_data · redis_data · neo4j_data · neo4j_logs
qdrant_storage · qdrant_snapshots · n8n_data
langfuse_data · openclaw_config · openclaw_extensions
openclaw_memory · engram_data · voice_models
wacli_data · wacli_media · omnivoice_data
```

---

## 11. Memorias

| Sistema | Tipo | Datos | Acceso |
|---------|------|-------|--------|
| **Engram** | SQLite WAL | 360+ obs, 319 sesiones, 126 prompts | MCP (agent profile) |
| **Vector Memory** | SQLite | 71 entries, 5 categorías | `feed_memory.py --search` |
| **Graph Memory** | SQLite | 71 nodes, 665 edges | `feed_memory.py --query-graph` |
| **Qdrant** | Vectorial | Embeddings semánticos | VPS (:6333) |
| **Neo4j** | Grafo | Relaciones | VPS (:7687) |
| **Obsidian** | Markdown | People, Decisions, Projects, etc | `~/Documents/sdc-brain-vault/` |

### Categorías de Memoria

| Categoría | Entradas | Descripción |
|-----------|----------|-------------|
| code | 31 | MCP servers, scripts, pipelines, tests |
| architecture | 17 | SPECs, ADRs, configs técnicas |
| pipeline | 10 | Gherkin, BDD features |
| business | 5 | Pricing, packages, ambassadors, margen |
| security | 4 | Prompt filter, URL validator, FFmpeg sanitizer |

---

## 12. Seguridad

### 12.1 Capas de Defensa

| Capa | Herramienta | Protege Contra |
|------|-------------|----------------|
| **Prompt filter** | `common/security/prompt_filter.py` | 50+ patrones de prompt injection |
| **URL validator** | `common/security/url_validator.py` | SSRF (localhost, privadas, metadata) |
| **FFmpeg sanitizer** | `common/security/ffmpeg_sanitizer.py` | Filter injection via watermark |
| **Shell injection** | `infra/mcp-server/server.py` | shell=False, shlex, metachar check |
| **Neo4j auth** | `docker-compose.yml` | auth__enabled=true |
| **Pre-commit hook** | `.githooks/pre-commit` | Secrets antes de commit |
| **File permissions** | chmod 600 | .env, openclaw.json |
| **.gitignore** | `.gitignore` | .env, .key, .pem, credentials |

### 12.2 Auditoría

```
31 vulnerabilidades encontradas → 8 críticas, 8 altas, 10 medias, 5 bajas
215 tests de seguridad
Prompt injection bloqueado: 50+ patrones críticos/altos/medios
```

---

## 13. Productos

### 13.1 Catálogo

| Producto | Precio Wholesale | Descripción |
|----------|-----------------|-------------|
| **Clone Service** | $2,500-15,000/mes | Clonación facial y vocal para marketing |
| **Digital Brain** | $5,000-15,000/mes | Memoria corporativa persistente |
| **Enterprise Platform** | $2,500-15,000/mes | Multi-tenant white-label para partners |
| **WhatsApp Automation** | $49-299/mes | Chatbot AI + onboarding + broadcasting |
| **Social Media Auto** | $49/mes (add-on) | Publicación automática multi-plataforma |

### 13.2 Planes Enterprise

| Plan | Setup | Monthly | Ideal para |
|------|-------|---------|------------|
| Medium | $1,500+ | $5,000/mes | Empresas 10-30 empleados |
| Premium ⭐ | $2,500+ | $7,500/mes | Empresas 30-200 empleados |
| Enterprise | $5,000+ | $15,000/mes | 200+ empleados o corporativos |

### 13.3 Planes WhatsApp

| Plan | Setup | Monthly | Ideal para |
|------|-------|---------|------------|
| Starter | $99 | $49/mes | Pequeños negocios |
| Pro ⭐ | $199 | $99/mes | PYMES, tiendas online |
| Enterprise | $499 | $299/mes | Empresas, agencias |

---

## 14. Alias de Shell

```bash
# Clone Service
clone-test        → pytest tests/test_clone_*.py -q
clone-flow        → bash test_clone_flow.sh
clone-quantum     → Abre presentación cuántica en Firefox
clone-ls          → Lista archivos del clon
clone-spec        → Lee la SPEC
clone-help        → Lista comandos
clone-status X    → Estado del cliente X

# Digital Brain
brain-sync        → Engram → Obsidian + Google Drive
brain-open        → Obsidian AppImage
brain-status      → Estado del cerebro

# Sistema
sdc-status        → Verificar repo correcto
mystic-status     → System overview
```

---

**Blueprint generado por Mystic (SDC Orchestrator) — 2026-07-18**
**215 tests · 23 MCP servers · 70+ scripts · 20+ agents · 10 pipelines**
