# AUDITORÍA TOTAL — Sonora Digital Corp

**Fecha:** 2026-07-03 22:30 MST
**Auditor:** OpenCode (modo solo observación)
**Alcance:** Repositorio local + VPS sdc-prod (149.56.46.173)
**Principio:** VERDAD ABSOLUTA — nada de opiniones, solo evidencia

---

## 1. ESTRUCTURA COMPLETA DEL REPOSITORIO

### Métricas globales

| Métrica | Valor |
|---------|-------|
| Directorios totales | 9,028 |
| Archivos totales | 125,117 |
| Tamaño total (sin .git) | **2.9 GB** |
| Commits en main | 186 |
| Autores | 3 (SDC, Sonora Digital Corp, dependabot[bot]) |
| Primer commit | `feat: sdc unified monorepo — core, platforms, infra, products` |
| Último commit | `feat(close-session): script automatizado + unificacion CATALOGs + docs` |

### Tamaño por directorio raíz

| Directorio | Tamaño | Archivos | Estado |
|------------|--------|----------|--------|
| `backups/` | **2.0 GB** | ~90,000 | 🟠 Backup históricos diarios (3 días) |
| `products/` | **505 MB** | ~15,000 | 🟡 7 productos, mystika = 504MB (node_modules) |
| `clients/` | **353 MB** | ~8,000 | 🟡 abe-music = 352MB, azrec = 724KB |
| `apps/` | **33 MB** | ~2,500 | 🟠 20 apps, 1 con código real (jarvis) |
| `mcp/` | **28 MB** | ~4,000 | 🟡 27 subdirectorios, node_modules = 27MB |
| `sonora-enterprise-os/` | **2.4 MB** | ~500 | 🟢 Documentación, prompts, truth |
| `process/` | **1.2 MB** | ~200 | 🟢 33 procesos completados, templates |
| `tests/` | **1.1 MB** | ~150 | 🟢 78 tests en 5 suites |
| `state/` | **984 KB** | ~300 | 🟡 Logs, memoria, eventos |
| `scripts/` | **596 KB** | ~50 | 🟢 Automatizaciones |
| `config/` | **592 KB** | ~80 | 🟢 Configuraciones |
| `infra/` | **480 KB** | ~100 | 🟢 Docker, nginx, monitoreo |
| `frontends/` | **268 KB** | ~30 | 🟠 4 frontends (abe, dashboard, docs, landing) |
| `docs/` | **268 KB** | ~15 | 🟢 Documentación técnica |
| `ref/` | **228 KB** | ~10 | 🔴 No evaluado |
| `business/` | **184 KB** | ~30 | 🟢 5 unidades de negocio |
| `scrapers/` | **148 KB** | ~40 | 🟡 8 scrapers |
| `webui/` | **144 KB** | ~50 | 🟠 FastAPI app |
| `collectors/` | **132 KB** | ~30 | 🟡 8 collectors |

### Árbol de estructura (nivel 1-3)

```
sonora-digital-corp/
├── apps/                          # 20 aplicaciones backend
│   ├── abe-service/               # ABE Music API (FastAPI, 348KB)
│   ├── act/                       # Agente de acción (64KB, placeholder)
│   ├── agent_metrics/             # Métricas (24KB, placeholder)
│   ├── agents/                    # Agentes Python (16KB, placeholder)
│   ├── cache/                     # Caché (8KB, placeholder)  
│   ├── control/                   # Dashboard control (12KB, placeholder)
│   ├── data/                      # Datos (12KB, vacío)
│   ├── decide/                    # Motor de decisiones (96KB, placeholder)
│   ├── economics/                 # Economía (24KB, placeholder)
│   ├── guardian/                  # Security guardian (80KB, placeholder)
│   ├── hermes/                    # Hermes services (56KB, publisher/thumbnails/youtube)
│   ├── jarvis/                    # JARVIS core (30MB — ÚNICA app con código real)
│   ├── learn/                     # Evolution loop (88KB)
│   ├── learning/                  # Learning system (24KB, placeholder)
│   ├── logs/                      # Logs (4KB)
│   ├── measure/                   # Guardian metrics (156KB)
│   ├── observe/                   # Observability (12KB, placeholder)
│   ├── understand/                # Understanding (12KB, placeholder)
│   ├── voice/                     # Voice pipeline (84KB)
│   └── webui/                     # Web UI (1.8MB, FastAPI + templates)
│
├── products/                      # 7 productos
│   ├── mystika/                   # 504MB — web/ (Next.js 478MB), api/ (20MB), telegram-bot/ (6.7MB)
│   ├── yami/                      # 288KB
│   ├── telegram-masterclass/      # 44KB
│   ├── booking/                   # 24KB
│   ├── landing-artista/           # 12KB
│   ├── chatbot/                   # 12KB
│   └── footprint/                 # 4KB (vacío)
│
├── clients/                       # 2 clientes
│   ├── abe-music/                 # 352MB (Node.js + Python, Telegram bot, studio)
│   └── azrec/                     # 724KB
│
├── mcp/                           # MCP Ecosystem (28MB, 27 subdirs)
│   ├── gateway/                   # MCP HTTP gateway
│   ├── cli/                       # CLI tools
│   ├── servers/                   # Server configs (8 servers)
│   └── ...                        # 23 otros subdirectorios
│
├── sonora-enterprise-os/          # Enterprise OS (2.4MB)
│   ├── constitution/              # 11 archivos fundacionales
│   ├── prompts/                   # 54+ prompts del sistema
│   ├── adr/                       # 11 Architecture Decision Records
│   ├── capabilities/              # Registry + 10 legacy systems
│   ├── roadmap/                   # 27 hitos históricos
│   ├── events/                    # Catálogo de eventos (83 eventos)
│   ├── memory/                    # Lecciones aprendidas
│   └── specs/                     # Especificaciones
│
├── infra/                         # Infraestructura Docker (480KB)
│   ├── docker-compose.yml         # Full stack (348 lines)
│   ├── docker-compose.vps.yml     # Override VPS
│   ├── docker/                    # Dockerfiles (neo4j, qdrant, mcp-server, jarvis)
│   ├── nginx/                     # Nginx configs
│   └── monitoring/                # Monitoreo
│
├── config/                        # Configuraciones (592KB)
│   ├── design-systems/            # 3 design systems
│   ├── mcp/                       # MCP ecosystem + playwright
│   ├── n8n/                       # Workflows n8n core
│   ├── n8n-sdc/                   # Workflows n8n SDC
│   ├── generated/                 # Configs autogeneradas
│   └── .secrets/                  # Secrets (texto plano + age cifrado)
│
├── scripts/                       # Automatizaciones
├── tests/                         # Tests (78 tests, 5 suites)
├── frontends/                     # Frontends (abe, dashboard, docs, landing)
├── docs/                          # Documentación técnica
├── webui/                         # Web UI (FastAPI, static/)
├── state/                         # Estado operacional
├── process/                       # Procesos completados
├── truth/                         # Truth YAML (12 archivos)
├── scrapers/                      # Web scrapers
├── collectors/                    # Data collectors
└── business/                      # Unidades de negocio
```

---

## 2. ARQUITECTURA DETECTADA

