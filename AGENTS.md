# Sonora Digital Corp — Quick Reference

**One truth**: `sonora-enterprise-os/constitution/OMEGA-PROMPT-v10.0.md`
**Soul**: `sonora-enterprise-os/constitution/SOUL.md`
**Governance**: VDD → EDD → PDD → ODD → SDD → BDD → TDD

---

## People

| Persona | Rol | Nota |
|---------|-----|------|
| **Luis Daniel Guerrero Enciso** | Dueño del sistema | Fundador técnico. Opera desde laptop Linux en Mexico. Habla con el AI. |
| **Noel Nichols** | Socio creativo | Co-construye el proyecto con Luis Daniel. Aporta trabajo colaborativo creativo. |
| **Abraham Ortega** | CEO de ABE Music | Cliente del sistema. Consume vía PWA. No codea ni configura. |

## Machines

| Máquina | IP | OS | Rol | Acceso |
|---------|-----|-----|-----|--------|
| **sdc-prod** (OVH VPS) | `149.56.46.173` | Ubuntu 26.04 | Servidor principal | `ssh ubuntu@149.56.46.173` |
| **laptop** (Luis Daniel) | `187.245.106.218` (dinámica MX) | Linux | Máquina local | Solo sale, no entra (NAT) |

**Reglas**:
- El VPS NO tiene display ni browser — todo es headless
- La laptop NO es accesible desde el VPS
- Para abrir algo en browser de Luis Daniel: necesita SSH forwarding o URL directa a IP publica
- `config/machines.json` tiene todos los detalles persistentes
- `scripts/ver.sh <servicio>` muestra el comando exacto para abrir en laptop

**Forwarding recomendado** (agregar a `~/.ssh/config` en la laptop):
```
Host sdc-prod
  HostName 149.56.46.173
  User ubuntu
  LocalForward 8080 localhost:8080
  LocalForward 5180 localhost:5180
  LocalForward 5174 localhost:5174
```
Luego `ssh sdc-prod` forwards automático. Abrir `http://localhost:8080/` en laptop.

---

## Structure

| Ruta | Qué es |
|------|--------|
| `apps/jarvis/` | 18 agentes, RAG, Neo4j, Qdrant |
| `apps/webui/` | FastAPI frontend + WebSocket |
| `apps/voice/` | Whisper + TTS |
| `apps/hermes/` | MCP bridge + servicios |
| `apps/abe-service/` | **ABE Music OS** — canal interno PWA con voz, avatar, contratos, revenue, CRM |
| `planner/` | Capability Registry + Decision Engine — 7 módulos, 70 tests |
| `scrapers/` | 8 colectores (Deezer, Apple Music, YouTube, Wikipedia, TikTok, Spotify, Instagram, Facebook) |
| `scrapers/sync.py` | Sync orchestrator migrado a decision engine |
| `config/registry.json` | Registry v2: 3 capabilities, 10 providers |
| `platforms/telegram/` | Bot + 97 skills |
| `platforms/whatsapp/` | Bridge |
| `infra/` | Docker, compose, monitoreo, n8n |
| `products/` | ABE Music, AZREC, Masterclass |
| `tests/` | 79 tests (26 legacy + 8 ABE Service + 70 planner) |
| `tests/planner/` | 70 tests: models, registry, health, engine, events |
| `scripts/` | 50+ DevOps |
| `process/completed/SPEC-20260701-004/` | Capability Registry + Decision Engine (Score 77) |
| `process/completed/20260701-live-data-pipeline/` | Live Data Pipeline (Score 84) |
| `sonora-enterprise-os/` | Enterprise OS completo |

## Comandos

```bash
pytest tests/unit/              # unit tests
pytest tests/integration/       # integration
pytest tests/planner/ -v        # planner tests (70)
pytest tests/test_abe_service.py -v  # ABE Service tests (9)
npx playwright test             # E2E
ruff check planner/ scrapers/ tests/ apps/  # lint all
PYTHONPATH=. python scrapers/sync.py  # full sync cycle
PYTHONPATH=. python -c "from planner import execute_capability; import asyncio; print(asyncio.run(execute_capability('acquire-metadata', {'artist_name':'Hector Rubio'})))"  # test engine
docker compose -f infra/docker-compose.yml up -d
python apps/jarvis/main.py      # JARVIS core
python -m uvicorn apps.abe-service.main:app --host 127.0.0.1 --port 5180  # ABE Service
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
| 5180 | **ABE Service** | `abe-service.service` --user |
| 8080 | Evolucion Dashboard | `evolucion-dashboard.service` --user |

## Comandos utiles

```bash
bash scripts/ver.sh presentacion  # muestra como abrir presentacion en laptop
bash scripts/ver.sh abe           # muestra como abrir ABE Service en laptop
bash scripts/deploy.sh            # genera + despliega presentacion
tmux attach -t presentacion       # ver presentacion en terminal
ssh -L 8080:localhost:8080 ubuntu@149.56.46.173  # forwarding para laptop
```

## Revenue Intelligence

| Artista | Streams | Revenue | Spotify ML | Tasa |
|---------|---------|---------|------------|------|
| Hector Rubio | 115,093,009 | $460,372 | 1,028,288 | $0.004/stream |
| Jesus Urquijo | 4,635,222 | $18,540 | 24,278 | $0.004/stream |
| Javier Arvayo | 50,000 | $200 | 73,680 | $0.004/stream |

**→ 100% Spotify. Oplaai no paga multi-plataforma.**

## Key Learnings (SPEC-20260701-004)

- Capability-first abstractions: registry fuerza todas las abstracciones
- SDK executor bridge necesario para conectar engine con collectors multi-step
- Fallback por weight > health-first (más robusto)
- Browser scraping frágil pero necesario sin API keys
- Instagram bloqueado (login wall) — Wikipedia bloqueado (datacenter 403)
- Sync cron no instalado aún — script en `scripts/install-sync-cron.sh`

## Session HTML

Estado completo desplegado en:
- `apps/abe-service/pwa/estado.html` (via ABE Service :5180/pwa/estado.html)
- `docs/SONORA-EVOLUTION.html` (via python http.server :9090)
- `memory/learning/session-20260701.json` (memoria de agentes)

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
- `/presentar` — genera presentacion reveal.js de la sesion actual
- `/deploy` — genera + despliega presentacion a :8080

## Templates

| Template | Location |
|----------|----------|
| Agent Harness | `harnesses/AGENT-HARNESS-TEMPLATE.md` |
| Skill | `skills/SKILL-TEMPLATE.md` |
| Initiative | `initiatives/initiative-TEMPLATE.md` |
| Event Catalog | `events/CATALOG.md` |
| Enterprise Score | `metrics/enterprise-score.md` |

Enterprise Score: ≥60 para aprobar (10 metrics × 10, max 100).
