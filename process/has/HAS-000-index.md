# HAS-000 — Hermes Architecture Standard: Index & Glossary

**Status:** Draft v1
**Domain:** meta
**Updated:** 2026-07-08

---

## Purpose

This document is the entry point to the Hermes Architecture Standard (HAS). It defines the vocabulary, structure, and roadmap of the standard. Every other HAS document references this one.

---

## Glossary

| Term | Definition | Example |
|---|---|---|
| **Capability** | A business-aligned unit of functionality. Contains agent, workflow, prompts, skills, memory, policies, tests. A capability is not a module — it is a capacity the system has. | `GenerateVideo`, `AnalyzeArtist`, `PublishTrack` |
| **Kernel** | Hermes Kernel. Does not know Spotify, PostgreSQL, or any external system. Manages context, memory, events, policies, routing, and agent selection. The "brain" of the OS. | `kernel/planner`, `kernel/policy`, `kernel/memory` |
| **Agent** | A cognitive process that reasons and delegates. Agents do not execute — they plan, delegate to Skills, and reflect on results. | `PlannerAgent`, `ArchitectAgent`, `ResearcherAgent` |
| **Skill** | A concrete executor that does one thing well. Skills are called by agents. Skills have no agency — they execute and return. | `SpotifySkill.fetchArtist()`, `FFmpegSkill.renderVideo()` |
| **Tool** | A raw interface to an external system (MCP, REST, gRPC, CLI). Tools implement `discover()` → `authorize()` → `execute()` → `observe()`. | `MCPTool`, `SpotifyDriver`, `PostgreSQLDriver` |
| **Driver** | An adapter between a Tool and a Provider. Drivers normalize external APIs into the Tool contract. | `SpotifyDriver`, `YouTubeDriver`, `FileSystemDriver` |
| **Provider** | An AI model provider. Interchangeable. Agents never call providers directly — they call the Kernel which routes to the appropriate provider. | `Ollama`, `OpenAI`, `Anthropic`, `DeepSeek` |
| **Domain** | A bounded context within the business. Each domain has its own knowledge, agents, skills, events, prompts, tests, UI, and API. Domains are independent. | `music/`, `marketing/`, `finance/`, `crm/` |
| **Memory** | A typed store accessed via a uniform `MemoryStore` interface. The system has multiple memory types, not one RAG. | Working, Semantic, Long, Knowledge Graph, Event |
| **Event** | A structured message published to the Event Mesh. Nothing calls functions directly — everything publishes events. | `TrackUploaded`, `VideoGenerated`, `RevenueUpdated` |
| **Constitution** | A set of YAML files that define the laws of the system. Every action is validated against the Constitution before execution. | `constitution/principles.yaml`, `constitution/security.yaml` |
| **Evolution Engine** | A meta-agent that observes system health, generates ADRs, proposes refactors, and updates prompts automatically. | `evolution/observer`, `evolution/proposer` |
| **Experience Layer** | The user-facing interface. Not "frontend" — it's a set of interaction modes (conversation, canvas, watch, config). | Orb states: Listening, Thinking, Executing, Alert |
| **Orb** | The primary visual representation of Hermes. Changes state based on Kernel context. No pages — just states. | `Orb.listening()`, `Orb.thinking()`, `Orb.executing()` |
| **Policy Gate** | A validation step in the execution pipeline. Every action passes through Policy → Security → Cost → Compliance before execution. | `verify-gate.py` → `constitution/` |

---

## Document Map

```
process/has/
├── HAS-000-index.md           # THIS FILE — index + glossary
├── HAS-001-constitution.md    # Constitution Engine + constitution/ layout
├── HAS-002-memory.md          # Memory contracts + store interfaces
├── HAS-003-events.md          # Event Mesh + schema registry
├── HAS-004-kernel.md          # Hermes Cognitive Kernel
├── HAS-005-capabilities.md    # Capability Bus + capability structure
├── HAS-006-agents.md          # Agent Runtime + lifecycle
├── HAS-007-pipeline.md        # Mission→Evolution pipeline + gates
├── HAS-008-evolution.md       # Evolution Engine
├── HAS-009-experience.md      # Experience Layer + Orb
├── HAS-010-security.md        # Security & Governance
└── HAS-011-multitenancy.md    # Multi-tenancy model
```

