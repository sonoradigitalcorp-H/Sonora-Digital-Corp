# AGENTS.md — Sonora Digital Corp

**Constitution**: `constitution/SOUL.md` + `constitution/OMEGA-PROMPT.md`
**Architecture**: `process/has/HAS-000-index.md` (HAS-000 through HAS-011)
**Active spec**: `process/active/` — read before acting
**Remote**: `git@github.com:sonoradigitalcorp-H/Sonora-Digital-Corp.git` (SSH key)

---

## VPS — sdc-prod (149.56.46.173)

- Ubuntu 26.04, headless (no display, no browser)
- 11GB RAM, 96GB disk (84% used — 17GB free)
- **WARNING**: swap 100% full (~2GB), free RAM <200MB — containers get OOM-killed under load
- **WARNING**: n8n needs postgres ready first. If n8n is unhealthy (`DB timeout`), restart AFTER postgres is up
- Laptop (Luis Daniel) is behind NAT — unreachable from VPS. Use SSH forwarding for browser access.

## Commands (verified)

```bash
make              # list targets
make test         # 852 tests collected, 27 collection errors (import paths — known issue)
make lint         # ruff (LOCAL only — not installed on VPS)
make lint-fix     # ruff --fix (LOCAL only)
make eval         # structural evals + promptfoo
make score        # enterprise score
```

## Docker

```bash
# Core infra (postgres, redis, neo4j, qdrant, n8n, prometheus)
docker compose -f infra/docker-compose.yml up -d

# VPS override
docker compose -f infra/docker-compose.yml -f infra/docker-compose.vps.yml up -d

# Health overview
docker ps -a --format 'table {{.Names}}\t{{.Status}}'
docker stats --no-stream

# Rebuild MCP image (after changing mcp/Dockerfile)
cd mcp && docker build -t sdc-mcp-server:latest .
docker rm -f sdc-adk-runtime sdc-hermes-mcp
# Then recreate with: -v /home/ubuntu/sonora-digital-corp/config:/config:rw --network sdc-network
```

## Gotchas

- **MCP Dockerfile**: copies entire `mcp/` dir now (was only partial). Volume must mount config at `/config` NOT `/app/config` because `path.join(__dirname, '../..', 'config')` resolves to `/config` when `__dirname=/app/gateway`.
- **n8n DB timeout**: sdc-n8n must start AFTER sdc-postgres is healthy. Restart: `docker restart sdc-n8n`.
- **Test collection errors**: 27 import errors in `tests/unit/` (`test_unified_bridge.py`, `test_verify.py`, `test_voice.py`). These don't block integration/eval/structural tests.
- **ruff not on VPS**: lint commands only work locally. VPS has no dev tooling.

## Key paths

```
config/       — tenants.json, registry.json, ambassadors.yaml, whatsapp-product.yaml
mcp/gateway/  — MCP HTTP server (port 18989), mcp-server-http.js
mcp/servers/  — wacli_mcp.py (WhatsApp CLI tools)
mcp/Dockerfile — full image build for sdc-mcp-server
infra/        — docker-compose files, systemd units, qdrant/neo4j Dockerfiles
ops/          — api_bridge.py (WebSocket chat), voice/, code/
state/        — engram.db, engram/, events/, whatsapp/
process/active/ — current specs, ADRs, scores
clients/      — abe-music, azrec, el-joyero
scripts/      — 70+ shell scripts (start-session, end-session, backup, etc.)
```

## References

- `CLAUDE.md` — session workflow (start/end/branch/PR)
- `Makefile` — all dev commands
- `constitution/` — governance, rules, security, evolution
- `docs/` — maps, protocols, presentations
