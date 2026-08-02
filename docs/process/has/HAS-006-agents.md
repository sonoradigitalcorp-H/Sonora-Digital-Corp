# HAS-006 — Hermes Architecture Standard: Agent Runtime

**Status:** Draft v1
**Domain:** agents
**Updated:** 2026-07-08
**Depends on:** HAS-000, HAS-004, HAS-005

---

## 1. Purpose

Define the contract, lifecycle, and structure for all agents in the system. Agents are cognitive processes that **reason and delegate** — they do not execute directly. Execution is done by Skills (HAS-005).

---

## 2. Agent Contract

Every agent implements this contract:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

@dataclass
class AgentContext:
    mission: str                          # What the user wants
    tenant: str
    user_id: str
    conversation_id: str
    memories: dict[str, list[dict]]       # From MemoryRouter
    capabilities: list[str]               # Available capabilities from Bus
    constitution: list[dict]              # Applicable rules
    working_memory: list[dict]            # Current conversation

@dataclass
class AgentResult:
    status: str                           # success | failure | needs_human
    output: Any
    reasoning: str                        # Why the agent chose this path
    events_emitted: list[str]
    score: int                            # Self-evaluation 0-100
    lessons: list[str]
    capabilities_used: list[str]

class HermesAgent(ABC):
    @abstractmethod
    async def think(self, context: AgentContext) -> AgentResult:
        """Receive context, reason, return result."""
```

---

## 3. Agent Registry

All agents registered in `agents/index.yaml`:

```yaml
agents:
  - id: planner
    name: Planner Agent
    capabilities: ["planning", "decomposition", "routing"]
    model: ollama/qwen3:4b-64k
    status: active
    tier: 1                              # 1=system, 2=domain, 3=specialist

  - id: researcher
    name: Research Agent
    capabilities: ["research", "analysis", "knowledge-synthesis"]
    model: ollama/qwen3:4b-64k
    status: active
    tier: 2

  - id: architect
    name: Architect Agent
    capabilities: ["architecture", "design", "adr-generation"]
    model: ollama/deepseek-r1:7b-64k
    status: active
    tier: 2

  - id: builder
    name: Builder Agent
    capabilities: ["implementation", "coding", "refactoring"]
    model: ollama/qwen3:4b-64k
    status: active
    tier: 2

  - id: reviewer
    name: Reviewer Agent
    capabilities: ["code-review", "quality-check", "linting"]
    model: ollama/qwen3:1.7b-32k
    status: active
    tier: 3

  - id: collector
    name: Collector Agent
    capabilities: ["data-sync", "artist-tracking", "provider-integration"]
    model: ollama/qwen3:1.7b-32k
    status: active
    tier: 2

  - id: video-agent
    name: Video Agent
    capabilities: ["video-generation", "lipsync", "talking-head"]
    model: ollama/qwen3:4b-64k
    status: experimental
    tier: 3

  - id: sales-agent
    name: Sales Agent
    capabilities: ["crm", "lead-tracking", "outreach"]
    model: ollama/qwen3:4b-64k
    status: experimental
    tier: 3

  - id: marketing-agent
    name: Marketing Agent
    capabilities: ["campaigns", "publishing", "analytics"]
    model: ollama/qwen3:4b-64k
    status: experimental
    tier: 3

  - id: finance-agent
    name: Finance Agent
    capabilities: ["payments", "revenue-tracking", "invoicing"]
    model: ollama/qwen3:1.7b-32k
    status: experimental
    tier: 3

  - id: security-agent
    name: Security Agent
    capabilities: ["audit", "threat-detection", "compliance-check"]
    model: ollama/deepseek-r1:7b-64k
    status: active
    tier: 1

  - id: evolution-engine
    name: Evolution Engine
    capabilities: ["self-improvement", "adr-generation", "refactoring-proposal"]
    model: ollama/deepseek-r1:7b-64k
    status: active
    tier: 1
```

---

## 4. Agent Lifecycle

```
REGISTERED → IDLE → THINKING → EXECUTING → REFLECTING → IDLE
                         │                        │
                         ▼                        ▼
                     FAILED ← → RETRY        LEARNING