---

## Architecture Layers (top to bottom)

```
MISSION LAYER          Mission, Vision, North Star, Business Goals
    ↓
CONSTITUTION LAYER     Laws: principles, security, quality, architecture, etc.
    ↓
COGNITIVE KERNEL       Hermes: planner, policy, memory, context, reflector
    ↓
CAPABILITY BUS         GenerateVideo | AnalyzeArtist | PublishTrack | CRM | ...
    ↓
DOMAIN LAYER           music/ | marketing/ | finance/ | crm/ | legal/ | ...
    ↓
MEMORY SYSTEM          Working | Semantic | Long | Knowledge Graph | Event
    ↓
AGENT RUNTIME          PlannerAgent | ArchitectAgent | ResearcherAgent | ...
    ↓
SKILL RUNTIME          SpotifySkill | FFmpegSkill | YouTubeSkill | ...
    ↓
TOOL RUNTIME           MCP | REST | gRPC | CLI | Filesystem | WebSocket
    ↓
PROVIDER LAYER         Ollama | OpenAI | Anthropic | DeepSeek | OpenRouter
    ↓
EXPERIENCE LAYER       Orb | Voice | Canvas | CLI | API | Dashboard
    ↓
OBSERVABILITY          Logs | Metrics | Traces | AI Eval | Cost | Latency
    ↓
EVOLUTION ENGINE       Learn | Measure | Propose | Refactor | Update
```

---

## Pipeline (Mission → Evolution)

Old pipeline (VDD→TDD) is replaced by:

```
1. MISSION       — Purpose, north star, business goal
2. CONSTITUTION  — Validate against all laws
3. RESEARCH      — Knowledge layer: papers, benchmarks, competitors, RFCs
4. ARCHITECTURE  — ADR, patterns, contracts
5. SIMULATION    — Risk analysis, cost estimation, security review
6. SPECIFICATION — SDD with Gherkin + FRs + Score
7. IMPLEMENTATION— BDD + TDD + Code
8. VERIFICATION  — All gates: truth, security, cost, compliance, quality
9. OBSERVABILITY — Deploy + monitor + trace
10. EVOLUTION    — Score → ADR → Refactor → Update prompts
```

Tiers:
- **Tier 0** (typo/config): bypass to Implementation
- **Tier 1** (quick fix): Research → Implementation → Verification
- **Tier 2** (feature): Architecture → Spec → Implementation → Verification → Observability
- **Tier 3** (capability): Full pipeline Mission → Evolution

---

## Implementation Roadmap

| Phase | HAS Docs | Code Changes | Timeline |
|---|---|---|---|
| 0 | HAS-000, HAS-001 | `truth/` → `constitution/` rename | Immediate |
| 1 | HAS-002, HAS-003 | Memory + Event contracts | Week 1 |
| 2 | HAS-004 | Extract Kernel from existing agents | Week 2-3 |
| 3 | HAS-005, HAS-006 | First capabilities + agent runtime | Week 3-4 |
| 4 | HAS-007 | Pipeline evolution gates | Week 4 |
| 5 | HAS-008 | Evolution Engine MVP | Week 5-6 |
| 6 | HAS-009, HAS-010 | Experience + Security | Week 6-8 |
| 7 | HAS-011 | Multi-tenancy foundation | Week 8 |

---

## Design Principles

1. **Constitution-first**: Every change validates against `constitution/` before execution
2. **Events over functions**: No direct calls — publish events and let subscribers react
3. **Capabilities over modules**: Organize by what the system can do, not by technology
4. **Memory is typed**: Not one RAG — multiple memory stores with a uniform interface
5. **Agents reason, Skills execute**: Agents never touch APIs directly
6. **Drivers isolate externals**: Spotify, YouTube, etc. are drivers — remove without side effects
7. **Orb over pages**: The UI expresses state, not routes
8. **Evolution is built-in**: The system improves itself or it stagnates
9. **10% debt tolerance**: No rewrites — incremental refactor only
