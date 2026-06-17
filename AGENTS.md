# Sonora Digital Corp

UN proyecto. Tres agentes base: **JARVIS** (cerebro), **Hermes** (voz/canales), **OpenClaw** (skills). Sub-agentes: builder, reviewer, sdd, code, research, memory.

## Estructura

| Ruta | Qué es |
|------|--------|
| `apps/jarvis/` | Orquestador central: 18 agentes, RAG, Neo4j, Qdrant, harness SDD |
| `apps/webui/` | FastAPI frontend: 20 routers + HTML templates + WebSocket |
| `apps/voice/` | Whisper STT + edge-tts/gTTS engine |
| `apps/hermes/` | MCP bridge + servicios (publisher, thumbnails, youtube) |
| `platforms/telegram/` | Bot runtime (Node.js) + 97 skills JSON de negocio |
| `platforms/whatsapp/` | WhatsApp bridge |
| `packages/` | agent-runtime, sdd-harness, memory (esqueletos, populate as needed) |
| `infra/` | Docker (neo4j/qdrant/mcp), compose, monitoreo, nginx, n8n workflows |
| `specs/` | SDD specs: 000-constitucion a 010 + 23 históricos en archive/ |
| `config/` | Prompts, knowledge, MCP configs, n8n workflows, design tokens |
| `skills/` | 5 skills verticales (creativo, ecommerce, educacion, fitness, musica) |
| `products/` | Clientes: ABE Music, AZREC, Telegram Masterclass, booking |
| `tests/` | Unit (22 tests), integration (3), Playwright E2E (1), mocks |
| `scripts/` | 50+ DevOps, automation, utilities |
| `docs/` | ARQUITECTURA-MENTAL, systems OS (COMPANY-OS, SALES-OS, etc.), business layer |

## Comandos

```bash
pytest tests/unit/                           # unit tests
pytest tests/integration/                    # integration tests
npx playwright test                          # Playwright E2E
ruff check apps/                             # lint
flake8 apps/                                 # flake8 lint (max-line-length=100)
docker compose -f infra/docker-compose.yml up -d  # levantar servicios
cd platforms/telegram && node server.js      # Telegram bot
python apps/jarvis/main.py                   # JARVIS core
```

## Servicios locales

| Puerto | Servicio |
|--------|----------|
| 5174 | Web UI (uvicorn) |
| 8000 | Hermes Agent MCP |
| 18789 | OpenClaw Gateway |
| 6333 | Qdrant (vectores) |
| 7687 | Neo4j (grafos Bolt) |
| 7474 | Neo4j (HTTP) |
| 5678 | n8n workflows |

## SDD Workflow

Revenue Gate → Discovery → Spec → BDD/ATDD → ADR → Plan → Tasks → Code → Verify → Delivery Gate → Archive

Cada spec en `specs/` sigue: `spec.md` → `plan.md` → `tasks.md` → `checklist.md`. Constitution en `specs/000-constitucion/constitution.md`.

## Agentes (opencode.json)

- **mystic**: primary — asistente con identidad SDC
- **explore**: subagent — investiga código y arquitectura
- **builder**: subagent — implementa features
- **reviewer**: subagent — code review y seguridad
- **hermes**: subagent — gateway multi-canal
- **openclaw**: subagent — skills gateway
- **sdd** (+spec/design/apply/verify/archive): subagents — pipeline SDD completo
- **memory**: subagent — contexto persistente (Engram + Neo4j + Qdrant)
- **research**: subagent — búsqueda y síntesis
- **code**: subagent — análisis y generación de código

## Skills paths

- `.opencode/skills` y `.opencode/agents` (repo-local)
- `/home/mystic/.openclaw/workspace/skills` (42 skills: browser-use, stripe, fal-ai, supabase, etc.)
- `/home/mystic/.hermes/skills` (skills de Hermes: TDD, SDD, plan, etc.)
- `/home/mystic/.config/opencode/skills`

## Custom commands (opencode.json)

- `/status` — healthcheck completo del ecosistema
- `/backup` — backup con timestamp a /home/mystic/backups/sdc/
- `/brain` — brain graph dashboard
- `/gsd` — Get Shit Done (discutir→planificar→ejecutar→verificar)
- `/sdd-new` — nueva spec SDD con pipeline completo
- `/build` — construir feature completo siguiendo SDD

## Testing quirks

- `pytest-asyncio` con `asyncio_mode = auto`
- Cobertura mínima 60% (`fail_under = 60`)
- Conftest fuerza fake `MERCADO_PAGO_ACCESS_TOKEN=TEST-fake`
- Playwright en headless=false, viewport 1350x700, baseURL :5174
- Ruff select: E, F, I, UP, B (ignore B008)

## Origen

Consolidado desde `jarvis/` (código activo, backup preservado), `archive-sonora-digital-corp-git/` (referencia histórica), `sdcorp/` (agentes opencode), y `products/` (clientes). Repo GitHub: `github.com/sonoradigitalcorp-H/sonora-digital-corp`.
