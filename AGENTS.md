# Sonora Digital Corp — Enterprise OS

**Supreme governing document**: `sonora-enterprise-os/constitution/MASTER-SYSTEM-PROMPT.md`

Every action follows: **VDD → EDD → PDD → SDD → BDD → TDD → Implementation**

Value leads. Technology follows.

---

## Enterprise OS Structure

`sonora-enterprise-os/` contains the full operating system:

| Directory | Purpose |
|-----------|---------|
| `constitution/` | Supreme governance: master prompt, constitution |
| `adr/` | Architectural Decision Records |
| `capabilities/` | Business capability registry & maturity model |
| `policies/` | Policy engine rules (event→action) |
| `events/` | Standard event catalog (all ops start here) |
| `skills/` | Skill registry with inputs/outputs/metrics |
| `harnesses/` | Agent harness registry per domain |
| `digital_twins/` | Customer & corporate digital twins |
| `initiatives/` | Initiative registry with kill criteria |
| `metrics/` | Score systems, KPIs, FinOps |
| `observability/` | Monitoring, BI, executive reports |
| `prompts/` | Prompt evolution engine (evidence-based) |
| `playbooks/` | Reusable playbooks |
| `roadmap/` | Autonomous roadmap output |

---

## Repo Structure

| Ruta | Qué es |
|------|--------|
| `apps/jarvis/` | Orquestador central: 18 agentes, RAG, Neo4j, Qdrant |
| `apps/webui/` | FastAPI frontend: 20 routers + HTML + WebSocket |
| `apps/voice/` | Whisper STT + TTS engine |
| `apps/hermes/` | MCP bridge + servicios |
| `platforms/telegram/` | Bot runtime + 97 skills JSON |
| `platforms/whatsapp/` | Bridge |
| `packages/` | agent-runtime, sdd-harness, memory |
| `infra/` | Docker, compose, monitoreo, nginx, n8n |
| `specs/` | SDD specs activos (000-010) + 23 archive |
| `config/` | Prompts, knowledge, MCP, n8n, design tokens |
| `skills/` | 5 skills verticales |
| `products/` | Clientes: ABE Music, AZREC, Masterclass |
| `tests/` | 22 unit + 3 integration + 1 Playwright |
| `scripts/` | 50+ DevOps |
| `docs/` | ARQUITECTURA-MENTAL, systems OS |

---

## Comandos

```bash
pytest tests/unit/                           # unit tests
pytest tests/integration/                    # integration tests
npx playwright test                          # E2E
ruff check apps/                             # lint
flake8 apps/                                 # flake8
docker compose -f infra/docker-compose.yml up -d
python apps/jarvis/main.py                   # JARVIS core
```

## Servicios locales

| Puerto | Servicio |
|--------|----------|
| 5174 | Web UI |
| 8000 | Hermes MCP |
| 18789 | OpenClaw Gateway |
| 6333 | Qdrant |
| 7687 | Neo4j Bolt |
| 5678 | n8n |

---

## Agentes

Primary: **mystic**. Sub-agents: explore, builder, reviewer, hermes, openclaw, sdd (+spec/design/apply/verify/archive), memory, research, code.

## Custom commands

- `/status` — healthcheck completo
- `/backup` — backup a /home/mystic/backups/sdc/
- `/brain` — brain graph dashboard
- `/gsd` — Get Shit Done
- `/sdd-new` — nueva spec SDD
- `/build` — construir feature

---

## Enterprise Score

Every proposal must score ≥60 total across: Revenue, Automation, Scalability, Reusability, Maintainability, Founder Independence, Customer Value, Operational Simplicity (0-10 each).

## SDD Workflow

Revenue Gate → Discovery → Spec → BDD/ATDD → ADR → Plan → Tasks → Code → Verify → Delivery Gate → Archive

Read: `specs/000-constitucion/constitution.md`

---

## Origen

Consolidado en `github.com/sonoradigitalcorp-H/Sonora-Digital-Corp`.