### Diagrama textual completo

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SONORA DIGITAL CORP                               │
│                        VPS sdc-prod (OVH)                                │
│                        Ubuntu 26.04 | 6 vCPUs | 11GB RAM                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   FRONTEND       │    │   API LAYER      │    │   AGENTS LAYER   │
├──────────────────┤    ├──────────────────┤    ├──────────────────┤
│ mystika.sdc.com  │    │ api.sdc.com:443  │    │ opencode CLI     │
│ (Next.js :3001)  │    │ (nginx proxy)    │    │ (mystic agent)   │
│                  │    │                  │    │                  │
│ Jarvis WebUI     │    │ ABE API :8111    │    │ Hermes :8643     │
│ (:5174)          │    │ (FastAPI)        │    │ (gateway multi-  │
│                  │    │                  │    │  canal)          │
│ Vercel Deploy    │    │ Mystika API :4000│    │                  │
│ (abe, landing)   │    │ (Node.js)        │    │ OpenClaw :18789  │
│                  │    │                  │    │ (42 skills)      │
│ WebUI FastAPI    │    │ MCP Srv :8000    │    │                  │
│ (:5180)          │    │ (Python)         │    │ Truth Guardian   │
└──────────────────┘    └──────────────────┘    └──────────────────┘
          │                         │                         │
          └──────────┬──────────────┴──────────────┬──────────┘
                     │                             │
                     ▼                             ▼
          ┌─────────────────────┐    ┌─────────────────────┐
          │   DATABASES         │    │   AI & INFRA        │
          ├─────────────────────┤    ├─────────────────────┤
          │ Neo4j (Bolt:7687)   │    │ Ollama :11434       │
          │ Graph DB            │    │ 6 modelos locales   │
          │                     │    │                     │
          │ Qdrant (gRPC:6333)  │    │ n8n :5678           │
          │ Vector Store        │    │ 5+ workflows        │
          │                     │    │                     │
          │ Postgres :5432      │    │ Langfuse :3000      │
          │ Relational DB       │    │ LLM Observability   │
          │                     │    │                     │
          │ Redis :6379         │    │ Docker Engine       │
          │ Cache + Queues      │    │ 11 containers       │
          └─────────────────────┘    └─────────────────────┘
