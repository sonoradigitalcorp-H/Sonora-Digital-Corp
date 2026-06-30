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
| `/home/ubuntu/sdc/` | `🚫 OBSOLETO — systemd usa /home/ubuntu/sonora-digital-corp/` |

## Latest Commit

`9420abc` — feat: revenue pipeline — sales agent automation, Engram bridge, score dashboard
(`87c4077` — feat: pipeline system)

## Key Locations

| What | Where |
|------|-------|
| Monorepo root (local) | `/home/mystic/sonora-digital-corp/` |
| Monorepo root (VPS) | `/home/ubuntu/sonora-digital-corp/` |
| Enterprise OS | `sonora-enterprise-os/` |
| Constitution | `sonora-enterprise-os/constitution/OMEGA-PROMPT-v10.0.md` |
| RULES | `sonora-enterprise-os/constitution/10-RULES.md` |
| Soul | `sonora-enterprise-os/constitution/SOUL.md` |
| Truth | `sonora-enterprise-os/constitution/TRUTH.md` |
| CONTRATO | `sonora-enterprise-os/constitution/CONTRATO.md` |
| Checksums | `sonora-enterprise-os/constitution/CHECKSUMS.sha256` |
| State (logs, engram, events) | `state/` |
| JARVIS core engine | `apps/jarvis/src/core/` |
| Web UI | `apps/webui/` (FastAPI, port 5174) |
| Hermes bridge | `apps/hermes/hermes_bridge.py` |
| Docker compose | `infra/docker-compose.yml` |
| Tests | `tests/` |
| Scripts | `scripts/` |
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
| Memories stored | 48 | 45 level 1, 3 level 2 |
| Importance levels | 4 | critical(3), high(2), medium(1), low(0) |
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
| Monorepo path | `/home/ubuntu/sonora-digital-corp/` (systemd) |
| Old repo | `/home/ubuntu/sdc/` (deprecated) |
| Latest commit | `9420abc` |
| n8n | Docker, port 5678 |
| Neo4j | Docker, port 7687 |
| Qdrant | Docker, port 6333 |
| LangFuse | Docker, port 3000 |

## Services (VPS)

| Service | Port | Type | How to restart |
|---------|------|------|---------------|
| JARVIS Web UI | 5174 | systemd | `sudo systemctl restart jarvis-webui.service` |
| JARVIS Core | — | systemd | `sudo systemctl restart jarvis-core.service` |
| JARVIS Error Correction | — | systemd timer | `sudo systemctl restart jarvis-error-correction.timer` |
| Docker containers (9) | various | docker compose | `cd /home/ubuntu/sonora-digital-corp && docker compose -f infra/docker-compose.yml restart` |

## Docker Containers

| Container | Image | Mem Limit | Port |
|-----------|-------|-----------|------|
| postgres | postgres:15 | 512MB | 127.0.0.1:5432 |
| redis | redis:7-alpine | 256MB | 127.0.0.1:6379 |
| neo4j | neo4j:5.19-community | 3GB | 127.0.0.1:7687 |
| qdrant | qdrant/qdrant | 256MB | 127.0.0.1:6333 |
| mcp-server | custom | — | 127.0.0.1:8000 |
| n8n | n8nio/n8n | 512MB | 127.0.0.1:5678 |
| telegram-bot | custom | 128MB | — |
| langfuse | langfuse/langfuse | 256MB | 127.0.0.1:3000 |
| langfuse-db | postgres:15 | 256MB | — |

## Test Results
- `pytest tests/unit/ -q` → **417 pass, 1 skip, 0 fail** 🟢
- Coverage: new modules have ≥70% (sales_pipeline.py, engram.py extended, pipeline_bridge.py, score calculation)
- CI enforces: TDD check (new modules need test files) + pytest-cov --cov-fail-under=60
- Integration: 372 pass, 4 fail (need API key), same as before

## Governance
- **Decision hierarchy**: VDD → EDD → PDD → ODD → SDD → BDD → TDD → Implementation
- **Score gate**: ≥60 to approve | JR-Lite 15-point checklist enforced
- **10 Sub-OS**: Sales, Dev, Support, Agent, Knowledge, Finance, Security, Ops, Quality, Strategy
- **Observability**: LangFuse (traces, cost tracking)
- **Enterprise Score**: Calculated from events.jsonl, live at /api/enterprise-score
