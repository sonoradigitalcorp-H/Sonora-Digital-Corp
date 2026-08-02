# Changelog

All notable changes to Sonora Digital Corp will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-08-02

### Added
- **Core Engine**: 5-layer agentic pipeline (Context → Planner → Router → Decision Engine → Executor)
- **MCP Ecosystem**: 35 MCP servers with 98+ tools (messaging, voice, payments, AI, media, browser, data, business)
- **Gateway**: `sonora-mcp-gateway` at port 18989 with JWT auth and 108 tools
- **Multi-Tenant**: 8 tenants configured (sonora-digital, astrotech, abe-music, nathy-conta, el-joyero, azrec, mds-corp, r1)
- **Telegram Bot**: 102 skills covering facturación, SAT, finanzas, soporte, ventas
- **WhatsApp Bots**: 3 responders (Ce-Son, Mystic, JARVIS) with kill switches
- **Social Media**: Instagram + Facebook auto-responder with Playwright
- **Voice Pipeline**: edge-tts (DaliaNeural) + faster-whisper (local, $0 cost)
- **OmniVoice**: Voice cloning product at port 3900
- **Engram Memory**: 7-layer persistent memory system with FTS5 search
- **n8n Workflows**: 49 workflows (14 active, 6 active with issues)
- **SDD Framework**: Dual-track pipeline (internal skills + SpecKit) with CLI tool
- **GitHub Actions**: 29 CI/CD workflows (deploy, CI, monitor, security, process-gate)
- **Docker**: 9 core services with health checks, memory limits, 127.0.0.1 binding
- **systemd**: 21 services + 3 timers
- **Tests**: 628 tests collected, 139 unit tests stable
- **Documentation**: ADRs (17+), specs (22), Gherkin features (21), blueprint

### Fixed
- **Security**: Removed hardcoded Telegram token from `telegram-scheduler.service`
- **Security**: Enabled Neo4j authentication in Dockerfile
- **Security**: Removed hardcoded passwords from docker-compose.yml (4 instances)
- **Security**: Updated `.env.example` with all 28 required variables
- **Bugs**: Fixed `import re` missing in `dispatch.py` (critical)
- **Bugs**: Created missing `clients/r1/menu.json` for Ce-Son bot
- **Bugs**: Created missing `apps/whatsapp/responders/__init__.py`
- **Bugs**: Fixed session persistence in `r1_bot.py` (save after each step)
- **Bugs**: Fixed confirm intent false positives (`si`, `ok`, `sale`)
- **Bugs**: Fixed double count in `order_store.py` `add_dispatch_event`
- **Bugs**: Fixed price validation against menu in `r1_bot.py`
- **Bugs**: Fixed temp file leak in `responder.py` `_send_voice`
- **Bugs**: Fixed error leakage in `responder.py` `_ask_llm`
- **Bugs**: Added kill switch to `whatsapp_agent.py` (was responding to anyone)
- **Bugs**: Fixed kill switch timing in `whatsapp_agent.py` (check before LLM call)
- **Bugs**: Fixed `ia` substring false positive in `social/responder.py`
- **Bugs**: Added lead deduplication in `social/responder.py`
- **Bugs**: Applied platform context in `social/responder.py` `generate_response`
- **n8n**: Replaced 3 hardcoded Telegram tokens with env vars
- **n8n**: Replaced 3 hardcoded WhatsApp API keys with env vars
- **n8n**: Fixed 6 `127.0.0.1:8000` URLs to `api:8000`
- **n8n**: Deleted 3 duplicate workflows
- **n8n**: Deleted 5 incomplete prototipos

### Changed
- **Architecture**: Documented 6-layer concentric architecture in `docs/BLUEPRINT-LIMPIO.md`
- **Cost Analysis**: Estimated $16.88/mes total ($0.88 LLM + $16 infra)
- **Engram**: Saved 27 memories across 4 layers (business, project, working, historical)

### Known Issues
- 27 test collection errors (import path issues in `tests/unit/`)
- No semantic versioning or git tags (this is the first tag)
- `clients/` contains code that should be in `core/` (RAG engine, chat engine)
- VPS swap 100% full, <200MB free RAM
- 3 Docker images use `:latest` tag
- `.gitignore` missing some patterns (`.db` in state/, `.env.backup`)