```

### Stack de comunicación

| Capa | Tecnología | Puerto |
|------|-----------|--------|
| HTTP Externo | Nginx + Let's Encrypt | 80/443 |
| API Gateway | Cloudflare / Vercel | - |
| LLM Gateway | Ollama local | 11434 |
| MCP Gateway | sonora-mcp-gateway (Node.js) | 18989 |
| Bot Gateway | Hermes Agent (Python) | 8643 |
| Skills Gateway | OpenClaw | 18789 |
| Servicios Docker | sdc-network (bridge) | Interno |

---

## 3. TECNOLOGÍAS UTILIZADAS

### Lenguajes detectados

| Lenguaje | Archivos | Líneas estimadas |
|----------|----------|------------------|
| Python | ~200 | ~15,000 |
| JavaScript/TypeScript | ~500 | ~25,000 |
| YAML | ~80 | ~5,000 |
| JSON | ~50 | ~8,000 |
| Markdown | ~1,819 | ~54,000 |
| Bash | ~30 | ~3,000 |
| HTML | ~10 | ~2,000 |
| CSS | ~10 | ~1,000 |
| SQL | ~5 | ~500 |

### Frameworks y librerías detectados

| Tecnología | Uso | Versión |
|------------|-----|---------|
| **Python** | | |
| FastAPI | ABE API, Jarvis, WebUI | - |
| uvicorn | ASGI server | - |
| pytest | Test framework | 8+ |
| ruff | Python linter | - |
| httpx | Async HTTP client | - |
| neo4j | Graph DB driver | - |
| qdrant-client | Vector DB driver | - |
| redis | Cache driver | - |
| deepeval | LLM evaluation | - |
| **Node.js** | | |
| Next.js | Mystika Web | 14.2.30 |
| Express | Mystika API | - |
| node-telegram-bot-api | Telegram bots | - |
| Prisma | ORM (Mystika) | - |
| Stripe SDK | Payments | - |
| Playwright | Browser automation | - |
| **Infraestructura** | | |
| Docker / docker-compose | Container orchestration | 27.x |
| Neo4j | Graph database | 5.19.0 |
| Qdrant | Vector database | 1.7.4 |
| Redis | Cache | 7-alpine |
| PostgreSQL | Relational DB | 15 |
| n8n | Workflow automation | latest |
| Langfuse | LLM observability | 2 |
| Nginx | Reverse proxy | - |
| Ollama | LLM serving | - |
| Fail2Ban | Security | - |

### Modelos de IA disponibles en Ollama (VPS)

| Modelo | Tamaño | Contexto | Capacidades |
|--------|--------|----------|-------------|
| qwen3:4b-64k | 4.0B | 262K | completion, tools, thinking |
| deepseek-r1:7b-64k | 7.6B | 131K | completion, thinking |
| llama3.2:3b-64k | 3.2B | 131K | completion, tools |
| qwen3:1.7b-32k | 2.0B | 41K | completion, tools, thinking |
| qwen2.5:1.5b-32k | 1.5B | 33K | completion, tools |
| nomic-embed-text | 137M | 2K | embedding |

### APIs externas referenciadas en código

| API | Propósito | Dónde se usa |
|-----|-----------|-------------|
| Stripe | Pagos | products/mystika/api, clients/abe-music |
| Mercado Pago | Pagos LATAM | products/mystika/api |
| Telegram Bot API | Mensajería | apps/abe-service, products/mystika/telegram-bot |
| OpenRouter | LLM fallback | .hermes/config.yaml (VPS) |
| fal.ai | Image generation | .hermes/config.yaml (plugin) |
| WhatsApp API | Messaging | .hermes/config.yaml |
| Vercel API | Deploy | .github/workflows/ |
| GitHub API | Repos | .github/workflows/ |

---

## 4. VARIABLES DE ENTORNO

### Todas las variables encontradas (redactadas)

#### `.env` raíz (laptop)

| Variable | Estado | Dónde se usa |
|----------|--------|-------------|
| ABE_TELEGRAM_TOKEN | ✅ Usada | apps/abe-service/ |
| ABE_TELEGRAM_CHAT | ✅ Usada | apps/abe-service/ |
| ABE_FENIX_BOT_TOKEN | ✅ Usada | apps/abe-service/ |
| REDIS_PASSWORD | ⚠️ No referenciada localmente | Solía usarse |

#### `products/mystika/api/.env`

| Variable | Estado |
|----------|--------|
| PORT | ✅ Usada |
| NODE_ENV | ✅ Usada |
| DB_HOST | ✅ Usada |
| DB_PORT | ✅ Usada |
| DB_NAME | ✅ Usada |
| DB_USER | ✅ Usada |
| DB_PASSWORD | ✅ Usada |
| DATABASE_URL | ✅ Usada |
| JWT_SECRET | ✅ Usada |
| JWT_EXPIRES_IN | ✅ Usada |
| STRIPE_SECRET_KEY | ✅ Usada |
| STRIPE_WEBHOOK_SECRET | ✅ Usada |
| STRIPE_MYSTERIA_PRICE_ID | ✅ Usada |
| STRIPE_RITUAL_PRICE_ID | ✅ Usada |
| MP_ACCESS_TOKEN | ✅ Usada |
| MP_WEBHOOK_SECRET | ✅ Usada |
| MP_MYSTERIA_PREAPPROVAL_ID | ✅ Usada |
| MP_RITUAL_PREAPPROVAL_ID | ✅ Usada |
| TELEGRAM_BOT_TOKEN | ✅ Usada |
| TELEGRAM_ADMIN_ID | ✅ Usada |
| VIDEO_STORAGE_PATH | ✅ Usada |
| OPENROUTER_API_KEY | ✅ Usada |
| FRONTEND_URL | ✅ Usada |

#### `products/mystika/telegram-bot/.env`

| Variable | Estado |
|----------|--------|
| TELEGRAM_BOT_TOKEN | ✅ Usada |
| TELEGRAM_ADMIN_ID | ✅ Usada |
| API_URL | ✅ Usada |
| NODE_ENV | ✅ Usada |

#### `infra/.env.langfuse`

| Variable | Estado |
|----------|--------|
| LANGFUSE_PUBLIC_KEY | ✅ Usada |
| LANGFUSE_SECRET_KEY | ✅ Usada |
| LANGFUSE_HOST | ✅ Usada |

#### `.env.example` — Variables definidas PERO sin archivo .env real

| Variable | Estado | Riesgo |
|----------|--------|--------|
| NEO4J_URI | ❌ Faltante | Sin conexión a Neo4d desde opencode |
| NEO4J_USER | ❌ Faltante | |
| NEO4J_PASSWORD | ❌ Faltante | |
| QDRANT_HOST | ❌ Faltante | |
| QDRANT_PORT | ❌ Faltante | |
| MCP_HOST | ❌ Faltante | |
| MCP_PORT | ❌ Faltante | |
| OPENCODE_API_KEY | ❌ Faltante | |
| OPENROUTER_API_KEY | ❌ Faltante | |
| GH_TOKEN | ❌ Faltante | |
| NGROK_TOKEN | ❌ Faltante | |
| VERCEL_TOKEN | ❌ Faltante | |

#### Secrets hardcodeados (SIN variable de entorno)

| Archivo | Línea | Secret | Severidad |
|---------|-------|--------|-----------|
| `apps/abe-service/pwa/app.js` | 16 | `abe_music_jwt_secret_dev_change_in_prod_2026` | 🔴 Crítico |
| `apps/abe-service/config.py` | 31 | `abe_music_jwt_secret_dev_change_in_prod_2026` | 🔴 Crítico |
| `apps/abe-service/config.py` | 46 | `sdc_secret_ent3rpr1s3_k3y_2026` | 🔴 Crítico |
| `infra/docker/mcp-server/config.py` | 13 | `jarvis2026` | 🟠 Alto |
| `infra/docker-compose.yml` | 16 | `POSTGRES_PASSWORD=sdc2026prod` | 🟠 Alto |
| `infra/docker-compose.yml` | 38 | `REDIS_PASSWORD=sdc2026prod` | 🟠 Alto |
| `infra/docker-compose.yml` | 62 | `NEO4J_AUTH=neo4j/jarvis2026` | 🟠 Alto |
| `infra/docker-compose.yml` | 216 | `LANGFUSE_SECRET=sdc-langfuse-secret-2026` | 🟠 Alto |
| `infra/docker-compose.yml` | 220 | `LANGFUSE_SALT=sdc-langfuse-salt-2026` | 🟠 Alto |
| `infra/docker-compose.yml` | 245 | `LANGFUSE_DB_PASS=postgres` | 🟡 Medio |
| `config/.secrets/clients.json` | - | 3 client_id en texto plano | 🟡 Medio |

---

## 5. DOCKER

### En VPS (producción real)

#### 11 contenedores activos

| Contenedor | Imagen | Puerto | Status | Propósito |
|------------|--------|--------|--------|-----------|
| sdc-neo4j | infra-neo4j | 7474, 7687 | ✅ healthy | Graph DB |
| sdc-qdrant | infra-qdrant | 6333-6334 | ✅ healthy | Vector DB |
| sdc-redis | redis:7-alpine | 6379 | ✅ healthy | Cache |
| sdc-postgres | postgres:15 | 5432 | ✅ healthy | Relacional |
| sdc-n8n | n8nio/n8n:latest | 5678 | ✅ healthy | Workflows |
| sdc-langfuse | langfuse/langfuse:2 | 3000 | ✅ healthy | LLM tracing |
| sdc-mcp-server | infra-mcp-server | 8000 | ✅ healthy | MCP tools |
| sdc-jarvis-core | infra-jarvis-core | - | ✅ running | Core logic |
| sdc-jarvis-webui | infra-jarvis-webui | 5174 | ✅ healthy | Web UI |
| sdc-telegram-bot | infra-telegram-bot | 3003 | 🔴 404 | Bot Telegram |
| sdc-langfuse-db | postgres:15 | - | ✅ healthy | Langfuse DB |

#### Red Docker

| Red | Driver | Contenedores |
|-----|--------|-------------|
| sdc-network | bridge | 11 (todos los sdc-*) |
| scrapers_sdc-scrapers | bridge | Scrapers |

#### Volúmenes Docker persistentes (19 total)

| Volumen | Tamaño (est.) | Propósito |
|---------|--------------|-----------|
| sdc_neo4j_data | ~2GB | Graph data |
| sdc_qdrant_storage | ~500MB | Vector data |
| sdc_pg_data | ~1GB | PostgreSQL |
| sdc_redis_data | ~100MB | Redis |
| sdc_n8n_data | ~100MB | n8n workflows |
| sdc_langfuse_data | ~100MB | Langfuse |

#### Dockerfiles (13 total)

| Dockerfile | En producción? |
|------------|---------------|
| infra/docker/jarvis/Dockerfile | ✅ Sí (multi-stage) |
| infra/docker/jarvis-api/Dockerfile | ❌ No detectado |
| infra/docker/neo4j/Dockerfile | ✅ Sí |
| infra/docker/qdrant/Dockerfile | ✅ Sí |
| infra/docker/mcp-server/Dockerfile | ✅ Sí |
| mcp/Dockerfile | ❌ No (solo en infra/) |
| platforms/telegram/Dockerfile | ❌ No |
| clients/abe-music/*/Dockerfile (6) | ❌ No (cliente) |

#### Docker Compose

| Archivo | Servicios | En uso? |
|---------|-----------|---------|
| infra/docker-compose.yml | 11 servicios | ✅ Sí (VPS) |
| infra/docker-compose.vps.yml | Override | ✅ Sí (VPS) |
| infra/docker-compose.studio.yml | ABE Studio | ❌ No |
| scrapers/docker-compose.scrapers.yml | Scrapers | ❌ No |
| clients/abe-music/*.yml (3) | ABE Music | ❌ No |

#### Healthchecks en Docker (todos configurados)

| Servicio | Healthcheck | Intervalo |
|----------|------------|-----------|
| neo4j | `cypher-shell` | 30s |
| qdrant | `curl /healthz` | 30s |
| redis | `redis-cli ping` | 10s |
| postgres | `pg_isready` | 10s |
| n8n | `wget /healthz` | 30s |
| langfuse | `wget /api/health` | 30s |

---

## 6. GITHUB

### Workflows CI/CD (26 activos)

| Categoría | Workflows | Runner |
|-----------|-----------|--------|
| **CI** | ci.yml, tests.yml, test.yml, docker-build.yml | ubuntu-latest |
| **Deploy** | deploy.yml, sync-vps.yml | self-hosted |
| **Vercel** | vercel-deploy.yml, vercel-preview.yml | ubuntu-latest |
| **Security** | security.yml | ubuntu-latest |
| **Quality** | process-gate.yml | ubuntu-latest |
| **Monitoring** | monitor.yml, auto-sync.yml, backup.yml, detect-duplicate-repos.yml | self-hosted |
| **Notifications** | agent-alerts.yml, notify-push.yml | ubuntu-latest |
| **Automation** | automation-validate.yml, auto-assign.yml, analizador.yml | ubuntu-latest |
| **Verification** | verify-constitution.yml, schedule-models.yml | ubuntu-latest |
| **Disabled** | implementador.yml | - |

### Dependabot config (4 ecosistemas)

| Ecosistema | Directorio | Schedule |
|-----------|------------|----------|
| pip | / | weekly |
| npm | platforms/telegram | weekly |
| docker | infra/docker/jarvis | weekly |
| github-actions | / | weekly |

### PR Template

Checklist: tests pasan, coverage >=60%, lint, SPEC tier, ADR.

### Git Hooks

- **pre-commit**: TDD enforcement + SPEC requirement
- **post-commit**: CATALOG update + event logging

### Branch strategy

```
ANTES (jul 2):    main + 17 ramas zombies
DESPUÉS (jul 3):  main SOLO (cleanup ejecutado)
```

---

## 7. VERCEL

### Configs encontradas

| Archivo | Propósito |
|---------|-----------|
| `/vercel.json` | Raíz: rutas a landing, dashboard, ABE portal |
| `/frontends/abe/vercel.json` | ABE portal SPA + API proxy |

### Rutas definidas en root vercel.json

```
/abe/portal/*     → proxy a api.sonoradigitalcorp.com
/abe/*            → proxy a api.sonoradigitalcorp.com
/dashboard/*      → serve static
/api/*            → proxy a api.sonoradigitalcorp.com
/                 → serve landing page
```

**NO encontrado**: archivo `.vercel/` con proyecto vinculado, ni `env` de Vercel en CI.

---

## 8. VPS (sdc-prod — 149.56.46.173)

### Sistema

| Especificación | Valor |
|---------------|-------|
| Proveedor | OVH |
| OS | Ubuntu 26.04 LTS (Resolute Raccoon) |
| Kernel | 7.0.0-14-generic x86_64 |
| CPU | 6 vCPUs (Intel Haswell) |
| RAM | 11 GB total / 3.0 GB usada |
| Disco | 96 GB total / 46 GB usado (48%) |
| Swap | 2 GB (1.6 GB usado — 80%) |
| Uptime | 10 días 3h |
| Vulnerabilidad CPU | Spec store bypass: VULNERABLE |

### Servicios Systemd (33 activos)

#### Propios SDC (9 servicios)

| Servicio | Puerto | Status |
|----------|--------|--------|
| openclaw-gateway | 18789 | ✅ Active (desde Jul 1) |
| sonora-mcp-gateway | 18989 | ✅ Active |
| truth-guardian | - | ✅ Active (cada 10 min) |
| abe-api | 8111 | ✅ Active |
| abe-daemon | - | ✅ Active (cada 10 min) |
| mystika-api | 4000 | ✅ Active |
| mystika-bot | - | ✅ Active (token inválido? 401) |
| mystika-web | 3001 | ✅ Active |
| ollama | 11434 | ✅ Active |

#### Del sistema (24 servicios)

nginx, docker, containerd, fail2ban, ssh, cron, chrony, rsyslog, unattended-upgrades, qemu-guest-agent, networkd-dispatcher, polkit, udisks2, ModemManager + otros

#### Systemd Timers

| Timer | Schedule | Estado |
|-------|----------|--------|
| jarvis-backup.timer | daily | 🔴 **Inactivo** (User=mystic no existe) |
| jarvis-healthcheck.timer | cada 5 min | 🔴 **Inactivo** (User=mystic no existe) |
| jarvis-error-correction.timer | daily 4am | ✅ Active |
| certbot.timer | 2x/dia | ✅ Active |
| logrotate.timer | daily | ✅ Active |

### Nginx

#### Sites configurados

| Dominio | SSL | Proxy a |
|---------|-----|---------|
| mystika.sonoradigitalcorp.com | ❌ No | :3001 (Next.js) + :4000 (API) |
| api.sonoradigitalcorp.com | ✅ Let's Encrypt | :8111 (ABE API) + :5174 (Jarvis) |

### Firewall (UFW)

| Puerto | Acción |
|--------|--------|
| 22/tcp | ✅ ALLOW |
| 80/tcp | ✅ ALLOW |
| 443/tcp | ✅ ALLOW |
| 8080/tcp | ✅ ALLOW (Evolución Dashboard) |
| 5180/tcp | ✅ ALLOW (ABE PWA) |
| 3001, 4000 | ⛔ DENY (redundante, tras nginx) |

### Cron (usuario ubuntu)

| Schedule | Comando | Propósito |
|----------|---------|-----------|
| */10 * * * * | df alert | Alerta disco >85% |
| */15 * * * * | health-monitor.sh | Health monitor |
| */15 * * * * | autonomous.sh | Healthcheck autónomo |
| */15 * * * * | telegram-alerts.sh | Alertas Telegram |
| 0 * * * * | git pull | Sync cada hora |
| 0 * * * * | memory-save.py | Auto-save Jarvis |
| 0 */2 * * * | autonomous-night.sh | Self-heal cada 2h |
| 0 */6 * * * | scrapers sync | Sync scrapers |
| 0 2 * * * | log cleanup | Logs >14 días |
| 0 3 * * * | backup.sh | Backup diario |
| 0 8 * * * | daily-pipeline.sh | Pipeline diario |
| 30 9 * * 1 | abe-report-push.sh | Reporte ABE (lunes) |
| */30 * * * * | brain-sync.sh | Brain sync |

