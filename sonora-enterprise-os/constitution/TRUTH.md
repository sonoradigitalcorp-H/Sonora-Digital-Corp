# THE TRUTH — Single Source of Truth for All Agents

All agents (OpenClaw, Hermes, Mystic, JARVIS, ABE) MUST follow these rules.

## Paths (NO EXCEPTIONS)

| Old Path | New Path |
|----------|----------|
| `/home/mystic/jarvis/` | `/home/mystic/sonora-digital-corp/` |
| `/home/mystic/sdcorp/` | `/home/mystic/sonora-digital-corp/` |
| `~/jarvis/` | `/home/mystic/sonora-digital-corp/` |
| `~/sdcorp/` | `/home/mystic/sonora-digital-corp/` |
| `$JARVIS_HOME` | `/home/mystic/sonora-digital-corp/` |
| `~/SonoraDigitalCorp-Yami/` | `🚫 OBSOLETO — movido a sonora-enterprise-os/` |
| `$YAMI_HOME` | `🚫 OBSOLETO — movido a sonora-enterprise-os/` |
| `archive-sonora-digital-corp-git/` | `🚫 OBSOLETO — movido a backups/repos/` |
| `/home/ubuntu/sdc/` | `🚫 OBSOLETO — usar ~/sdc (symlink unificado)` |

## Latest Commit

`a7d9ee9` — feat: Ollama local models — provider config + 5 models with extended context (64k/32k)

## Key Locations

**UNIFIED PATH: `~/sdc`** — funciona en local y VPS (symlink → real path).

| What | Where |
|------|-------|
| Monorepo root (any machine) | `~/sdc` |
| Monorepo root (local real) | `/home/mystic/sonora-digital-corp/` |
| Monorepo root (VPS real) | `/home/ubuntu/sonora-digital-corp/` (via symlink `~/sdc`) |
| Abrir terminal | `sdc` (alias: `cd ~/sdc && opencode`) |
| Enterprise OS | `sonora-enterprise-os/` |
| Constitution | `sonora-enterprise-os/constitution/OMEGA-PROMPT-v10.0.md` |
| RULES | `sonora-enterprise-os/constitution/10-RULES.md` |
| Soul | `sonora-enterprise-os/constitution/SOUL.md` |
| Truth | `sonora-enterprise-os/constitution/TRUTH.md` |
| CONTRATO | `sonora-enterprise-os/constitution/CONTRATO.md` |
| Checksums | `sonora-enterprise-os/constitution/CHECKSUMS.sha256` |
| State (logs, engram, events, quality) | `state/` |
| JARVIS core engine | `apps/jarvis/src/core/` |
| Web UI | `apps/webui/` (FastAPI, port 5174) |
| Harnesses (10 OS) | `harnesses/` (symlink → `sonora-enterprise-os/harnesses/`) |
| Skills (10 canonical) | `skills/` (symlink → `sonora-enterprise-os/skills/`) |
| Initiatives (3 active) | `initiatives/` (symlink → `sonora-enterprise-os/initiatives/`) |
| Metrics | `metrics/` (symlink → `sonora-enterprise-os/metrics/`) |
| Specs (active) | `specs/` + `process/active/` |
| Quality violations | `state/quality/violations.jsonl` |
| Hermes bridge | `apps/hermes/hermes_bridge.py` |
| Docker compose | `infra/docker-compose.yml` |
| Tests | `tests/` |
| Scripts | `scripts/` |
| Decrypt env script | `scripts/decrypt-env.sh` |
| Fleet config (SSOT) | `fleet.yml` |
| Telegram bot | `platforms/telegram/server.js` (Node.js, Telegraf) |

## Git Hooks

| Hook | Location | What it does |
|------|----------|-------------|
| pre-commit | `.git/hooks/pre-commit` | Blocks commit if code changes exist without active SPEC in `process/active/` |
| post-commit | `.git/hooks/post-commit` | Updates CATALOG.md and emits commit event to events.jsonl |

Install with: `bash scripts/install-hooks.sh`

## CI / GitHub Actions

| Workflow | File | What it does |
|----------|------|-------------|
| Process Gate | `.github/workflows/process-gate.yml` | Enforces: active SPEC exists, JR-Lite 15-point compliance, Score ≥60, events logged |
| Tests | `.github/workflows/tests.yml` | Runs pytest and ruff lint on every PR |

## Pipeline System (`process/`)

Lifecycle:
```
Tier 1: Execute → Lección
Tier 2: Spec → Score → Gherkin → Tests → Code → Events → ADR → Lección
Tier 3: VDD → EDD → PDD → ODD → SDD → BDD → TDD → ADR → Events → Lección
```

