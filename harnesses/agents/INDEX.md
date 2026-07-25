# Agent Harnesses — Sonora Digital Corp

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Generated**: 2026-07-23

---

## Agent Registry

| # | Agent | Status | License | Path | Description |
|---|-------|--------|---------|------|-------------|
| 1 | **Voice Agent** (Mystic) | 🟢 Live | $149/mo | `harnesses/agents/HARNESS-VOICE-001.md` | Asistente telefónico IA 24/7 — STT → Intent Router → LLM → TTS → Soundscape |
| 2 | **CRM Agent** (Sales Pipeline) | 🟢 Live | $99/mo | `harnesses/agents/HARNESS-CRM-001.md` | Pipeline de ventas inteligente — Neo4j, scoring, propuestas, gamificación |
| 3 | **X Agent** (Social Media) | 🔴 Coming Soon | $79/mo | `harnesses/agents/HARNESS-X-001.md` | Automatización de redes sociales — tendencias, contenido, scheduling, analytics |

---

## Quick Start

### Voice Agent

```bash
cd ~/sdc
pip install -r apps/voice-realtime/requirements.txt
export VOICE_PORT=8900
python apps/voice-realtime/server.py
# Open http://127.0.0.1:8900
```

### CRM Agent

```bash
cd ~/sdc
docker compose -f infra/docker-compose.yml up -d sdc-neo4j
python scripts/crm.py contacts
# Web UI at http://127.0.0.1:5174/api/sales/dashboard
```

### X Agent

> **Coming Soon** — No code exists yet. See `harnesses/agents/HARNESS-X-001.md` for implementation roadmap.

---

## Pricing Summary

| Agent | Starter | Professional | Enterprise |
|-------|---------|-------------|------------|
| Voice Agent | $149/mo (1k sessions, 1 tenant) | $499/mo (5k sessions, 5 tenants) | $1,499/mo (unlimited, white-label) |
| CRM Agent | $99/mo (500 leads, 1 tenant) | $299/mo (2.5k leads, 5 tenants) | $999/mo (unlimited, white-label) |
| X Agent | $79/mo (1 platform, 30 posts) | $249/mo (3 platforms, 150 posts) | $799/mo (unlimited, white-label) |

---

## Architecture Overview

```
                    ┌──────────────────┐
                    │   MCP Gateway    │
                    │   (127.0.0.1)    │
                    │   :18989         │
                    └────┬──────┬──────┘
              ┌──────────┘      └──────────┐
              ▼                             ▼
    ┌──────────────────┐         ┌──────────────────┐
    │   Voice Agent    │         │   CRM Agent      │
    │   (port 8900)    │         │   (port 5174)    │
    │   WebSocket      │         │   REST API       │
    │   PCM16 / JSON   │         │   Neo4j Graph    │
    └──────────────────┘         └──────────────────┘

    ┌──────────────────┐
    │   X Agent        │ ◄── Coming Soon
    │   (port 9100)    │
    │   Social APIs    │
    └──────────────────┘
```

## Shared Infrastructure

```
All agents share:
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Engram   │  │ Neo4j    │  │ Qdrant   │  │ Redis    │
│ (memory) │  │ (graph)  │  │ (vector) │  │ (cache)  │
└──────────┘  └──────────┘  └──────────┘  └──────────┘

┌──────────┐  ┌──────────┐  ┌───────────────┐
│ Events   │  │ LLM      │  │ MCP Gateway   │
│ JSONL    │  │ DeepSeek │  │ (unified bus) │
└──────────┘  └──────────┘  └───────────────┘
```

## Compliance

All harnesses comply with:

- **OMEGA PROMPT v10.0** — Enterprise Operating Constitution
- **SOUL.md** — 5 Elements (Foundation, Knowledge, Action, Flow, Connection)
- **10-RULES.md** — Spec first, tests green, humans decide, etc.
- **AGENT-HARNESS-TEMPLATE.md** — 12 fields required
- **Decision Hierarchy**: VDD → EDD → PDD → ODD → SDD → BDD → TDD

---

## Agent Harness Lifecycle

```
1. User requests new agent capability
2. Spec written → Scored → Approved
3. Harness created (this format)
4. Implementation via SDD pipeline
5. Tests pass → Code merged
6. Status updated to "Live"
7. Lessons learned → Lección document
```

---

## See Also

- `skills/harnesses/AGENT-HARNESS-TEMPLATE.md` — Template used for all harnesses
- `skills/harnesses/agent-harness.md` — Agent Lifecycle Harness reference
- `agents/MANIFEST.md` — Agent registry with autonomy levels
- `process/active/` — Active specs for in-progress agents
- `constitution/10-RULES.md` — Absolute rules for all development