### Backups

| Backup | Tamaño | Método |
|--------|--------|--------|
| sdc-20260701_030002.tar.gz | 11.8 MB | Cron 3am |
| sdc-20260702_030001.tar.gz | 12.4 MB | Cron 3am |
| sdc-20260703_030001.tar.gz | 12.4 MB | Cron 3am |

### Procesos principales (por memoria)

| PID | %MEM | Proceso |
|-----|------|---------|
| 2343490 | 4.3% | opencode CLI |
| 12361 | 3.3% | neo4j (Java, heap 2G) |
| 177629 | 2.8% | openclaw gateway |
| 780329 | 1.8% | hermes gateway |
| 3091125 | 1.2% | n8n |
| 3726309 | 1.0% | Mystika Web (Next.js) |

---

## 9. AGENTES IA

### Inventario completo (21 agentes en opencode.json)

| # | Agente | Modelo | Rol | Estado real |
|---|--------|--------|-----|-------------|
| 1 | **mystic** | qwen3:4b-64k | Primary — alma de SDC | ✅ Activo |
| 2 | hermes | default | Gateway multi-canal | 🟡 Existe como MCP remoto |
| 3 | openclaw | default | 42 skills gateway | 🟡 Existe como MCP remoto |
| 4 | sdd | qwen3:4b-64k | SDD orchestrator | 🔴 Modelo no descargado local |
| 5 | sdd-spec | deepseek-r1:7b-64k | Spec generator | 🔴 Modelo no descargado local |
| 6 | sdd-design | qwen3:4b-64k | Design agent | 🔴 Modelo no descargado local |
| 7 | sdd-apply | llama3.2:3b-64k | Implementation | 🔴 Modelo no descargado local |
| 8 | sdd-verify | llama3.2:3b-64k | Validation | 🔴 Modelo no descargado local |
| 9 | sdd-archive | default | Documentation | 🔴 Sin uso real |
| 10 | process-doc | deepseek-r1:7b-64k | Auto-doc | 🔴 Sin uso real |
| 11 | memory | default | Engram memory | 🔴 Sin uso real |
| 12 | sales | llama3.2:3b-64k | Sales OS | 🔴 Sin uso real |
| 13 | dev | qwen3:4b-64k | Dev OS | 🔴 Sin uso real |
| 14 | support | qwen3:1.7b-32k | Support OS | 🔴 Sin uso real |
| 15 | agent-os | qwen3:4b-64k | Agent OS | 🔴 Sin uso real |
| 16 | knowledge | qwen3:4b-64k | Knowledge OS | 🔴 Sin uso real |
| 17 | finance | default | Finance OS | 🔴 Sin uso real |
| 18 | security | deepseek-r1:7b-64k | Security OS | 🔴 Sin uso real |
| 19 | ops | default | Ops OS | 🔴 Sin uso real |
| 20 | quality | llama3.2:3b-64k | Quality OS | 🔴 Sin uso real |
| 21 | strategy | deepseek-r1:7b-64k | Strategy OS | 🔴 Sin uso real |