```

| State | Description |
|---|---|
| `REGISTERED` | Agent exists in registry but not running |
| `IDLE` | Agent ready, waiting for tasks |
| `THINKING` | Agent building context + reasoning (HAS-004 Context + Planner) |
| `EXECUTING` | Agent delegating to skills / capabilities |
| `REFLECTING` | Agent evaluating result (HAS-004 Reflector) |
| `LEARNING` | Agent extracting lessons, updating memory |
| `FAILED` | Agent encountered unrecoverable error |
| `RETRY` | Agent retrying after recoverable error |

---

## 5. Agent Directory Structure

```
agents/
├── index.yaml                  # Registry of all agents
├── base.py                     # HermesAgent ABC
├── types.py                    # AgentContext, AgentResult
├── runtime.py                  # AgentRuntime (process manager)
├── planner/                    # Agent implementations
│   ├── __init__.py
│   ├── agent.py
│   └── prompts/
├── researcher/
│   ├── __init__.py
│   ├── agent.py
│   └── prompts/
├── architect/
│   ├── __init__.py
│   ├── agent.py
│   └── prompts/
├── builder/
│   ├── __init__.py
│   ├── agent.py
│   └── prompts/
├── collector/
│   ├── __init__.py
│   ├── agent.py
│   └── prompts/
├── security/
│   ├── __init__.py
│   ├── agent.py
│   └── prompts/
├── evolution/
│   ├── __init__.py
│   ├── agent.py
│   └── prompts/
└── tests/
    ├── test_base.py
    ├── test_runtime.py
    └── test_agents.py
```

---

## 6. Agent Runtime

The runtime manages agent lifecycle, health, and resource allocation:

```python
class AgentRuntime:
    def __init__(self):
        self.agents: dict[str, HermesAgent] = {}
        self.registry = self._load_registry()

    async def start(self, agent_id: str) -> bool:
        """Start an agent process."""

    async def stop(self, agent_id: str) -> bool:
        """Gracefully stop an agent."""

    async def health(self, agent_id: str) -> AgentHealth:
        """Return health metrics."""

    async def execute(self, agent_id: str, context: AgentContext) -> AgentResult:
        """Run agent.think() with monitoring."""

    def list_agents(self) -> list[AgentInfo]:
        """List all registered agents with status."""

    def find_by_capability(self, capability: str) -> list[str]:
        """Find agents that have a specific capability."""
```

---

## 7. Migration: agents_v2 → HAS Agents

| Current (agents_v2) | New (agents/) | Action |
|---|---|---|
| `agents_v2/agent_base_v2.py` | `agents/base.py` | Refactor to HermesAgent ABC |
| `agents_v2/hermes_v2.py` | `agents/planner/` | Split into planner + router |
| `agents_v2/research_v2.py` | `agents/researcher/` | Move |
| `agents_v2/review_v2.py` | `agents/reviewer/` | Move |
| `agents_v2/sales_v2.py` | `agents/sales/` | Move |
| `agents_v2/code_v2.py` | `agents/builder/` | Rename + move |
| `agents_v2/memory_v2.py` | `memory/` | Not an agent — move to memory |
| `agents_v2/voice_v2.py` | `capabilities/generate-video/skills/` | Move to skill |
| `agents_v2/gbrain_v2.py` | `memory/stores/graph.py` | Move to memory |
| `agents_v2/skill_v2.py` | `agents/builder/` | Merge into builder |
| `agents_v2/pr_v2.py` | `agents/reviewer/` | Merge into reviewer |
| `agents_v2/openclaw_v2.py` | `deprecated/` | Remove (MCP replaced) |
| `agents_v2/explore_v2.py` | `agents/researcher/` | Merge into researcher |

---

## 8. Events

| Event | Trigger | Payload |
|---|---|---|
| `agent.registered` | Agent added to registry | `{ id, capabilities }` |
| `agent.started` | Agent process started | `{ id }` |
| `agent.stopped` | Agent process stopped | `{ id, reason }` |
| `agent.thinking` | Agent started reasoning | `{ id, mission }` |
| `agent.executed` | Agent completed execution | `{ id, status, duration_ms, cost }` |
| `agent.error` | Agent encountered error | `{ id, error, recoverable }` |
| `agent.health.changed` | Health status changed | `{ id, status, error_rate }` |
