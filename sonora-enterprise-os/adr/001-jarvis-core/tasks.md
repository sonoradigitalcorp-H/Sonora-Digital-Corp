---
description: "Task list for JARVIS Core Agent Platform"
---

# Tasks: JARVIS Core Agent Platform

**Input**: Design documents from `specs/001-jarvis-core/`

**Prerequisites**: plan.md ✅, spec.md ✅

**Organization**: Tasks grouped by user story (priority order from spec.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: User story the task belongs to (US1–US4)
- Exact file paths included

---

## Phase 1: Core Infrastructure (Done)

- [X] T001 Initialize project with Python 3.11+, FastAPI, dependencies (neo4j, qdrant-client, httpx, pydantic)
- [X] T002 Create src/core/ structure with __init__.py and module skeleton
- [X] T003 [P] Implement Neo4j connection manager in src/core/neo4j_store.py (connection pool, retry, fallback)
- [X] T004 [P] Implement Qdrant client in src/core/embeddings.py (collection init, upsert, search)
- [X] T005 [P] Implement engram memory system in src/core/engram.py (importance scoring, promotion, decay)
- [X] T006 [P] Implement brain graph builder in src/core/brain_graph.py (entity extraction, relationship creation)
- [X] T007 [P] Implement RAG pipeline in src/core/rag.py (hybrid graph + vector search)
- [X] T008 [P] Implement LLM client in src/core/llm.py (opencode-go / OpenRouter, streaming, timeout)
- [X] T009 [P] Implement security guard in src/core/security_guard.py (input sanitization, injection prevention)
- [X] T010 [P] Create Docker Compose setup (Neo4j, Qdrant, MCP server, Web UI)

---

## Phase 2: Agent Orchestration (Done)

- [X] T011 Implement AgentOrchestrator in src/core/orchestrator.py (agent registry, intent routing, chaining)
- [X] T012 [P] Register 15 agents in src/core/agents/ (general, memory, code, research, creative, business, music, mysticverse, voice, system, data, security, social, learning, automation)
- [X] T013 [P] Implement tool definitions in src/core/tools/ (web fetch, file ops, code exec, search, memory ops, MCP bridge)
- [X] T014 [P] Implement MCP server in docker/mcp-server/ (FastMCP with 10+ tools)
- [X] T015 [P] Implement Hermes bridge in src/core/unified_bridge.py (task delegation, status, results)
- [X] T016 [P] Implement OpenClaw bridge in src/core/unified_bridge.py (parallel agent execution)
- [X] T017 [P] Create systemd service files for all services (orchestrator, MCP, web UI)

---

## Phase 3: Memory & Context (Done)

- [X] T018 [P] Unit tests for Neo4j store operations in tests/unit/test_neo4j_store.py
- [X] T019 [P] Unit tests for engram promotion logic in tests/unit/test_engram.py
- [X] T020 [P] Unit tests for brain graph building in tests/unit/test_brain_graph.py
- [X] T021 [P] Unit tests for RAG pipeline in tests/unit/test_rag.py
- [X] T022 [P] Integration tests for orchestrator routing in tests/integration/test_orchestrator.py

---

## Phase 4: Polish & Hardening (Needs Work)

- [ ] T023 [P] Add comprehensive error handling for all agent failures (graceful degradation)
- [ ] T024 [P] Add Neo4j connection loss recovery mid-session (transparent switch to fallback)
- [ ] T025 [P] Add MCP tool timeout handling (< 30s cancel with user notification)
- [ ] T026 [P] Add Hermes bridge slow-operation streaming (progress updates for > 2min tasks)
- [ ] T027 [P] Add concurrent write locking for engram storage
- [ ] T028 [P] Add max promotion depth guard for engram (3 levels)
- [ ] T029 [P] Add agent registry miss → default agent fallback with logging
- [ ] T030 [P] Add Qdrant collection auto-creation on first write
- [ ] T031 [P] Increase test coverage to >= 80% on deterministic code
- [ ] T032 Document all agent intents and routing rules
- [ ] T033 [P] Add healthcheck endpoints for all services
- [ ] T034 [P] Add Prometheus metrics for orchestrator, memory, tools

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Core Infrastructure)**: No dependencies — COMPLETE
- **Phase 2 (Agent Orchestration)**: Depends on Phase 1 — COMPLETE
- **Phase 3 (Memory & Context)**: Depends on Phase 2 — COMPLETE
- **Phase 4 (Polish)**: Depends on Phase 3 — IN PROGRESS

### Parallel Opportunities

- All [P] tasks within each phase can run in parallel
- Phase 4 tasks are independent of each other

---

## Implementation Strategy

1. ~~Phase 1: Core Infrastructure~~ ✅ Done
2. ~~Phase 2: Agent Orchestration~~ ✅ Done
3. ~~Phase 3: Memory & Context~~ ✅ Done
4. **Phase 4: Polish & Hardening** ← Current focus
