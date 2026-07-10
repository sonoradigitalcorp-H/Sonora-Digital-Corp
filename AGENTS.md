# Sonora Digital Corp — Quick Reference

**One truth**: `constitution/OMEGA-PROMPT.md`
**Soul**: `constitution/SOUL.md`
**Governance**: HAS-007 Pipeline (Mission → Constitution → Research → Architecture → Simulation → Specification → Implementation → Verification → Observability → Evolution)
**Architecture**: HAS-000 through HAS-011 in `process/has/`

---

## Última sesión: 2026-07-10 — ~40 proyectos (la más grande)

### Producto estrella: Mystik AI 🎯
- **Mystik API** (:5200) — FastAPI backend: chat con OpenRouter AI, leads, voz, multi-tenant, knowledge base
- **Lobe Chat UI** (:3210) — PWA mobile-first con branding Mystik (color #FF6B35)
- **Voice pipeline**: Whisper STT + OpenVoice TTS + OmniVoice cloning. Endpoints: `/speak`, `/transcribe`, `/clone`
- **Multi-tenant**: DB SQLite con tenants aislados. API CRUD. 2 precargados (sonora, demo)
- **CRM**: ABE CRM (:5180) conectado. Twenty CRM (:3002) con schema creado
- **ChromaDB** (:8001) — RAG sobre productos SDC
- **LiveKit** (:7880) — WebRTC para voz en tiempo real
- **Coolify** (:80) — Open-source Vercel instalado

### Sesión completa: ~40 entregables
| Categoría | Items |
|-----------|-------|
| **Nuevo producto** | Mystik AI (API + UI + voz + CRM + multi-tenant) |
| **Kernels** | L1 Observe, L2 Understand, L3 Decide, L4 Act, L5 Measure, L6 Learn, L7 Control |
| **5 proyectos GSD** | Capability Bus, Founder Index, Enterprise Score, Knowledge Ingestion, Weekly Reports |
| **Fixes** | 19 tests rotos → 0, 24 ADK YAMLs rotos → 36 válidos, 6 duplicados eliminados |
| **Infra** | Coolify instalado, SSL automation workflow, catalog.yaml 57→111 eventos |
| **Auditoría** | 5 reportes (MCPs, eventos, infra, estructura, prompts comunitarios) |

### 759 tests ✅ — 0 fallos | 15+ servicios activos | 170+ endpoints

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
  LocalForward 8502 localhost:8502
  LocalForward 5055 localhost:5055
```
Luego `ssh sdc-prod` forwards automático. Abrir en laptop:
- `http://localhost:8080/` — Evolution Dashboard
- `http://localhost:5174/` — Web UI
- `http://localhost:8502/` — Open Notebook (RAG con documentos)

---

## Structure

**Core OS** — `apps/`, `infra/`, `constitution/`, `process/`, `config/`, `scrapers/`, `platforms/`, `scripts/`
**Productos** — `products/<name>/`

| Ruta | Qué es | Dominio |
|------|--------|---------|
| `apps/jarvis/src/core/` | Core OS — módulos backend (neo4j_store, brain_graph, rag, llm) | Core |
| `apps/webui/` | FastAPI frontend + WebSocket (:5174) | Core |
| `apps/voice/` | Whisper + TTS | Core |
| `apps/hermes/` | MCP bridge + publisher + thumbnails | Core |
| `apps/abe_service/` | **ABE Music OS** — PWA, contratos, revenue, CRM | Core |
| `apps/observe→control/` | Niveles 1-7 Cognitive Kernel | Core |
| `planner/` | Capability Registry + Decision Engine | Core |
| `scrapers/` | 8 colectores artísticos | Core |
| `platforms/` | Telegram bot, WhatsApp bridge | Core |
| `products/content-studio/` | Content gen: images, TTS, talking heads, queue | **Producto** |
| `products/omnivoice/` | Voice cloning (Docker image, :3900) | **Producto** |
| `products/open-notebook/` | Open-source NotebookLM: RAG, PDFs, web, podcast (Docker) | **Producto** |
| `infra/` | Docker, compose, monitoreo | Core |
| `tests/` | 78 tests (5 suites) | Core |
| `scripts/` | DevOps + close-session + constitution-gate | Core |

## Comandos

```bash
PYTHONPATH=. python3 -m pytest tests/ -q          # all tests (78+)
PYTHONPATH=. python3 -m pytest tests/test_execution.py -v  # Execution (24)
PYTHONPATH=. python3 -m pytest tests/test_evolution.py -v  # Evolution (19)
PYTHONPATH=. python3 -m pytest tests/test_collectors/ -v   # Collectors (17)
PYTHONPATH=. python3 -m pytest tests/test_constitution.py -v  # Constitution (10)
PYTHONPATH=. python3 -m pytest tests/test_abe_service.py -v  # ABE (9)
ruff check apps/ collectors/ tests/ constitution/  # lint
python3 scripts/constitution-gate.py --plan PLAN.yaml  # 6-gate constitution check
python3 scripts/evolution-cron.sh                   # Evolution Engine cron
python3 scripts/close-session.sh --dry-run          # test close flow
scripts/up.sh                          # start all (core + products)
docker compose -f infra/docker-compose.yml up -d    # core only
docker compose -f infra/docker-compose.products.yml up -d  # products only
python -m uvicorn apps.abe_service.main:app --host 127.0.0.1 --port 5180  # ABE Service
```

## Servicios

| Puerto | Servicio | Dominio | Systemd |
|--------|----------|---------|---------|
| 5174 | Web UI | Core | `jarvis-webui.service` --user |
| 8000 | Hermes MCP | Core | `hermes-gateway.service` --user |
| 18789 | OpenClaw Gateway | Core | `openclaw-gateway.service` |
| 6333 | Qdrant | Core | Docker |
| 7687 | Neo4j | Core | Docker |
| 5678 | n8n | Core | Docker (33 workflows) |
| 5180 | **ABE Service** | Core | `abe-service.service` --user |
| 8080 | Evolution Dashboard | Core | `evolucion-dashboard.service` --user |
| 8765 | **Content Server MCP** | **Producto** | Docker |
| 8766 | **Edge TTS API** | **Producto** | Docker |
| 8768 | **Content Storage (nginx)** | **Producto** | Host |
| 8502 | **Open Notebook UI** | **Producto** | Docker |
| 5055 | **Open Notebook API** | **Producto** | Docker |
| 3900 | **OmniVoice** | **Producto** | Docker |

## SSL Automation

`scripts/ssl-auto.sh` + `.github/workflows/ssl-auto.yml` automatizan SSL para nuevos dominios.

### Desde GitHub (recomendado)
Ir a Actions → SSL Auto → Run workflow → ingresar dominio, puerto, email.

### Desde VPS
```bash
bash scripts/ssl-auto.sh client.sonoradigitalcorp.com 3001 email@example.com
```

El workflow usa `secrets.VPS_SSH_KEY` para conectar al VPS y:
1. Obtiene certificado Let's Encrypt via certbot
2. Genera config nginx en `/etc/nginx/sites-enabled/ssl-auto-{domain}.conf`
3. Recarga nginx

El nginx principal incluye automáticamente: `include /etc/nginx/sites-enabled/ssl-auto-*.conf`

## Comandos utiles

```bash
bash scripts/ver.sh presentacion  # muestra como abrir presentacion en laptop
bash scripts/ver.sh abe           # muestra como abrir ABE Service en laptop
bash scripts/ver.sh open-notebook # muestra como abrir Open Notebook en laptop
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

## Key Learnings

### SPEC-20260701-004
- Capability-first abstractions: registry fuerza todas las abstracciones
- SDK executor bridge necesario para conectar engine con collectors multi-step
- Fallback por weight > health-first (más robusto)
- Browser scraping frágil pero necesario sin API keys
- Instagram bloqueado (login wall) — Wikipedia bloqueado (datacenter 403)

### SPEC-20260710 (Fork Products)
- SSH key en VPS auth al user account, NO a org repos. Para pushear a org repos usar HTTPS con token: `git remote set-url origin https://x-access-token:${GH_TOKEN}@github.com/sonoradigitalcorp-H/<repo>.git`
- GitHub API (`gh`) funciona con OAuth token aun si SSH push falla
- `scripts/fork-product.sh` automatiza extract + standalone repo creation

## Protocolo de Construccion

`docs/PROTOCOLO.md` — 7 mandamientos + checklist para no fallar.
Leer antes de empezar cualquier tarea nueva.

## Session HTML

Estado completo desplegado en:
- `apps/abe_service/pwa/estado.html` (via ABE Service :5180/pwa/estado.html)
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
- `/doc` — genera docs de proceso (SPEC, SCORE, ADR, LECCION, gherkin, events)

## Close Session (AUTO-CLOSE)

`scripts/close-session.sh` automatiza todo el cleanup post-sesión:

```
./scripts/close-session.sh --spec-id SPEC-xxx --title "Mi Feature" --tier 3 --summary "..."
```

Pipeline: tests gate → auto-doc → move SPECs activos → update AGENTS.md → merge CATALOGs → commit + push → VPS sync automático.

Flags:
- `--dry-run` — muestra el plan sin ejecutar
- `--interactive` — pregunta antes de cada paso
- `--no-tests` — saltea gate de tests
- `--no-push` — hace commit pero no push
- `--force` — sobreescribe docs existentes

## Documentación de Proceso (AUTO-DOC)

Cada sesión debe documentarse siguiendo CONDUCT.md. **No marcar DONE sin documentar.**

Reglas:
1. **Toda sesión con cambios** (no solo consulta) genera directorio en `process/completed/`
2. **Tier 2** requiere: SPEC.md, SCORE.md, gherkin, ADR.md, events.jsonl, LECCION.md
3. **Tier 3** requiere: VDD→EDD→PDD→ODD→SDD→BDD→TDD + ADR + events + LECCION
4. **Al terminar**: ejecutar `/doc` para auto-generar docs desde resumen de sesión
5. Si `/doc` no captura todo, completar manualmente siguiendo `process/templates/`

Comandos:
- `python3 scripts/auto-doc.py --auto` — auto desde AGENTS.md
- `python3 scripts/auto-doc.py --spec-id SPEC-xxx --title "..." --tier 3 --summary "..."` — manual
- `/doc` — via process-doc agent

## Templates

| Template | Location |
|----------|----------|
| Agent Harness | `harnesses/AGENT-HARNESS-TEMPLATE.md` |
| Skill | `skills/SKILL-TEMPLATE.md` |
| Initiative | `initiatives/initiative-TEMPLATE.md` |
| Event Catalog | `events/CATALOG.md` |
| Enterprise Score | `metrics/enterprise-score.md` |

Enterprise Score: ≥60 para aprobar (10 metrics × 10, max 100).

## Cognitive Kernel (NUEVO — 2026-07-03)

Arquitectura de 3 fases implementada: Foundations (A), Kernel Separation (B), Intelligence Layer (C).

### Directorios clave
| Ruta | Qué es |
|------|--------|
| `process/has/` | **Hermes Architecture Standard** — 11 specs (HAS-000 through HAS-011) |
| `constitution/` | 16 archivos YAML, Niveles 0-5 — fuente única de verdad (HAS-001) |
| `truth/ → constitution/` | Backward-compat symlink |
| `agents/registry.yaml` | 11 agentes con capabilities explícitas |
| `agents/capabilities/` | 8 definiciones de capabilities |
| `agents/policies/` | 7 policies (deny-all por defecto) |
| `state/memory/` | 3 DBs con TTL (working/project/organization) |
| `state/events/catalog.yaml` | Schema de eventos unificado |
| `state/execution/` | Execution Kernel: SQLite queue + checkpoints |
| `state/evolution/` | Evolution Loop: propuestas + decisiones |
| `apps/observe/` | Nivel 1: collectors, events pipeline |
| `apps/understand/` | Nivel 2: truth, knowledge, memory |
| `apps/decide/` | Nivel 3: planning, economics, execution |
| `apps/act/` | Nivel 4: agents, capabilities |
| `apps/measure/` | Nivel 5: scoreboard, guardian, verification |
| `apps/learn/` | Nivel 6: heuristics, evolution |
| `apps/control/` | Nivel 7: dashboard unificado |
| `collectors/` | Artist Intelligence Network: 4 collectors + registry |
| `config/generated/` | Configs autogeneradas desde fleet.yml |

### Nuevos comandos
| Comando | Qué hace |
|---------|----------|
| `/plan` | Planning Gate: descompone objetivo en tareas |
| `/verify` | Constitution Gate: 6 gates (policy/security/cost/compliance/quality/knowledge) — `scripts/constitution-gate.py` |
| `/evolve` | Evolution Engine: `python3 -m evolution.main --mode full` |
| `python3 scripts/check-capability.py <agent> <cap>` | Verifica capability |
| `python3 scripts/constitution-gate.py --plan PLAN.yaml` | 6-gate constitution check (HAS-001) |
| `python3 scripts/evolution-cron.sh` | Evolution Engine every 6h (HAS-008) |

### API (Truth Guardian, :8088)
| Endpoint | Respuesta |
|----------|-----------|
| `GET /api/v1/status` | Drifts + health + status general |
| `GET /api/v1/health` | Health check simple |
| `GET /api/v1/drift` | Lista de drifts detectados |
| `GET /api/v1/scoreboard` | Métricas por agente |
| `GET /api/v1/events/recent` | Últimos eventos del bus |
| `GET /api/v1/cost/summary` | Costos por agente desde economics.db |
| `GET /api/v1/execution/stats` | Stats de la cola de ejecución |
| `GET /api/v1/execution/tasks` | Lista de tareas (filtrable) |
| `POST /api/v1/execution/submit` | Encola nueva tarea |
| `POST /api/v1/execution/cancel/:id` | Cancela tarea |
| `POST /api/v1/execution/retry/:id` | Reintenta tarea fallida |
| `GET /scoreboard` | SPA scoreboard interactivo |
| `GET /control` | Control Plane dashboard SPA |

### Sincronización
- `scripts/sync-to-vps.sh` → rsync + regenerate + restart
- `.github/workflows/sync-vps.yml` → GitHub Action que hace git pull en VPS

### Enterprise Score actual: 88/100

### Última sesión: 2026-07-08 — Hermes Architecture Standard (HAS)
- 11 HAS specification files creados (HAS-000 through HAS-011) en `process/has/`
- `truth/` → `constitution/` migration completada (16 YAMLs, symlink, 20 tests verdes)
- `scripts/constitution-gate.py` — 6-gate replacement for verify-gate.py (HAS-001)
- `scripts/evolution-cron.sh` + `evolution/main.py` — Evolution Engine stub (HAS-008)
- `process/CONDUCT.md` actualizado con HAS-007 pipeline
- `scripts/close-session.sh` actualizado con Evolution Engine auto-doc
- `AGENTS.md` actualizado con HAS architecture, constitution dir, pipeline v2
- Capabilities scaffold: `capabilities/index.yaml` + `sync-artist-data/` primer capability
- Git push history: `3df0d48` → `5fe15fb` → `ff0171d` + pending commit

### Sesión anterior: 2026-07-04 — ECA Fase 1
- 40 archivos nuevos, 15 movidos, 0 borrados
- 78 tests (5 suites), 0 fallos
- Stack Lock, Vercel Secrets, GitHub Pages, 7 niveles cognitivos
- Execution Kernel (24 tests) + Evolution Loop (19 tests) + Artist Intelligence (17 tests)
- Control Plane + Scoreboard Dashboard
