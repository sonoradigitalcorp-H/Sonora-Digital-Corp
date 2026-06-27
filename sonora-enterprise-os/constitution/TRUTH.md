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
| `~/SonoraDigitalCorp-Yami/` | `🚫 OBSOLETO — movido a sonora-enterprise-os/` |
| `$YAMI_HOME` | `🚫 OBSOLETO — movido a sonora-enterprise-os/` |
| `archive-sonora-digital-corp-git/` | `🚫 OBSOLETO — movido a backups/repos/` |

## Key Locations

| What | Where |
|------|-------|
| Monorepo root | `/home/mystic/sonora-digital-corp/` |
| Enterprise OS | `/home/mystic/sonora-digital-corp/sonora-enterprise-os/` |
| Constitution | `sonora-enterprise-os/constitution/OMEGA-PROMPT-v10.0.md` |
| RULES | `sonora-enterprise-os/constitution/10-RULES.md` |
| CONTRATO | `sonora-enterprise-os/constitution/CONTRATO.md` |
| Checksums | `sonora-enterprise-os/constitution/CHECKSUMS.sha256` |
| State (logs, engram, backups) | `state/` |
| JARVIS core engine | `apps/jarvis/` |
| Hermes bridge | `apps/hermes/hermes_bridge.py` |
| Docker compose | `infra/docker-compose.yml` |
| Tests | `tests/` |
| Scripts | `scripts/` |
| Enterprise OS scripts | `sonora-enterprise-os/scripts/` |
| Enterprise OS specs | `sonora-enterprise-os/specs/` |
| Enterprise OS templates | `sonora-enterprise-os/templates/` |
| Enterprise OS memory | `sonora-enterprise-os/memory/` |
| Enterprise OS docs | `sonora-enterprise-os/docs/` |

## VPS Info

| What | Value |
|------|-------|
| IP | 149.56.46.173 |
| OS | Ubuntu 26.04 |
| User | ubuntu |
| SSH key | `~/.ssh/id_ed25519_sdc` |
| SSH host | 149.56.46.173 |
| Monorepo path | `/home/ubuntu/sdc/` |
| OpenClaw | `openclaw gateway run` via systemd (port 18789, token in `~/.openclaw/gateway.env`) |
| Hermes | `/home/ubuntu/hermes-agent/venv/bin/hermes` (Python 3.13, v0.16.0) |
| n8n | Docker, port 5678, API key configured |
| Docker services | n8n, neo4j, qdrant, postgres, redis (all healthy) |

## Services

| Service | Port | How to start |
|---------|------|-------------|
| Web UI | 5174 | `systemctl --user start jarvis-webui.service` |
| Hermes API | 8000 | `systemctl --user start hermes-gateway.service` |
| OpenClaw Gateway | 18789 | `~/.openclaw/openclaw.json` — `openclaw gateway run` |
| Qdrant | 6333 | `docker compose -f infra/docker-compose.yml up -d qdrant` |
| Neo4j | 7687 | `docker compose -f infra/docker-compose.yml up -d neo4j` |
| n8n | 5678 | `docker compose -f infra/docker-compose.yml up -d n8n` |
| Playwright MCP | 18990 | `systemctl --user start playwright-mcp.service` |
| OpenClaw (VPS) | 18789 | `systemctl --user start openclaw-gateway.service` |

## Test Results
- `pytest tests/unit/ -q` → 338 pass, 0 fail
- `pytest -q` → 372 pass, 4 fail (integration, need API key)

## Constitution
- Root: `constitution/OMEGA-PROMPT-v10.0.md`
- Soul: `constitution/SOUL.md`
- RULES: `constitution/10-RULES.md`
- CONTRATO: `constitution/CONTRATO.md`
- Governance: VDD → EDD → PDD → ODD → SDD → BDD → TDD → CODE → **OBS → EVA**
  - **OBS** (Observabilidad): LangFuse — traces, cost tracking, dashboard en vivo
  - **EVA** (Evaluación): DeepEval — eval suite, CI/CD gates, feedback loop
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
| Spec (SDD) | `sonora-enterprise-os/templates/spec-template.md` |
| Plan | `sonora-enterprise-os/templates/plan-template.md` |
| Tasks | `sonora-enterprise-os/templates/tasks-template.md` |
| Feature (Gherkin) | `sonora-enterprise-os/templates/TEMPLATE.feature` |
| Discovery | `sonora-enterprise-os/templates/DISCOVERY.md` |
| Issue | `sonora-enterprise-os/templates/issue-template.md` |