| Artifact | Template | Location |
|----------|----------|----------|
| Spec | `process/templates/SPEC.md` | `process/active/SPEC-{ID}.md` |
| Score | `process/templates/SCORE.md` | `process/active/SCORE-{ID}.md` |
| Gherkin | `process/templates/GHERKIN.md` | `process/active/gherkin/{ID}.feature` |
| ADR | `process/templates/ADR.md` | `process/active/ADR-{ID}.md` |
| Lección | `process/templates/LECCION.md` | `process/active/LECCION-{ID}.md` |
| Event | `process/templates/EVENT.md` | (inline in events.jsonl) |

CLI: `bash scripts/process-pipeline.sh <command>`
Commands: spec-new, score, complete, event, adr-new, leccion-new, gherkin-new, status

### Completed Specs

| Fecha | ID | Título | Score | Lección |
|-------|-----|--------|-------|---------|
| 2026-06-30 | SPEC-20260630-001 | Pipeline System Initial Setup | — | `process/completed/20260630-pipeline-setup/` |
| 2026-06-30 | SPEC-20260630-002 | Revenue Pipeline: Sales Agent Automation | 84/100 | `process/completed/20260630-revenue-pipeline/` |

### JR-Lite 15-Point Compliance

Every tier 2+ spec must pass:
1. Objetivo claro en 1 línea
2. Value Driver identificado
3. FR numerados (≥1)
4. Success criteria verificables
5. Gherkin scenarios (≥2: happy path + edge)
6. Edge cases documentados
7. Enums tipados (si aplica)
8. Data classes frozen (si aplica)
9. Módulos < 200 líneas
10. Dependencias explícitas
11. Eventos definidos
12. Kill criteria
13. Scale criteria
14. Docstrings con FR reference
15. Score calculado

## Engram (Memory System)

| Feature | Status | Details |
|---------|--------|---------|
| Location | `apps/jarvis/src/core/engram.py` | SQLite + FTS5 |
| DB file | `~/.engram/engram.db` or `state/engram.db` | Auto-detected |
| Importance levels | 4 | critical(3), high(2), medium(1), low(0) |
| Memory layers | **7** | working(0), task(1), project(2), customer(3), business(4), historical(5), strategic(6) |
| Max promotion | 3 | Engram.promote(memory_id) |
| Decay | 30 days | Engram.apply_decay() |
| Write lock | 5s timeout | concurrent write protection |
| Schema migration | Auto | _migrate_schema() adds columns if missing |

### Pipeline Bridge (`apps/jarvis/src/core/pipeline_bridge.py`)

| Function | What |
|----------|------|
| `store_spec_completion(spec_id, summary, tags)` | Auto-store learning on spec completion |
| `query_engram_context(task, limit)` | Auto-query before task execution |
| `format_engram_context(results)` | Format results as context string |
| `scan_and_store_pipeline()` | Backfill unregistered completions |

## Sales Pipeline (`apps/jarvis/src/core/sales_pipeline.py`)

| Component | What |
|-----------|------|
| SalesPipeline | Neo4j-backed pipeline: lead → qualified → proposal → negotiation → won/lost |
| LeadScorer | Scores by plan_interest, source, niche (threshold: 10) |
| ProposalGenerator | Generates markdown proposals from product catalog |
| Sales Agent | `apps/jarvis/src/core/agents/sales.py` — registered in orchestrator |
| WebUI Routes | `apps/webui/routes/sales_router.py` — 8 endpoints |
| Telegram Skill | `platforms/telegram/skills/sales-pipeline.json` — triggers: /cotizar, planes, etc. |
| Gamification | Awards XP (100) + badge "primera_venta" on deal won |

### API Endpoints

| Method | Path | What |
|--------|------|------|
| POST | `/api/sales/leads` | Capture lead |
| GET | `/api/sales/leads` | List leads (filter by stage) |
| GET | `/api/sales/leads/{id}` | Get lead |
| POST | `/api/sales/leads/{id}/qualify` | Qualify lead |
| GET | `/api/sales/leads/{id}/proposal` | Generate proposal |
| POST | `/api/sales/leads/{id}/accept` | Accept proposal |
| POST | `/api/sales/leads/{id}/won` | Close won |
| POST | `/api/sales/leads/{id}/lost` | Close lost |
| GET | `/api/sales/dashboard` | Pipeline dashboard |

### Events Emitted

