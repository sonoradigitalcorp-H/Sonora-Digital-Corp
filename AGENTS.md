# Sonora Digital Corp — Quick Reference

**One truth**: `sonora-enterprise-os/constitution/OMEGA-PROMPT-v10.0.md`
**Soul**: `sonora-enterprise-os/constitution/SOUL.md`
**Governance**: VDD → EDD → PDD → ODD → SDD → BDD → TDD

---

## Structure

| Ruta | Qué es |
|------|--------|
| `apps/jarvis/` | 18 agentes, RAG, Neo4j, Qdrant |
| `apps/webui/` | FastAPI frontend + WebSocket |
| `apps/voice/` | Whisper + TTS |
| `apps/hermes/` | MCP bridge + servicios |
| `platforms/telegram/` | Bot + 97 skills |
| `platforms/whatsapp/` | Bridge |
| `infra/` | Docker, compose, monitoreo, n8n |
| `products/` | ABE Music, AZREC, Masterclass |
| `tests/` | 26 tests |
| `scripts/` | 50+ DevOps |
| `sonora-enterprise-os/` | Enterprise OS completo |

## Comandos

```bash
pytest tests/unit/              # unit tests
pytest tests/integration/       # integration
npx playwright test             # E2E
ruff check apps/                # lint
flake8 apps/                    # flake8
docker compose -f infra/docker-compose.yml up -d
python apps/jarvis/main.py      # JARVIS core
```

## Servicios

| Puerto | Servicio | Systemd |
|--------|----------|---------|
| 5174 | Web UI | `jarvis-webui.service` --user |
| 8000 | Hermes MCP | `hermes-gateway.service` --user |
| 18789 | OpenClaw Gateway | `openclaw-gateway.service` |
| 6333 | Qdrant | Docker |
| 7687 | Neo4j | Docker |
| 5678 | n8n | Docker (33 workflows) |

## Sub-OS Architecture

| OS | Domain | Prompt |
|----|--------|--------|
| Sales | Go-to-market | `prompts/prompts/OS/Sales-OS.md` |
| Dev | Software delivery | `prompts/prompts/OS/Dev-OS.md` |
| Support | Client care | `prompts/prompts/OS/Support-OS.md` |
| Agent | Agent lifecycle | `prompts/prompts/OS/Agent-OS.md` |
| Knowledge | Memory & docs | `prompts/prompts/OS/Knowledge-OS.md` |
| Finance | FinOps & revenue | `prompts/prompts/OS/Finance-OS.md` |
| Security | Trust & compliance | `prompts/prompts/OS/Security-OS.md` |
| Ops | Infrastructure | `prompts/prompts/OS/Ops-OS.md` |
| Quality | Testing & evaluation | `prompts/prompts/OS/Quality-OS.md` |
| Strategy | Direction & growth | `prompts/prompts/OS/Strategy-OS.md` |

## Agentes opencode

`mystic` (primary) + explore, builder, reviewer, hermes, openclaw, sdd/*, memory, research, code, sales, dev, support, agent, knowledge, finance, security, ops, quality, strategy.

## Comandos rápidos

- `/status` — healthcheck
- `/backup` — backup
- `/brain` — brain graph
- `/gsd` — Get Shit Done
- `/sdd-new` — nueva spec
- `/build` — construir feature
- `/sales` — Sales OS
- `/dev` — Dev OS
- `/support` — Support OS
- `/agent` — Agent OS
- `/knowledge` — Knowledge OS
- `/finance` — Finance OS
- `/security` — Security OS
- `/ops` — Ops OS
- `/quality` — Quality OS
- `/strategy` — Strategy OS

## Templates

| Template | Location |
|----------|----------|
| Agent Harness | `harnesses/AGENT-HARNESS-TEMPLATE.md` |
| Skill | `skills/SKILL-TEMPLATE.md` |
| Initiative | `initiatives/initiative-TEMPLATE.md` |
| Event Catalog | `events/CATALOG.md` |
| Enterprise Score | `metrics/enterprise-score.md` |

Enterprise Score: ≥60 para aprobar (10 metrics × 10, max 100).
