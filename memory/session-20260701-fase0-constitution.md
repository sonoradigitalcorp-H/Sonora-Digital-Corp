# Session: Fase 0 — Constitution + Foundation

**Date**: 2026-07-01 (afternoon)
**Duration**: ~2h

## What was built

### Constitution (`constitution/`)
- `MANIFESTO.md` — Entry point for all agents
- `000-governance.md` — Purpose, mission, absolute law (migrated from OMEGA-PROMPT)
- `010-agent-rules.md` — 10 rules, SDD pipeline, autonomy levels (migrated from 10-RULES)
- `020-data-policy.md` — Paths, locations, collector schema, pipeline system (migrated from TRUTH)
- `030-security.md` — Secrets policy, service access, incident response
- `040-evolution.md` — Amendment process, versioning, review cycle

### Research completed
- Explored: IronCurtain, Vectimus, Cordum, smolagents, Neo4j GraphRAG, crw, Playwright MCP
- Decision: No Spotify API → Collector methodology (Deezer, YouTube, Wikipedia, etc.)
- crw selected as central scraper (Rust, ~50MB RAM, MCP server included)
- Playwright MCP for JS-heavy sites (TikTok, YouTube)

### VPS setup
- Installed opencode 1.17.13 on VPS (149.56.46.173)
- Copied opencode.json config + .opencode/agents + .opencode/skills
- All Docker containers confirmed running (Neo4j, Qdrant, PostgreSQL, Redis, n8n, etc.)

### Key decisions
1. No Spotify API — collectors via public data sources instead
2. Fase 0 = Constitution + scraper infra + agent runtime + policy engine
3. Local dev → commit → VPS pull (production deployment)
4. IronCurtain for compiled policies, Vectimus for enforcement

## Pending for next session
- Install IronCurtain on VPS (`npm install -g @provos/ironcurtain`)
- Deploy crw on VPS (`docker compose -f scrapers/docker-compose.scrapers.yml up -d`)
- Install smolagents on VPS
- Install Vectimus on VPS (if PyPI package available)
- Add Playwright MCP to MCP Gateway
- Create GitHub Actions workflow for constitution validation
- Update opencode.json to reference new constitution
- Verify tests still pass on VPS

## Lessons
- VPS had Docker infra but no development tools — important distinction
- opencode config needs explicit PATH setup on fresh installs
- Constitution first, tools second, collectors third — correct dependency order
