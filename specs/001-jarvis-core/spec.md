# Feature Specification: JARVIS Core Agent Platform

**Feature Branch**: `001-jarvis-core`

**Created**: 2026-06-10

**Status**: Draft

**Input**: JARVIS (Just A Rather Very Intelligent System) is a multi-agent AI platform with persistent memory (Neo4j graph + Qdrant vector), 15 specialized agents, MCP tool ecosystem, and Hermes/OpenClaw orchestration bridges.

## User Scenarios & Testing

### User Story 1 - Multi-agent conversation with memory (Priority: P1)

The user asks JARVIS a question and the orchestrator routes it through the appropriate agents, consulting graph + vector memory for context, and returns a coherent response with full context awareness.

**Why this priority**: Core product. Without agent orchestration + memory, there is no JARVIS.

**Independent Test**: Ask a question that requires cross-agent context (e.g., "what did we discuss about Python projects yesterday?"), verify the orchestrator routes correctly and memory recall works.

**Acceptance Scenarios**:

1. **Given** a user message, **When** the orchestrator receives it, **Then** it routes to the correct agent(s) based on intent classification.
2. **Given** prior conversation context in Neo4j, **When** the user asks a follow-up, **Then** JARVIS recalls the context without re-prompting.
3. **Given** a semantic query, **When** vector search is needed, **Then** Qdrant returns relevant embeddings and the response incorporates them.
4. **Given** all 15 agents registered, **When** a message arrives, **Then** the orchestrator selects the right agent or agent chain deterministically.

---

### User Story 2 - Memory persistence with graph + vectors (Priority: P1)

The user stores and retrieves information across sessions. JARVIS builds a knowledge graph connecting entities and enables semantic search.

**Why this priority**: Memory is the differentiator. Without Neo4j + Qdrant, JARVIS is just a chatbot.

**Independent Test**: Store facts ("my name is Alice, I work at Acme"), then query via graph traversal ("who works at Acme?") and via semantic search ("tell me about my job").

**Acceptance Scenarios**:

1. **Given** a fact stored in Neo4j, **When** the user queries via entity relationship, **Then** the graph returns the correct connected nodes.
2. **Given** embeddings stored in Qdrant, **When** the user makes a semantically similar query, **Then** the vector search returns relevant results even without keyword matches.
3. **Given** Neo4j is unavailable, **When** the user stores or retrieves a memory, **Then** the system falls back to in-memory storage without crashing.
4. **Given** the engram system, **When** information importance exceeds a threshold, **Then** it promotes from short-term to long-term memory automatically.

---

### User Story 3 - Tool execution via MCP (Priority: P2)

The user asks JARVIS to perform actions (browse web, read files, run code, query APIs) and the system executes tools via MCP connectors.

**Why this priority**: Tools make JARVIS useful beyond conversation. Depends on agent orchestration (US1).

**Independent Test**: Ask JARVIS to "check the weather in Tokyo" or "list files in /tmp" — verify the MCP tool is called and the result is returned.

**Acceptance Scenarios**:

1. **Given** a user request that requires a tool, **When** the orchestrator detects the intent, **Then** it invokes the correct MCP tool and returns the result.
2. **Given** an MCP tool failure, **When** the tool errors, **Then** JARVIS reports the error gracefully and suggests alternatives.
3. **Given** multiple tools available, **When** a request could use several, **Then** the orchestrator selects the optimal tool deterministically.
4. **Given** the MCP server is dockerized, **When** it needs restarting, **Then** systemd handles recovery automatically.

---

### User Story 4 - Hermes/OpenClaw bridge integration (Priority: P2)

JARVIS delegates complex tasks to Hermes agent (autonomous research, long-running tasks) and OpenClaw (parallel agent execution).

**Why this priority**: Extends JARVIS beyond single-turn Q&A into autonomous execution. Depends on US1.

**Independent Test**: Ask JARVIS to "research the top 3 AI frameworks for 2026" — verify it delegates to Hermes and returns a synthesized result.

**Acceptance Scenarios**:

1. **Given** a complex research task, **When** the orchestrator determines it needs Hermes, **Then** it delegates and streams results back.
2. **Given** a task that requires parallel execution, **When** OpenClaw is available, **Then** agents execute in parallel and results are merged.
3. **Given** Hermes is busy, **When** a new task arrives, **Then** it queues and reports status.
4. **Given** the bridge connection drops, **When** it reconnects, **Then** pending tasks resume automatically.

