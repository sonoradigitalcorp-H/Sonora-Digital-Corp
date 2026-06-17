# Sonora Digital Corp — Quick Reference

**One truth**: `sonora-enterprise-os/constitution/MASTER-SYSTEM-PROMPT.md`
**Governance**: VDD → EDD → PDD → SDD → BDD → TDD

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

| Puerto | Servicio |
|--------|----------|
| 5174 | Web UI |
| 8000 | Hermes MCP |
| 18789 | OpenClaw Gateway |
| 6333 | Qdrant |
| 7687 | Neo4j |
| 5678 | n8n |

## Agentes

`mystic` (primary) + explore, builder, reviewer, hermes, openclaw, sdd/*, memory, research, code.

## Comandos rápidos opencode

- `/status` — healthcheck
- `/backup` — backup
- `/brain` — brain graph
- `/gsd` — Get Shit Done
- `/sdd-new` — nueva spec
- `/build` — construir feature

Enterprise Score: ≥60 para aprobar (8 metrics × 10).