| Event | When |
|-------|------|
| `lead_received` | New lead captured |
| `lead_qualified` | Lead scored ≥ threshold |
| `proposal_generated` | Proposal sent |
| `proposal_accepted` | Lead accepted |
| `deal_created` | Deal created |
| `deal_won` | Sale closed + customer onboarded |
| `deal_lost` | Sale lost |
| `customer_onboarded` | Customer created in Neo4j |

### Pipeline Stages

`lead` → `qualified` → `proposal` → `negotiation` → `won` | `lost`

## Enterprise Score Dashboard

| Endpoint | What |
|----------|------|
| `GET /api/enterprise-score` | Live score + all 10 metrics |
| `GET /api/enterprise-score/history` | Last 100 score entries |

Current score: **23/100** (VPS — limpio, sin eventos históricos)
Metrics (10): Revenue Impact, Scalability, Reusability, Automation Impact, Knowledge Impact, Reliability, Founder Independence, Operational Simplicity, Customer Value, FinOps Efficiency
Threshold: ≥60 to approve

## Agent Registry (`agents/MANIFEST.md`)

| Agent | Role | Level | Status |
|-------|------|-------|--------|
| OpenClaw | Primary Operator | L1 | Active |
| JARVIS Core | System Orchestrator | L1 | Active |
| ABE | Music Production | L1 | Active |
| Engram | Memory System | L2 | Active |
| Enterprise Score | Metrics & Governance | L1 | Active |
| Sales Agent | Pipeline de ventas | L1 | Active |

Autonomy levels: L0(Manual) → L1(Assisted) → L2(Supervised) → L3(Delegated) → L4(Autonomous)

## VPS Info

| What | Value |
|------|-------|
| IP | 149.56.46.173 |
| OS | Ubuntu 26.04 |
| User | ubuntu |
| SSH key | `~/.ssh/id_ed25519_sdc` |
| SSH host | 149.56.46.173 |
| Monorepo path | `/home/ubuntu/sonora-digital-corp/` (physical) |
| Symlink | `~/sdc → /home/ubuntu/sonora-digital-corp/` |
| Latest commit | `a7d9ee9` |
| n8n | Docker, port 5678 |
| Neo4j | Docker, port 7687 |
| Qdrant | Docker, port 6333 |
| LangFuse | Docker, port 3000 (unhealthy) |
| Playwright MCP | Docker, port 8931 (unhealthy) |
| Web UI | Docker, port 5174 |

## Docker Management

```bash
cd ~/sdc && docker compose -f infra/docker-compose.yml ps
cd ~/sdc && docker compose -f infra/docker-compose.yml logs <container>
cd ~/sdc && docker compose -f infra/docker-compose.yml restart <container>
```

Docker compose file: `infra/docker-compose.yml` (also `infra/docker-compose.vps.yml`)

## Systemd Services (Split-brain — Pending Resolution)

| Service | Port | Type | Status | Action Needed |
|---------|------|------|--------|---------------|
| `jarvis-core.service` | — | systemd | active | ⚠️ Duplicates Docker `sdc-jarvis-core` — stop + disable |
| `abe-telegram-bot.service` | — | systemd | active | ⚠️ Duplicates Docker `sdc-telegram-bot` — stop + disable |
| `sonora-mcp-gateway.service` | — | systemd | active | ⚠️ Duplicates Docker `sdc-mcp-server` — stop + disable |
| `abe-daemon.service` | — | systemd | active | ✅ No Docker equivalent — keep |
| Docker (12 containers) | various | docker compose | 10 healthy, 2 unhealthy | Fix langfuse + playwright-mcp |

Docker services:
```bash
sudo systemctl stop jarvis-core.service abe-telegram-bot.service sonora-mcp-gateway.service
sudo systemctl disable jarvis-core.service abe-telegram-bot.service sonora-mcp-gateway.service
```

## Docker Containers

| Container | Image | Status | Mem Limit | Port |
|-----------|-------|--------|-----------|------|
| sdc-postgres | postgres:15 | healthy | 512MB | 127.0.0.1:5432 |
| sdc-redis | redis:7-alpine | healthy | 256MB | 127.0.0.1:6379 |
| sdc-neo4j | neo4j:5.19-community | healthy | 3GB | 127.0.0.1:7687 |
| sdc-qdrant | qdrant/qdrant | healthy | 256MB | 127.0.0.1:6333 |
| sdc-mcp-server | custom | healthy | — | 127.0.0.1:8000 |
| sdc-n8n | n8nio/n8n | healthy | 512MB | 127.0.0.1:5678 |
| sdc-jarvis-webui | custom | healthy | — | 127.0.0.1:5174 |
| sdc-jarvis-core | custom | Up 20h | — | — |
| sdc-telegram-bot | custom | Up 25h | 128MB | 127.0.0.1:3003 |
| sdc-langfuse | langfuse/langfuse | **unhealthy** | 256MB | 127.0.0.1:3000 |
| sdc-langfuse-db | postgres:15 | healthy | 256MB | — |
| sdc-playwright-mcp | custom | **unhealthy** | — | 0.0.0.0:8931 |

