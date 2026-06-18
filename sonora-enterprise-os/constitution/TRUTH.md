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

## Key Locations

| What | Where |
|------|-------|
| Monorepo root | `/home/mystic/sonora-digital-corp/` |
| Enterprise OS | `/home/mystic/sonora-digital-corp/sonora-enterprise-os/` |
| Constitution | `sonora-enterprise-os/constitution/MASTER-SYSTEM-PROMPT.md` |
| State (logs, engram, backups) | `state/` |
| JARVIS core engine | `apps/jarvis/` |
| Hermes bridge | `apps/hermes/hermes_bridge.py` |
| Docker compose | `infra/docker-compose.yml` |
| Tests | `tests/` |
| Scripts | `scripts/` |

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

## Constitution (ABRIDGED)
1. One monorepo. No exceptions.
2. Enterprise OS is supreme. Every decision traces to it.
3. Score gate ≥60 to approve any proposal.
4. Deliverable every 48h minimum.
5. ABE Music ($750/week) is primary client.
