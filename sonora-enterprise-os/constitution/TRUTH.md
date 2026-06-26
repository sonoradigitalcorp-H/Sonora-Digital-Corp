# THE TRUTH — Single Source of Truth for All Agents

All agents (OpenClaw, Hermes, Mystic, JARVIS) MUST follow these rules.

## Paths (NO EXCEPTIONS)

| Old Path | New Path |
|----------|----------|
| `/home/mystic/jarvis/` | `/home/mystic/sonora-digital-corp/` |
| `/home/mystic/sdcorp/` | `/home/mystic/sonora-digital-corp/` |
| `~/jarvis/` | `/home/mystic/sonora-digital-corp/` |
| `~/sdcorp/` | `/home/mystic/sonora-digital-corp/` |
| `$JARVIS_HOME` | `/home/mystic/sonora-digital-corp/` |
| `~/SonoraDigitalCorp-Yami/` | `/home/mystic/sonora-digital-corp/products/yami/` |
| `$YAMI_HOME` | `/home/mystic/sonora-digital-corp/products/yami/` |
| Yami repo (Mystic+Noel) | `/home/mystic/sonora-digital-corp/products/yami/` |

## Key Locations

| What | Where |
|------|-------|
| Monorepo root | `/home/mystic/sonora-digital-corp/` |
| Enterprise OS | `/home/mystic/sonora-digital-corp/sonora-enterprise-os/` |
| Constitution | `sonora-enterprise-os/constitution/OMEGA-PROMPT-v10.0.md` |
| State (logs, engram, backups) | `state/` |
| JARVIS core engine | `apps/jarvis/` |
| Hermes bridge | `apps/hermes/hermes_bridge.py` |
| Docker compose | `infra/docker-compose.yml` |
| Tests | `tests/` |
| Scripts | `scripts/` |
| Yami product | `products/yami/` |

## Services

| Service | Port | How to start |
|---------|------|-------------|
| Web UI | 5174 | `systemctl --user start jarvis-webui.service` |
| Hermes API | 8000 | `systemctl --user start hermes-gateway.service` |
| OpenClaw Gateway | 18789 | `systemctl --user start openclaw-gateway.service` |
| Qdrant | 6333 | `docker compose -f infra/docker-compose.yml up -d qdrant` |
| Neo4j | 7687 | `docker compose -f infra/docker-compose.yml up -d neo4j` |
| n8n | 5678 | `docker compose -f infra/docker-compose.yml up -d n8n` |
| Playwright MCP | 18990 | `systemctl --user start playwright-mcp.service` |

## Test Results
- `pytest tests/unit/ -q` → 338 pass, 0 fail
- `pytest -q` → 372 pass, 4 fail (integration, need API key)

## Constitution
- Root: `constitution/OMEGA-PROMPT-v10.0.md`
- Soul: `constitution/SOUL.md`
- Governance: VDD → EDD → PDD → ODD → SDD → BDD → TDD
- Score gate: ≥60 to approve any proposal (9 metrics)
- 10 Sub-OS: `prompts/prompts/OS/MANIFEST.md`

## Templates
| Template | Location |
|----------|----------|
| Agent Harness | `harnesses/AGENT-HARNESS-TEMPLATE.md` |
| Skill | `skills/SKILL-TEMPLATE.md` |
| Initiative | `initiatives/initiative-TEMPLATE.md` |
| Event Catalog | `events/CATALOG.md` |
| Enterprise Score | `metrics/enterprise-score.md` |