Total: 12 containers (2 unhealthy: langfuse, playwright-mcp)

## Systemd Services (VPS — Split-brain)

| Service | Status | Port | Conflict |
|---------|--------|------|----------|
| `jarvis-core.service` | active | — | ⚠️ Duplicates Docker `sdc-jarvis-core` |
| `abe-telegram-bot.service` | active | — | ⚠️ Duplicates Docker `sdc-telegram-bot` (causes 409 Conflict) |
| `sonora-mcp-gateway.service` | active | — | ⚠️ Duplicates Docker `sdc-mcp-server` |
| `abe-daemon.service` | active | — | ✅ Systemd only, no Docker equivalent |

**Resolution needed**: Stop + disable systemd duplicates, keep only Docker.

## Test Results
- `pytest tests/unit/ -q` → **24 pass, 0 fail** (live-data-pipeline tests)
- Coverage threshold: `fail_under = 80` (constitution requirement)
- CI enforces: TDD check + pytest-cov --cov-fail-under=80

## Networking (Policy P3)
- **Policy P3**: No service binds 0.0.0.0 without nginx proxy
- **Fixed 2026-07-03**: All 22 internal services now bind to 127.0.0.1
- **Public only**: ssh:22, nginx:80, nginx:443
- **SSL certs**: `/etc/letsencrypt/live/` permissions fixed to 755
- **Services fixed**:
  - `:5180` ABE Service: `--host 0.0.0.0` → `127.0.0.1`
  - `:8111` ABE API: `abe-api.service` bind to 127.0.0.1
  - `:8080` Evolucion Dashboard: `--bind 127.0.0.1`
  - `:8931` Playwright MCP: container removed (not in compose)
  - `:3001` Mystika Web: `next start -H 127.0.0.1`
  - `:4000` Mystika API: `app.listen(PORT, '127.0.0.1')`
- **Nginx**: SSL verified, `nginx -t` OK, reloaded

## Secrets Management
- **Method**: `age` v1.2.1 (age-encryption.org)
- **SSOT**: `fleet.yml` (Policy P2) — all configs auto-generated from it
- **Keys**: `~/.age/key.txt` per machine (never committed)
- **Encrypted files**:
  | File | Machine | Contents |
  |------|---------|----------|
  | `.env.age` | laptop | Telegram tokens, Redis password |
  | `config/.secrets/clients.json.age` | laptop | Client secrets |
  | `/home/ubuntu/.hermes/auth.json.age` | VPS | Hermes API keys (opencode-go + OpenRouter) |
  | `/home/ubuntu/.local/share/opencode/auth.json.age` | VPS | OpenClaw auth |
- **Decryption**: `age -d -i ~/.age/key.txt -o <output> <file>.age`
- **Script**: `scripts/decrypt-env.sh` — decrypts and sources `.env.age` + `clients.json.age`
- **Policy P1**: TRUTH.md is AUTOGENERATED — nobody edits by hand
- **Policy P2**: fleet.yml is SINGLE SOURCE OF TRUTH — all configs derived
- **Policy P3**: No service binds 0.0.0.0 without nginx proxy
- **Policy P6**: Silence = health (no daily "all OK" reports)
- **Policy P8**: AI queries live `/api/v1/status`, not static TRUTH.md

## Governance
- **Decision hierarchy**: VDD → EDD → PDD → ODD → SDD → BDD → TDD
- **Score gate**: ≥60 to approve | JR-Lite 15-point checklist enforced
- **10 Sub-OS**: Sales, Dev, Support, Agent, Knowledge, Finance, Security, Ops, Quality, Strategy
- **10 Agent Harnesses**: all defined in `harnesses/` (via symlink → `sonora-enterprise-os/harnesses/`)
- **10 Canonical Skills**: all defined in `skills/` (via symlink → `sonora-enterprise-os/skills/`)
- **3 Initiatives**: automation-coverage (64/100), finops-baseline (67/100), knowledge-immortality (71/100)
- **Observability**: LangFuse (traces, cost tracking — currently unhealthy)
- **Enterprise Score**: Calculated from events.jsonl, live at /api/enterprise-score. Currently 23/100. 10 metrics × 10 points, threshold ≥60.