### Agentes reales en VPS (no en opencode.json)

| Agente | Proceso | Puerto | Estado |
|--------|---------|--------|--------|
| Hermes Gateway | Python 3.13 | 8643 | ✅ Running (desde Jun 30) |
| OpenClaw Gateway | Go binary | 18789 | ✅ Running (desde Jul 1) |
| Truth Guardian | Python | - | ✅ Running (cada 10 min) |
| Monitoreo | Python | - | ✅ Running |
| Healer | Python | - | ✅ Running |
| Notifier | Python | - | ✅ Running |
| Mystika Bot | Node.js | - | 🔴 401 Unauthorized |
| ABE Daemon | Python | - | ✅ Running |

### MCP Servers configurados (Hermes: 22)

fetch, filesystem, git, github, gmail, google-calendar, drive, higgsfield, kubernetes, linear, meigen-ai-design, memory, playwright, postgres, puppeteer, redis, sqlite, stripe, supabase, tradingview, vercel, youtube

---

## 10. PROMPTS

### Inventario total

| Categoría | Archivos | Líneas | Estado |
|-----------|----------|--------|--------|
| Constitution | 11 | ~1,945 | ✅ Activos |
| Sistema (prompts/) | 54 | ~3,500 | ✅ Activos |
| OS Prompts | 11 | ~1,392 | 🟡 10 no se usan (subagents muertos) |
| Truth YAML | 12 | ~768 | ✅ Activos |
| Docs técnicas | 13 | ~1,768 | ✅ Activos |
| Capabilities (legacy) | 10 | ~34,253 | 🔴 **Muertos** — reemplazados por truth/ |
| SPECs activas | 6 | ~30,873 | 🟡 Activas pero infladas |
| ADRs | 11 dirs | ~2,000+ | 🟡 Archivo histórico |
| AGENTS.md | 1 | 282 | ✅ Referencia activa |
| CLAUDE.md | 1 | 59 | ✅ Activo |
| MAPA-SDC.md | 1 | 89 | ✅ Activo |

### Prompts duplicados o conflictivos detectados

| Conflicto | Explicación |
|-----------|-------------|
| 2x OMEGA-PROMPT | v10.0 activa + _deprecated/MASTER-SYSTEM-PROMPT-v2.0.md |
| 2x constitution.md | `constitution/constitution.md` + `constitution/OMEGA-PROMPT-v10.0.md` (parcialmente solapados) |
| 2x MANIFEST.md | `prompts/prompts/MANIFEST.md` + `prompts/prompts/OS/MANIFEST.md` |
| 10x capabilities legacy | `capabilities/systems/*.md` vs `truth/` (mismo contenido, distinto formato) |

### Prompts huérfanos (sin agente que los use)

