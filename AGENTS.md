# AGENTS.md — Sonora Digital Corp

**Constitution**: `kernel/SOUL.md` + `kernel/OMEGA-PROMPT.md`
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

## Architecture — 6 Capas Concéntricas

```
kernel/        ← Capa 0: identidad, reglas, constitución
infra/         ← Capa 1: infraestructura SSOT (fleet.yml, docker, nginx)
apps/          ← Capa 2: servicios core del sistema
products/      ← Capa 3: lo que SDC vende (cada producto aislado)
clients/       ← Capa 4: clientes externos (cada uno en su galaxia)
portal/        ← Capa visual: Grimoire 3D con Three.js — la galaxia SDC
ops/           ← Capa transversal: playbooks, runbooks, recovery
state/         ← Capa transversal: estado vivo del sistema (registry, eventos)
reference/     ← Capa transversal: specs cerradas, arqueología
```

Regla de oro: **El core NO se mezcla con clientes**. Lo que está en kernel/, infra/,
apps/ pertenece a Sonora Digital Corp como empresa. Productos y clientes
importan del core, nunca al revés.

## Portal — Grimoire 3D

```bash
# Servir localmente
python3 -m http.server 8080 --directory portal/
# Abrir: http://localhost:8080

# Subir al VPS (cuando esté disponible)
rsync -avz portal/ sdc-prod:/var/www/brain/
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

# Rebuild MCP image (after changing skills/mcp/Dockerfile)
cd skills/mcp && docker build -t sdc-mcp-server:latest .
docker rm -f sdc-adk-runtime sdc-hermes-mcp
# Then recreate with: -v /home/ubuntu/sonora-digital-corp/config:/config:rw --network sdc-network
```

## Gotchas

- **MCP Dockerfile**: copies entire `skills/mcp/` dir now (was only partial). Volume must mount config at `/config` NOT `/app/config` because `path.join(__dirname, '../..', 'config')` resolves to `/config` when `__dirname=/app/gateway`.
- **n8n DB timeout**: sdc-n8n must start AFTER sdc-postgres is healthy. Restart: `docker restart sdc-n8n`.
- **Test collection errors**: 27 import errors in `tests/unit/` (`test_unified_bridge.py`, `test_verify.py`, `test_voice.py`). These don't block integration/eval/structural tests.
- **ruff not on VPS**: lint commands only work locally. VPS has no dev tooling.

## Key paths

```
config/            — tenants, registry, ambassadors, secrets
config/tenants/    — Tenant configs per client
skills/mcp/        — MCP tools (gateway, servers, SDK, CLI)
skills/            — All skills + reusable tools unificados
apps/core/         — Motor único del sistema (engine, planner, executors, agents)
apps/evolution/    — Auto-evolución, scorecard, aprendizaje
infra/             — docker-compose files, fleet.yml, systemd units, qdrant/neo4j Dockerfiles
scripts/           — api_bridge.py (WebSocket chat), voice/, code/, 70+ scripts
state/             — engram.db, engram/, events/, whatsapp/
state/events/      — Sistema de eventos del core
process/           — Pipeline de SPECs activos/completados + specs
clients/           — abe-music, azrec, el-joyero, nathy-conta
products/          — mystic-shield, mystika, abe-music, clon-digital, nsfw-studio, omnivoice...
portal/            — Grimoire 3D (Three.js galaxy — la interfaz visual del sistema)
ops/playbooks/     — Recetas paso a paso para procedimientos estandarizados
adrs/              — Architecture Decision Records
```

## Preflight / Doctor

```bash
make doctor          # full validation (JSON, YAML, Docker, Git, env)
make doctor-quick    # rápido (sin Docker/Git)
make doctor-fix      # auto-corrige lo posible
make validate-configs  # solo configs
```

El comando `scripts/preflight.py` valida toda la configuración del proyecto antes de desarrollar. Ejecútalo siempre que edites `opencode.json`, YAMLs de infraestructura, o config de tenants.

Errores comunes que detecta:
- JSON mal formado (el que tuviste con la `}` extra)
- Claves `apiKey`/`fallbackProvider` incompatibles con OpenCode v1.18+
- YAML con sintaxis inválida
- Templates con variables Jinja2 no parseables
- Permisos de scripts no ejecutables
- Variables de entorno faltantes

```bash
# Alias recomendado para ~/.bashrc:
alias occheck='make doctor-quick && opencode --version'
```

## References

- `CLAUDE.md` — session workflow (start/end/branch/PR)
- `Makefile` — all dev commands
- `kernel/` — governance, rules, security, evolution
- `docs/` — maps, protocols, presentations
- `portal/data/system.json` — SSOT del estado del sistema para el Grimoire
- `adrs/ADR-20260722-ARQUITECTURA-CORE.md` — la ADR de esta arquitectura