---

### Edge Cases

- **All agents fail**: orchestrator must reply with an apology + fallback, not crash
- **Neo4j connection lost mid-session**: must transparently switch to Qdrant-only or memory fallback
- **Qdrant collection missing**: auto-create on first write with correct vector dimensions
- **15 agents registered but no router match**: default to general-purpose agent, log miss
- **MCP tool timeout (>30s)**: cancel and inform user, not hang indefinitely
- **Hermes bridge slow (>2min)**: stream partial progress, allow cancellation
- **Memory store on concurrent writes**: must use locking or transactions to avoid corruption
- **Engram promotion infinite loop**: max promotion depth guard (e.g., 3 levels)

## Requirements

### Functional Requirements

**Agent orchestration**

- **FR-001**: The system MUST maintain a registry of 15+ agents with intent classification rules.
- **FR-002**: The orchestrator MUST route messages deterministically based on intent, not via LLM decision.
- **FR-003**: The orchestrator MUST support chaining multiple agents for complex requests.
- **FR-004**: The orchestrator MUST degrade gracefully when all agents matching an intent are unavailable.

**Memory (Neo4j + Qdrant)**

- **FR-005**: The system MUST persist conversation entities and relationships in Neo4j.
- **FR-006**: The system MUST store and query vector embeddings via Qdrant for semantic search.
- **FR-007**: The memory layer MUST fall back to in-memory storage when Neo4j is unavailable.
- **FR-008**: The engram system MUST automatically promote important information from short-term to long-term memory based on configurable thresholds.

**MCP tools**

- **FR-009**: The system MUST expose tools via MCP protocol (FastMCP server) with at least 10 tool definitions.
- **FR-010**: MCP tools MUST have timeout handling and report errors without crashing the orchestrator.
- **FR-011**: Tools MUST be dockerized for isolation and managed via systemd.

**Bridges**

- **FR-012**: The system MUST integrate with Hermes agent for autonomous task execution.
- **FR-013**: The system MUST integrate with OpenClaw for parallel agent orchestration.
- **FR-014**: Bridges MUST support queuing, status reporting, and automatic reconnection.

**General**

- **FR-015**: All deterministic logic MUST have unit tests with >= 80% coverage.
- **FR-016**: The LLM MUST be mockable in tests and MUST NOT be required for core orchestration.

### Key Entities

- **Agent**: specialized processor with intent matcher, handler, and tool access
- **Orchestrator**: deterministic router that selects agents based on message intent
- **Memory**: dual storage (Neo4j graph + Qdrant vector) with engram promotion
- **Engram**: memory unit with importance score, decay rate, and promotion level
- **Tool**: MCP-exposed function with schema, timeout, and error handling
- **Bridge**: connector to external agent systems (Hermes, OpenClaw)
- **Session**: conversation unit with message history and metadata

## Success Criteria

### Measurable Outcomes

- **SC-001**: Orchestrator routes to correct agent with >= 95% accuracy on known intents.
- **SC-002**: Memory recall retrieves stored facts from Neo4j in < 200ms (local).
- **SC-003**: Vector search in Qdrant returns relevant results in < 100ms.
- **SC-004**: System recovers from Neo4j outage without data loss or user-facing error.
- **SC-005**: MCP tool execution completes within configurable timeout in 100% of cases.
- **SC-006**: Bridge integration maintains < 5s overhead for Hermes delegation.
- **SC-007**: All 15 agents are registered and routable at startup.
- **SC-008**: Deterministic logic test coverage >= 80%.

## Assumptions

- **Local first**: all services run on local machine (Docker or bare metal); cloud is optional
- **Single user**: no authentication or multi-tenancy in v1
- **LLM via opencode-go**: cloud model (DeepSeek) for generation; local embedding model for vectors
- **Neo4j community edition**: sufficient for single-user graph operations
- **Memory scale**: < 1M nodes and < 100K vectors in Qdrant; beyond requires scaling review
- **MCP scope**: tools are predefined and statically registered; dynamic tool loading is v2
- **Hermes bridge**: assumes Hermes agent available via MCP or REST; graceful degradation if not