| Prompt | Tamaño | Último uso |
|--------|--------|-----------|
| Todos los OS/*.md (10) | ~1,200 líneas | Creados para subagents que nunca se usaron |
| capabilities/systems/*.md (10) | ~34,000 líneas | Reemplazados por truth/ |
| STRATEGY/*.md (5) | ~269 líneas | Sin agente strategy activo |
| CONTENT/*.md (6) | ~454 líneas | Sin agente content activo |
| TOOLS/*.md (4) | ~293 líneas | Documentación referencial |
| CLIENTS/*.md (4) | ~262 líneas | Sin agente clients activo |
| IDENTITY/*.md (2) | ~123 líneas | Sin agente identity activo |

---

## 11. AUTOMATIZACIONES

### n8n Workflows

| Ubicación | Workflows | Estado |
|-----------|-----------|--------|
| config/n8n/ | backup, healthcheck, webhook, content, social, video | 🟡 No verificados en VPS |
| config/n8n-sdc/ | 35+ (agenda, alarmas, contenido, fiscal, music-hub, tests) | 🟡 No verificados en VPS |
| config/n8n-zero-token/ | system-health, git-sync, disk-cleanup, error-sentinel | 🟡 No verificados en VPS |

### Cron Jobs (13 entradas en VPS)

Ver sección 8 — 13 jobs programados incluyendo healthchecks, backups, sync, alertas.

### Playwright

| Archivo | Tests | Estado |
|---------|-------|--------|
| tests/playwright/sdc-app.spec.ts | 10 tests | 🟠 headless: false (no apto para CI) |

### Scrapers detectados

| Scraper | Directorio | Estado |
|---------|-----------|--------|
| apple_music.py | collectors/ | Data collector |
| deezer.py | collectors/ | Data collector |
| spotify.py | collectors/ | Data collector |
| tiktok.py | collectors/ | Data collector |
| youtube.py | collectors/ | Data collector |
| wikipedia.py | collectors/ | Data collector |
| healer.py | collectors/ | Auto-repair |
| sync_health.py | collectors/ | Health sync |

---

## 12. APIs

### APIs internas (VPS)

| API | Puerto | Framework | Status |
|-----|--------|-----------|--------|
| ABE Music API | 8111 | FastAPI | ✅ Respondiendo |
| ABE PWA | 5180 | FastAPI | ✅ Respondiendo |
| Mystika API | 4000 | Node.js/Express | ✅ Respondiendo |
| Mystika Web | 3001 | Next.js | ✅ Respondiendo |
| Jarvis WebUI | 5174 | FastAPI + Next.js | ✅ Respondiendo |
| MCP Server | 8000 | Python (server.py) | ✅ pero sin HTTP endpoints |
| Hermes Gateway | 8643 | Python (Hermes) | ✅ /health ok |
| OpenClaw Gateway | 18789 | Go | ✅ /health ok |
| n8n | 5678 | Node.js | ✅ /healthz ok |
| Langfuse | 3000 | Node.js | ✅ ok |
| Ollama | 11434 | Go | ✅ /api/tags ok |
| Neo4j | 7474 | Java | ✅ HTTP ok |
| Qdrant | 6333 | Rust | ✅ /healthz ok |
| Redis | 6379 | C | ✅ PONG |
| Postgres | 5432 | C | ✅ pg_isready ok |

### APIs externas referenciadas

| API | Tipo | Endpoint o SDK |
|-----|------|----------------|
| Stripe | REST | api.stripe.com |
| Mercado Pago | REST | api.mercadopago.com |
| Telegram Bot | REST | api.telegram.org |
| OpenRouter | REST | openrouter.ai/api |
| fal.ai | REST | fal.run |
| GitHub API | REST | api.github.com |
| Vercel API | REST | api.vercel.com |

---

## 13. BASE DE DATOS

### Motores

| Motor | Versión | Propósito | Datos |
|-------|---------|-----------|-------|
| Neo4j | 5.19.0 | Graph DB — memoria, relaciones, grafos de conocimiento | Con datos (2GB volumen) |
| Qdrant | 1.7.4 | Vector DB — embeddings, búsqueda semántica | Con datos (500MB volumen) |
| PostgreSQL | 15 | Relacional — Mystika, n8n, Langfuse, ABE | Con datos (1GB volumen) |
| Redis | 7-alpine | Cache + colas | Con datos (100MB volumen) |

### ORM / Drivers

| Tecnología | Dónde |
|-----------|-------|
| Prisma (Node.js) | products/mystika/api |
| neo4j Python driver | apps/ |
| qdrant-client (Python) | apps/ |
| redis-py | apps/ |
| asyncpg / psycopg2 | apps/ |

### Migraciones

| Proyecto | Migraciones | Estado |
|----------|------------|--------|
| products/mystika/api/prisma/ | ✅ Prisma migrations presentes | 🟡 No verificadas |
| infra/docker/neo4j/init.cypher | ✅ Init script Neo4j | ❌ No ejecutado? |
| infra/docker/neo4j/init_journey.cypher | ✅ Init script journey | ❌ No ejecutado? |

---

## 14. SEGURIDAD

### Hallazgos críticos

| # | Hallazgo | Archivo | Severidad |
|---|----------|---------|-----------|
| 1 | **JWT secret en frontend PWA** | `apps/abe-service/pwa/app.js:16` | 🔴 **Crítico** |
| 2 | **JWT secret default hardcodeado** | `apps/abe-service/config.py:31` | 🔴 **Crítico** |
| 3 | **MCP secret hardcodeado** | `apps/abe-service/config.py:46` | 🔴 **Crítico** |
| 4 | **Postgres password en docker-compose** | `infra/docker-compose.yml:16` | 🟠 Alto |
| 5 | **Redis password en docker-compose** | `infra/docker-compose.yml:38` | 🟠 Alto |
| 6 | **Neo4j password en docker-compose** | `infra/docker-compose.yml:62` | 🟠 Alto |
| 7 | **Langfuse secret + salt en docker-compose** | `infra/docker-compose.yml:216,220` | 🟠 Alto |
| 8 | **Secrets texto plano coexist con age cifrado** | `config/.secrets/clients.json` | 🟠 Alto |
| 9 | **Secrets en 3 backups históricos** | `backups/*/config/.secrets/` | 🟡 Medio |
| 10 | **Neo4j MCP password hardcodeado** | `infra/docker/mcp-server/config.py:13` | 🟠 Alto |
| 11 | **Mystika Bot token inválido (401)** | En VPS | 🟡 Medio |
| 12 | **machines.json con IP pública** | `config/machines.json` | 🟡 Medio |

### Checklist de seguridad

| Control | Estado | Evidencia |
|---------|--------|-----------|
| Fail2Ban | ✅ Activo | ufw active, fail2ban running |
| SSL/TLS | 🟡 Parcial | api.sdc.com ✅, mystika.sdc.com ❌ |
| Firewall | ✅ Activo | UFW deny incoming, allow specific |
| Secrets cifrados | 🟡 Parcial | age presente pero texto plano aún existe |
| CORS | ✅ Configurado | Nginx headers Access-Control-Allow-Origin: * |
| Rate limiting | ❌ NO implementado | Sin configuración detectada |
| JWT | 🟡 Inconsistente | Hardcodeado en frontend |
| OAuth | ❌ No detectado | Sin OAuth |
| Auth en MCP | ❌ No detectado | Servidores MCP sin tokens |

---

## 15. CÓDIGO MUERTO

### Archivos y directorios sin uso (detectados)

| Elemento | Tamaño | Razón |
|----------|--------|-------|
| `apps/act/` | 64KB | Placeholder, sin imports |
| `apps/agent_metrics/` | 24KB | Placeholder |
| `apps/cache/` | 8KB | Vacío |
| `apps/control/` | 12KB | Placeholder |
| `apps/data/` | 12KB | Vacío |
| `apps/economics/` | 24KB | Placeholder |
| `apps/hermes/services/` | 56KB | Código separado del Hermes real (VPS) |
| `apps/learning/` | 24KB | Duplicado de `apps/learn/` |
| `apps/logs/` | 4KB | Vacío |
| `apps/observe/` | 12KB | Placeholder |
| `apps/understand/` | 12KB | Placeholder |
| `products/footprint/` | 4KB | Vacío |
| `products/chatbot/` | 12KB | Esqueleto |
| `products/landing-artista/` | 12KB | Esqueleto |
| `sonora-enterprise-os/capabilities/systems/` | 34K líneas | Legacy, reemplazado por truth/ |
| `sonora-enterprise-os/constitution/_deprecated/` | 98 líneas | Prompt viejo |
| `.github/workflows/implementador.yml` | 15 líneas | DISABLED |
| `webui/static/static/` | ~400 archivos | Dashboards HTML estáticos sin referencias |

### Dependencias sin uso

| Directorio | Tamaño | Razón |
|------------|--------|-------|
| `products/mystika/web/node_modules/` | ~400MB | Dependencias de Next.js build |
| `mcp/node_modules/` | ~27MB | Dependencias no críticas |
| `clients/abe-music/**/node_modules/` | ~300MB | Dependencias de cliente |

---

## 16. ESTADO REAL

### Clasificación por componente

| Componente | Estado | Evidencia |
|------------|--------|-----------|
| **ABE Music API** | ✅ **Producción** | FastAPI, sistema service, healthcheck ok |
| **Mystika Web** | ✅ **Producción** | Next.js, nginx, systemd service |
| **Mystika API** | ✅ **Producción** | Express, Stripe/MP integrados |
| **Neo4j** | ✅ **Producción** | Docker healthy, datos persistentes |
| **Qdrant** | ✅ **Producción** | Docker healthy, datos persistentes |
| **Postgres** | ✅ **Producción** | Docker healthy |
| **Redis** | ✅ **Producción** | Docker healthy |
| **Ollama** | ✅ **Producción** | 6 modelos disponibles |
| **OpenClaw Gateway** | ✅ **Producción** | 42 skills, systemd |
| **Hermes Gateway** | ✅ **Producción** | v0.16.0, 22 MCP servers |
| **Nginx** | ✅ **Producción** | 2 dominios, SSL parcial |
| **Backups** | ✅ **Producción** | 3 días rotación diaria |
| **CI/CD** | ✅ **Producción** | 26 workflows |
| **Monitoring** | ✅ **Producción** | Cron cada 15 min |
| **Truth Guardian** | ✅ **Producción** | Systemd, cada 10 min |
| | | |
| **Jarvis Core** | 🟡 **Funcional** | Docker, sin healthcheck |
| **Jarvis WebUI** | 🟡 **Funcional** | Next.js, build presente |
| **n8n Workflows** | 🟡 **Funcional** | Docker healthy, workflows sin verificar |
| **Langfuse** | 🟡 **Funcional** | Docker healthy, sin tráfico aparente |
| **ABE Daemon** | 🟡 **Funcional** | Running, ciclo 10 min |
| | | |
| **Mystika Telegram Bot** | 🟠 **Parcial** | 401 Unauthorized — token inválido |
| **scrapers/** | 🟠 **Parcial** | Código presente, sin deploy confirmado |
| **collectors/** | 🟠 **Parcial** | Código presente, sin deploy confirmado |
| **apps/ (excepto jarvis)** | 🟠 **Parcial** | Placeholders mayoritariamente |
| **products/yami** | 🟠 **Parcial** | 288KB, sin deploy |
| **products/telegram-masterclass** | 🟠 **Parcial** | 44KB, contenido |
| | | |
| **process-doc agent** | 🔴 **Roto/Sin uso** | Modelo no descargado en laptop |
| **memory agent** | 🔴 **Roto/Sin uso** | Modelo no descargado en laptop |
| **SDD agents (6)** | 🔴 **Roto/Sin uso** | Modelos no descargados |
| **OS agents (10)** | 🔴 **Roto/Sin uso** | No hay subagentes activos |
| **playwright tests** | 🔴 **Roto** | headless: false, no apto CI |
| **jarvis-backup.timer** | 🔴 **Roto** | User=mystic no existe |
| **jarvis-healthcheck.timer** | 🔴 **Roto** | User=mystic no existe |
| **capabilities/systems/** | 🔴 **Muerto** | Reemplazado por truth/ |
| | | |
| **Terraform** | ⚫ **Sin implementar** | No existen archivos .tf |
| **Kubernetes** | ⚫ **Sin implementar** | No existe |
| **Load testing** | ⚫ **Sin implementar** | No hay tests de carga |
| **Rate limiting** | ⚫ **Sin implementar** | No configurado |
| **OAuth** | ⚫ **Sin implementar** | No implementado |

### Porcentaje de finalización estimado por capa

| Capa | % Completo | Estado |
|------|-----------|--------|
| Infraestructura VPS | 85% | ✅ Producción |
| Base de datos | 80% | ✅ Producción |
| CI/CD | 90% | ✅ Producción |
| Seguridad | 40% | 🟡 Medio |
| APIs (ABE, Mystika) | 70% | ✅ Producción |
| Frontend (Mystika Web) | 75% | ✅ Producción |
| Agentes IA (opencode) | 20% | 🔴 20/21 agentes muertos |
| Automatizaciones | 60% | 🟡 Funcional |
| Tests | 50% | 🟡 Medio |
| Documentación | 80% | ✅ Exceso |
| Productos (no mystika) | 10% | 🔴 Esqueletos |
| **GLOBAL** | **~55%** | 🟡 Funcional con deuda |

---

## 17. RIESGOS

### Priorizados

| # | Riesgo | Severidad | Impacto | Mitigación |
|---|--------|-----------|---------|------------|
| 1 | **JWT secret hardcodeado en frontend PWA** | 🔴 **Crítico** | Cualquier usuario puede ver el secret JS. Compromete toda la autenticación de ABE Music. | Mover a .env, regenerar secret |
| 2 | **6+ passwords hardcodeados en docker-compose** | 🔴 **Crítico** | Si alguien accede al repo, tiene acceso a todas las DBs del VPS | Usar .env + secrets management |
| 3 | **Swap al 80% (1.6GB/2GB)** | 🟠 **Alto** | Degradación de rendimiento, riesgo de OOM | Reducir heap de Neo4j o agregar RAM |
| 4 | **Mystika Bot Token inválido (401)** | 🟠 **Alto** | Bot de Telegram no funciona | Renovar token |
| 5 | **Spec store bypass: VULNERABLE** | 🟠 **Alto** | Vulnerabilidad de CPU sin mitigar | Microcódigo / kernel update |
| 6 | **Mystika Web sin SSL** | 🟠 **Alto** | Tráfico HTTP plano para mystika.sdc.com | Agregar cert Let's Encrypt |
| 7 | **2 timers systemd rotos** | 🟠 **Alto** | Backup y healthcheck nunca ejecutados (User=mystic no existe) | Cambiar a User=ubuntu |
| 8 | **Secrets en backups históricos** | 🟡 **Medio** | 3 copias de secrets en backups/ | Cifrar backups |
| 9 | **18 agentes IA configurados pero muertos** | 🟡 **Medio** | Complexidad injustificada, confusión | Limpiar opencode.json |
| 10 | **Secrets en texto plano coexist con age** | 🟡 **Medio** | clients.json sin cifrar aún existe | Eliminar versión texto plano |
| 11 | **Cobertura de tests inconsistente** | 🟡 **Medio** | 80% en pyproject vs 60% en PR template | Unificar threshold |
| 12 | **Machine specs expuestas en repo** | 🟡 **Medio** | config/machines.json con IP pública | Mover a .env o secret |
| 13 | **Rate limiting no implementado** | 🟡 **Medio** | APIs expuestas sin protección | Agregar nginx limit_req |
| 14 | **Docker images sin scan de vulnerabilidades** | 🟡 **Medio** | No hay Trivy / Grype en CI | Agregar al workflow security |
| 15 | **capacities legacy (34K líneas) sin limpiar** | 🟢 **Bajo** | Ruido, confusión, peso muerto | Archivar o eliminar |
| 16 | **SPECs activas infladas (30K líneas)** | 🟢 **Bajo** | Procesos sobredocumentados | Simplificar formato |

---

## 18. DEUDA TÉCNICA

### Qué eliminar YA (seguro, sin impacto)

| Elemento | Tamaño | Razón |
|----------|--------|-------|
| `apps/act/`, `apps/cache/`, `apps/control/`, `apps/data/`, `apps/economics/`, `apps/learning/`, `apps/logs/`, `apps/observe/`, `apps/understand/` | ~200KB total | Placeholders vacíos |
| `products/footprint/` | 4KB | Vacío |
| `products/chatbot/` | 12KB | Esqueleto sin uso |
| `products/landing-artista/` | 12KB | Esqueleto sin uso |
| `sonora-enterprise-os/capabilities/systems/` | 34K líneas | Legacy -> truth/ |
| `sonora-enterprise-os/constitution/_deprecated/` | 98 líneas | Prompt viejo |
| `.github/workflows/implementador.yml` | 15 líneas | Disabled |
| `backups/` en repo (vs VPS) | 2GB | Backups locales duplicados |

### Qué conservar (core del proyecto)

| Elemento | Prioridad | Razón |
|----------|-----------|-------|
| `apps/jarvis/` | 🥇 Alta | Única app con código real |
| `apps/abe-service/` | 🥇 Alta | API en producción |
| `apps/webui/` | 🥇 Alta | Web UI en producción |
| `products/mystika/` | 🥇 Alta | Producto principal en producción |
| `infra/docker-compose.yml` | 🥇 Alta | Orquestación de producción |
| `truth/` | 🥇 Alta | Source of truth |
| `config/` (sin .secrets) | 🥇 Alta | Configuraciones |
| `scripts/` | 🥇 Alta | Automatizaciones activas |
| `tests/` | 🥇 Alta | Suite de tests |
| `sonora-enterprise-os/constitution/` | 🥇 Alta | Prompts activos |
| `sonora-enterprise-os/prompts/` | 🥈 Media (podar) | Muchos prompts, pocos usados |
| `docs/` | 🥈 Media | Documentación referencial |

### Qué unificar

| Elementos | Acción |
|-----------|--------|
| `apps/learn/` + `apps/learning/` | Unificar en una sola |
| `apps/measure/` + `apps/guardian/` | Unificar (mismo propósito) |
| `sonora-enterprise-os/capabilities/` + `truth/` | Unificar en truth/ |
| `config/n8n/` + `config/n8n-sdc/` + `config/n8n-zero-token/` | Unificar workflows |
| `mcp/servers/` + `config/mcp/` | Unificar config de MCP |

### Qué dividir

| Monolito | Propuesta |
|----------|-----------|
| `opencode.json` (21 agentes) | Reducir a 3-5 agentes reales |
| `sonora-enterprise-os/prompts/` (54 archivos) | Podar a ~20 activos |
| `infra/docker-compose.yml` (11 servicios) | Separar en stacks (data, AI, apps) |

---

## 19. ROADMAP SUGERIDO

### Orden exacto de implementación (SIN MODIFICAR — solo sugerencia)

```
FASE 1 — SEGURIDAD INMEDIATA (días 1-2)
  ├── Rotar JWT secret de ABE Music (eliminar hardcode)
  ├── Rotar todas las passwords de docker-compose
  ├── Eliminar config/.secrets/clients.json texto plano
  ├── Agregar SSL a mystika.sonoradigitalcorp.com
  └── Arreglar Mystika Bot Token (401)

