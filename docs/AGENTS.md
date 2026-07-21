# OMEGA System — AGENTS.md
## Sonora Digital Corp — Boot Configuration
## Auto-loaded every session

---

## Boot Sequence (Every Session — MUST follow)

1. **Read rules** → `/home/mystic/sonora-digital-corp/memory/learning/rules.json`
2. **Read BOOT** → `/home/mystic/sonora-digital-corp/memory/learning/BOOT.md`
3. **Check 6x manifesto** → `/home/mystic/sonora-digital-corp/ref/6X-BETTER-MANIFESTO.md`
4. **Load methodology** → `/home/mystic/sonora-digital-corp/ref/METHODOLOGY.md`

## System Identity

- **Name**: OMEGA (Operational Methodology for Engineered Growth and Autonomy)
- **Version**: v10.3
- **Pipeline**: VDD → EDD → PDD → ODD → SDD → BDD → TDD
- **Client**: Sonora Digital Corp
- **Models**: nomic-embed-text (local) + qwen2.5:1.5b (local) + deepseek-v4-flash (fallback)

## Infrastructure

- **VPS**: 149.56.46.173 (OVH, 11GB RAM, 96GB SSD, Ubuntu 26.04)
- **SSH**: `ssh -i ~/.ssh/id_ed25519_sdc ubuntu@149.56.46.173`
- **Docker**: Neo4j (7474/7687), Qdrant (6333, 768-dim Cosine), PostgreSQL (5432), Redis (6379), n8n (5678)
- **Services**: abe-server (8080), abe-telegram-bot, ollama (11434), openclaw-gateway (18789)
- **SSL**: sonoradigitalcorp.com + n8n.sonoradigitalcorp.com

## Key Paths

| What | Path |
|---|---|
| Production | `~/sdc/` (VPS) |
| Source | `~/sonora-digital-corp/` (local git) |
| Reference library | `~/sonora-digital-corp/ref/` |
| Learning loop | `~/sonora-digital-corp/memory/learning/` |
| n8n workflows | `~/sonora-digital-corp/config/n8n-sdc/` |
| Static web | `~/sdc/static/` (VPS) |

## Hard Rules (14 active)

- **R-001**: Apple design for public pages. Never dark unpolished.
- **R-002**: Speed mode on URGENTE/RAPIDO/FABOR.
- **R-003**: ONE recommendation, never multiple options.
- **R-004**: Load skills BEFORE writing code.
- **R-005**: End every task with what's done/pending/next.
- **R-006**: APA citations always.
- **R-007**: OMEGA pipeline never skipped.
- **R-008**: TailwindCSS + Apple for public, dark for internal.
- **R-009**: Local models first, OpenCode Go fallback.
- **R-010**: Capture learning events post-session.
- **R-011**: Real data only.
- **R-012**: Never explain code without being asked.
- **R-014**: Keep ref library updated.
- **R-015**: Test 1 item before batch API ops.
- **R-016**: Search system before asking user for keys.
- **R-017**: Load design skill before ANY visual output.
- **R-018**: Temp files for credentials with special chars.
- **R-019**: Output minimal. One line per result.

## Available Skills (67 total, 51 active)

**Key skills for daily use:**
- `popular-web-designs` — 54 design systems (load before any HTML)
- `open-design` — 129 design systems + 31 composable skills
- `fal-ai` — 600+ image/video/audio models
- `meta-ads` — Facebook/Instagram Ads API
- `learning-loop` — Self-improvement engine
- `skill-creator` — Create new skills from workflows
- `playwright` — Browser automation
- `browser-use` — Web testing
- `comfyui` — Local image/video generation
- `canva-connect` — Canva design automation
- `ghost-cms` — Content management
- `stripe` — Payment processing
- `supabase` — Database + auth
- `posthog` — Product analytics
- `mcporter` — MCP server management
- `linux-desktop` — Desktop control
- `agent-evolver` — Self-evolution
- `close-loop` — Session close workflow

## Models

| Task | Model | Type |
|---|---|---|
| Chat/reasoning | qwen2.5:1.5b | Local (Ollama, 1.1GB) |
| Embeddings | nomic-embed-text | Local (Ollama, 274MB, 768-dim) |
| Fallback | deepseek-v4-flash | OpenCode Go (cloud) |
| Images | flux-dev | fal.ai (cloud API) |

## Crisis Protocol

1. `ssh vps` → `docker ps` → `systemctl status ollama`
2. If service down: `sudo systemctl restart <service>`
3. If Docker down: `docker compose -f ~/sdc/docker-compose.yml restart`
4. If VPS dead: provision new → run `setup.sh` (not yet created)

## Quick Commands

| Say | Does |
|---|---|
| `status` | Show VPS health + Docker + Ollama state |
| `deploy` | rsync static files + nginx reload |
| `learn` | Run learning loop extraction |
| `push` | git add + commit + push |
| `n8n:import` | Import workflow JSONs to n8n API |
| `logs:abe` | tail -50 abe-server logs |
| `logs:n8n` | docker logs sdc-n8n -n 30 |
