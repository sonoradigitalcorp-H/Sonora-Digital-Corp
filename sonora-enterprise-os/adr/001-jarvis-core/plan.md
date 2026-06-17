# Implementation Plan: JARVIS Core Agent Platform

**Branch**: `001-jarvis-core` | **Date**: 2026-06-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-jarvis-core/spec.md`

## Summary

JARVIS is a multi-agent AI platform with 15 specialized agents, dual-memory (Neo4j graph + Qdrant vector), MCP tool ecosystem, and Hermes/OpenClaw bridges. All deterministic logic (orchestration, routing, validation) is Python puro; LLM is used only for generation. Everything runs local-first with Docker isolation.

## Technical Context

**Language/Version**: Python 3.11+, Next.js 16 (web UI)

**Primary Dependencies**: FastAPI, Neo4j Python driver, Qdrant client, opencode-go (LLM), Hermes MCP client, Docker, systemd

**Storage**: Neo4j (graph memory), Qdrant (vector embeddings), SQLite/JSON (sessions fallback)

**Testing**: pytest with mocked LLM, Docker Compose for integration tests, coverage >= 80%

**Target Platform**: Linux (Ubuntu 22.04+) local machine, Docker for services

**Project Type**: Multi-agent system with REST API + MCP server + Web UI

**Performance Goals**: Orchestration < 200ms, Neo4j queries < 100ms, Qdrant < 50ms, LLM response < 5s

**Constraints**: Local-first (no cloud dependency for core operations), single-user v1, all secrets in env vars

**Scale/Scope**: 15 agents, 10+ MCP tools, < 1M graph nodes, < 100K vectors, 1 user

## Constitution Check

*GATE: Must pass before implementation.*

| Principle | Compliance | Status |
|-----------|-----------|--------|
| **I. Separación de Responsabilidades** | Orchestrator is pure Python deterministic; LLM only generates responses from processed data. All tools validated before LLM sees results. | ✅ PASS |
| **II. Privacidad y Control Local** | All services run locally (Docker). LLM via opencode-go (configurable endpoint). No telemetry. Secrets in env vars. | ✅ PASS |
| **III. Arquitectura Modular** | Each agent is independent module. MCP for tool isolation. Docker for service isolation. Systemd for lifecycle. | ✅ PASS |
| **IV. Calidad y Testing** | pytest with mocked LLM. Coverage >= 80% on deterministic code. Edge cases for all failure modes. | ✅ PASS |
| **V. Documentación** | Spec-driven (this document). ADRs in specs/. Prompts versioned in prompts/. README updated with each change. | ✅ PASS |

**Result**: PASS. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-jarvis-core/
├── plan.md              # This file
├── spec.md              # Feature specification
├── tasks.md             # Implementation tasks
├── checklists/          # Quality checklists
└── contracts/           # API contracts
```

### Source Code (existing)

```text
jarvis/
├── src/core/            # Deterministic logic
│   ├── orchestrator.py  # AgentOrchestrator (15 agents)
│   ├── llm.py           # LLM client (opencode-go / OpenRouter)
│   ├── neo4j_store.py   # Neo4j persistence
│   ├── brain_graph.py   # Knowledge graph builder
│   ├── engram.py        # Memory promotion system
│   ├── embeddings.py    # Local embeddings (Ollama nomic-embed-text)
│   ├── rag.py           # RAG pipeline (Qdrant + embeddings)
│   ├── tools/           # MCP tool definitions
│   ├── agents/          # 15 specialized agent handlers
│   ├── unified_bridge.py # Hermes + OpenClaw bridge
│   └── security_guard.py # Input validation and sanitization
├── docker/              # Dockerfiles for services
├── webui/               # Next.js web interface
├── main.py              # Entry point
├── docker-compose.yml   # Service orchestration
└── config/              # Configuration files
```

**Structure Decision**: Flat src/core/ with submodules for each concern. Agents are files in agents/ directory, auto-discovered at startup. Tools follow same pattern. This keeps addition of new agents/tools to a single file create + registry entry.

## Complexity Tracking

No violations. Architecture is modular and each component has single responsibility.