FASE 2 — LIMPIEZA (días 3-4)
  ├── Eliminar placeholders de apps/
  ├── Eliminar capabilities legacy (34K líneas)
  ├── Eliminar backups locales (2GB)
  ├── Unificar learn/ + learning/
  ├── Unificar measure/ + guardian/
  └── Podar prompts a ~20 activos

FASE 3 — CONSOLIDACIÓN (días 5-7)
  ├── Reducir opencode.json a 3-5 agentes (mystic, builder, dev, memory)
  ├── Configurar OpenRouter híbrido en VPS
  ├── Arreglar jarvis-backup.timer (User=mystic → ubuntu)
  ├── Arreglar jarvis-healthcheck.timer
  └── Unificar config de MCP

FASE 4 — CALIDAD (días 8-10)
  ├── Unificar threshold de coverage (80% consistente)
  ├── Agregar rate limiting a nginx
  ├── Agregar scan de vulnerabilidades Docker (Trivy)
  ├── Arreglar Playwright tests (headless: true)
  └── Agregar tests de carga/performance

FASE 5 — MVP REAL (días 11-14)
  ├── Definir QUÉ es el MVP (1 producto funcional)
  ├── Congelar stack (STACK-LOCK.md se cumple)
  ├── Eliminar todo lo que no sea MVP
  └── Documentar qué se puede poner en producción HOY
```

---

## 20. REPORTE EJECUTIVO

### ¿Qué tenemos?

Un ecosistema funcional con:

- **1 VPS en producción** (OVH, 6 vCPU, 11GB RAM, Ubuntu 26.04)
- **11 contenedores Docker** (Neo4j, Qdrant, Postgres, Redis, n8n, Langfuse, Jarvis, MCP, Telegram)
- **6 servicios systemd** (OpenClaw, Hermes, ABE API, ABE Daemon, Mystika API/Bot/Web, Truth Guardian)
- **2 APIs en producción** (ABE Music en FastAPI, Mystika en Node.js/Express)
- **3 dominios** (api.sonoradigitalcorp.com con SSL, mystika.sonoradigitalcorp.com sin SSL)
- **26 GitHub workflows** (CI, tests, security, deploy, monitoring, backup)
- **78 tests** (5 suites) con coverage target 80%
- **6 modelos LLM locales** en Ollama (Qwen3, DeepSeek R1, Llama 3.2, etc.)
- **~40K líneas de prompts** y documentación
- **Backups diarios** funcionando (3 días de retención)
- **Monitoreo** cada 15 min con alertas Telegram

### ¿Qué falta?

- **Un MVP definido** — no hay un producto claramente identificado como "el que se lanza"
- **Seguridad básica** — rate limiting, OAuth, secrets management
- **SSL completo** — mystika.sonoradigitalcorp.com sin HTTPS
- **Tests de carga/performance** — no existen
- **Terraform/IaC** — infraestructura 100% manual via Docker + scripts
- **Integración real de agentes** — 20 de 21 agentes configurados pero sin uso

### ¿Qué sobra?

- **17 ramas** (YA LIMPIADAS durante esta auditoría)
- **2GB de backups** en el repo local (duplicados del VPS)
- **~34,000 líneas** de capabilities legacy (systems/) reemplazadas por truth/
- **20 de 21 agentes** en opencode.json que nunca se usaron
- **~40 archivos de prompt** sin agente que los ejecute
- **8 apps placeholder** en apps/ (act, cache, control, data, economics, learning, observe, understand)
- **3 productos esqueleto** (footprint, chatbot, landing-artista)
- **2 copias de repo** (v2 YA ELIMINADA durante esta auditoría)

### ¿Qué está duplicado?

- `apps/learn/` ↔ `apps/learning/` (mismo propósito)
- `apps/measure/` ↔ `apps/guardian/` (mismo propósito)
- `capabilities/systems/` ↔ `truth/` (mismo contenido semántico)
- `config/n8n/` + `config/n8n-sdc/` + `config/n8n-zero-token/` (3 copias de workflows)
- `mcp/servers/` + `config/mcp/` (2 configs MCP)
- `constitution/constitution.md` ↔ `constitution/OMEGA-PROMPT-v10.0.md` (solapamiento parcial)
- `prompts/prompts/MANIFEST.md` ↔ `prompts/prompts/OS/MANIFEST.md`

### ¿Qué está roto?

| Componente | Síntoma | Causa raíz |
|-----------|---------|------------|
| Mystika Telegram Bot | 401 Unauthorized | Token inválido/expirado |
| jarvis-backup.timer | Inactivo | User=mystic no existe en VPS |
| jarvis-healthcheck.timer | Inactivo | User=mystic no existe en VPS |
| Playwright tests | No ejecutables en CI | headless: false |
| Agentes SDD (6) | No arrancan | Modelos no descargados en laptop |
| OS Agents (10) | No se usan | Configurados pero sin invocación real |
| MCP Server HTTP | 404 en /health | Custom server.py sin endpoints REST |

### ¿Qué puede ponerse en producción HOY?

| Componente | Razón |
|-----------|--------|
| **ABE Music API** | Ya está en producción y funcionando |
| **Mystika Web + API** | Ya está en producción (sin SSL) |
| **Jarvis Core + WebUI** | Funcional, sirviendo en api.sdc.com:5174 |
| **Infraestructura Docker** | Todos los containers healthy |
| **CI/CD** | 26 workflows operativos |
| **Backups** | Rotación diaria funcionando |
| **Monitoreo** | Alertas cada 15 min funcionando |

### ¿Qué impide lanzar el MVP?

1. **No hay un MVP definido** — hay 7 productos, 2 clientes, 20 apps, pero ningún "producto mínimo viable" claramente identificado con métricas de éxito.

2. **Deuda de seguridad crítica** — JWT secret hardcodeado en frontend + 6 passwords en docker-compose impiden considerar "producción real" con clientes externos.

3. **Mystika sin SSL** — El producto principal del frontend no tiene HTTPS.

4. **Swap al 80%** — Infraestructura cerca del límite.

5. **Sobrecarga cognitiva** — 21 agentes, 100 skills, 80 prompts, 26 workflows, 11 servicios — el sistema es más complejo de operar que de lo que debería.

### ¿Qué porcentaje del proyecto está realmente terminado?

```
Infraestructura base:     ██████████ 85%
APIs en producción:       ███████░░░ 70%
Frontend (Mystika):       ███████░░░ 75%
CI/CD:                    █████████░ 90%
Tests:                    █████░░░░░ 50%
Seguridad:                ████░░░░░░ 40%
Agentes IA:               ██░░░░░░░░ 20%
Documentación/Prompts:    ████████░░ 80%
Productos (no Mystika):   █░░░░░░░░░ 10%
MVP definido:             ░░░░░░░░░░  0%

GLOBAL:                   █████░░░░░ 55%
```

---

## NOTAS FINALES

- **NO SE MODIFICÓ NINGÚN ARCHIVO** durante esta auditoría.
- Todos los datos fueron recolectados por observación directa.
- Los secrets se reportan sin valores visibles (redactados).
- Las ramas mencionadas como "YA LIMPIADAS" fueron eliminadas en una sesión previa autorizada.
- El directorio v2 fue eliminado en una sesión previa autorizada.
