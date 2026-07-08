# HAS-004 — Hermes Architecture Standard: Cognitive Kernel

**Status:** Draft v1
**Domain:** kernel
**Updated:** 2026-07-08
**Depends on:** HAS-000, HAS-001, HAS-002, HAS-003
**Replaces:** `apps/jarvis/src/core/orchestrator.py` (partially)

---

## 1. Purpose

Define the Hermes Cognitive Kernel — the central nervous system of the OS. The Kernel does not know Spotify, PostgreSQL, or any external system. It manages: context, memory, events, policies, agent routing, and reflection.

Hermes is no longer a chatbot. It is a Kernel.

---

## 2. Kernel Architecture

```
                    ┌──────────────────────────────┐
                    │         USER INPUT            │
                    │  (Voice / Web / Telegram /    │
                    │   WhatsApp / API / CLI)       │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │     1. CONTEXT ENGINE         │
                    │   Builds context from input    │
                    │   + memory + constitution      │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │     2. PLANNER                │
                    │   Decomposes mission into     │
                    │   tasks. Selects agent(s).    │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │     3. POLICY ENGINE          │
                    │   Constitution gates:         │
                    │   Policy → Security → Cost    │
                    │   → Compliance → Quality      │
                    └──────────────┬───────────────┘
                                   │
                            ┌──────┴──────┐
                            ▼             ▼
              ┌──────────────────┐  ┌──────────────────┐
              │ 4. AGENT ROUTER  │  │ 4. SKILL ROUTER  │
              │ Routes to the    │  │ Direct skill call │
              │ right agent      │  │ (known task)      │
              └──────┬───────────┘  └──────┬───────────┘
                     │                     │
                     └─────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────────────┐
                    │     5. EXECUTOR               │
                    │   Runs task via agent/skill   │
                    │   Collects result + metrics   │
                    └──────────────┬───────────────┘
                               │
                               ▼
                    ┌──────────────────────────────┐
                    │     6. REFLECTOR              │
                    │   Evaluates result:           │
                    │   - Score quality             │
                    │   - Extract lessons           │
                    │   - Emit events               │
                    │   - Update memory             │
                    └──────────────┬───────────────┘
                               │
                               ▼
                    ┌──────────────────────────────┐
                    │         OUTPUT                │
                    └──────────────────────────────┘
```

---

## 3. Kernel Modules

### 3.1 Context Engine

Builds the working context for every request. Merges:

- **Input context**: raw user message + metadata (channel, tenant, user)
- **Memory context**: relevant memories from all stores
- **Constitution context**: applicable rules from `constitution/`
- **Session context**: conversation history (working memory)

```python
@dataclass
class HermesContext:
    input: str
    channel: str                          # voice | web | telegram | api | cli
    tenant: str                           # tenant_id
    user_id: str
    conversation_id: str
    memories: dict[str, list[dict]]       # grouped by memory type
    constitution_rules: list[dict]        # applicable rules
    working_memory: list[dict]            # current conversation
```

### 3.2 Planner

Decomposes the user's mission into discrete tasks. Each task has:

```python
@dataclass
class KernelTask:
    id: str
    mission: str                          # what user wants
    description: str                      # what to do
    agent: str | None                     # assigned agent (None = planner decides)
    capability: str | None                # capability to use
    depends_on: list[str]                 # task dependencies
    priority: int                         # 0=normal, 1=high, 2=critical
    estimated_cost: float
    policies: dict                        # policy checks to run
```

Planner strategies:
- **Direct**: For known patterns ("sync artists" → skill route)
- **Delegation**: For complex tasks → route to specialist agent
- **Research**: For unknown tasks → route to researcher agent first
- **Emergency**: For critical issues → bypass planning, execute immediately

### 3.3 Policy Engine (Constitution Gates)

Reuses gates from HAS-001. Every task passes through:

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  POLICY  │→│ SECURITY │→│  COST   │→│COMPLIANCE│→│ QUALITY  │
│   GATE   │  │   GATE   │  │   GATE   │  │   GATE   │  │   GATE   │
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
     │              │            │             │             │
     ▼              ▼            ▼             ▼             ▼
   PASS/          PASS/        PASS/         PASS/         PASS/
   FAIL           FAIL         FAIL          FAIL          FAIL
```

If any gate FAILs → task is rejected with explanation + fix suggestion.

### 3.4 Agent Router

Routes tasks to the appropriate agent. Uses capability registry:

```python
class AgentRouter:
    registry: dict[str, AgentInfo]  # agent_id → {capabilities, status, load}

    def route(self, task: KernelTask) -> str:
        """Returns agent_id for this task."""

    def available(self, capability: str) -> list[str]:
        """Returns agents that can handle this capability."""

    def health(self, agent_id: str) -> AgentHealth:
        """Returns load, last_seen, error_rate."""
```

### 3.5 Executor

Executes a task by calling the assigned agent's entry point. Collects:

```python
@dataclass
class ExecutionResult:
    task_id: str
    status: str                           # success | failure | partial
    output: dict
    duration_ms: int
    cost: float
    model_used: str
    events_emitted: list[str]
    error: str | None
```

### 3.6 Reflector

Post-execution analysis. Runs after every task:

```python
class Reflector:
    async def reflect(self, task: KernelTask, result: ExecutionResult):
        # 1. Score the result (0-100)
        score = await self.score(task, result)

        # 2. Extract lessons
        lessons = await self.extract_lessons(task, result)

        # 3. Emit events
        await self.emit_events(task, result, score)

        # 4. Update memory
        await self.update_memory(task, result, lessons)

        # 5. Propose improvements (if score < threshold)
        if score < 60:
            await self.propose_adr(task, result, score)

        return score
```

---

## 4. Kernel as a Process

The Kernel runs as a **long-lived process** (`kernel/main.py`). It:

1. Listens on multiple channels (stdin, WebSocket, Redis Streams, HTTP)
2. Maintains its own working memory
3. Emits events for every operation
4. Self-heals: if a module crashes, restarts it
5. Exposes health endpoint for observability

```python
# kernel/main.py — pseudocode
class HermesKernel:
    def __init__(self):
        self.context = ContextEngine()
        self.planner = Planner()
        self.policy = PolicyEngine()
        self.router = AgentRouter()
        self.executor = Executor()
        self.reflector = Reflector()
        self.running = False

    async def start(self):
        self.running = True
        # Listen on all channels
        await asyncio.gather(
            self.listen_redis(),
            self.listen_websocket(),
            self.listen_http(),
            self.listen_stdin(),
        )

    async def process(self, hermes_context: HermesContext) -> ExecutionResult:
        # 1. Build context
        ctx = await self.context.build(hermes_context)

        # 2. Plan
        tasks = await self.planner.plan(ctx)

        # 3. Execute each task through gates
        results = []
        for task in tasks:
            # Gates
            if not await self.policy.validate(task):
                results.append(ExecutionResult(task_id=task.id, status="rejected"))
                continue

            # Route & Execute
            agent_id = self.router.route(task)
            result = await self.executor.execute(task, agent_id)
            results.append(result)

            # Reflect
            await self.reflector.reflect(task, result)

        return results
```

---

## 5. Migration from Current Code

| Current file | Kernel module | Migration |
|---|---|---|
| `apps/jarvis/main.py` | `kernel/main.py` | Extract orchestration, remove direct provider calls |
| `apps/jarvis/src/core/orchestrator.py` | `kernel/planner.py` + `kernel/router.py` | Split planning from agent management |
| `apps/jarvis/src/core/llm.py` | `kernel/context.py` (LLM is a tool, not kernel) | Move to tool runtime |
| `apps/jarvis/src/core/engram.py` | `memory/stores/long.py` | Wrap in MemoryStore |
| `apps/jarvis/src/core/rag.py` | `memory/stores/semantic.py` | Wrap in MemoryStore |
| `apps/jarvis/src/core/brain_graph.py` | `memory/stores/graph.py` | Wrap in MemoryStore |
| `apps/jarvis/src/core/neo4j_store.py` | `memory/stores/graph.py` | Merge into graph store |
| `apps/jarvis/src/core/pipeline_bridge.py` | `kernel/executor.py` | Move orchestration logic |
| `apps/jarvis/src/core/unified_bridge.py` | `kernel/router.py` | Move routing logic |
| `apps/jarvis/src/core/security_guard.py` | `kernel/policy.py` | Move to policy engine |
| `apps/jarvis/src/core/redis_streams.py` | `memory/stores/working.py` + `kernel/listener.py` | Split |
| `apps/jarvis/src/core/verify.py` | `kernel/reflector.py` | Move scoring/reflection |
| `apps/jarvis/src/core/agents_v2/agent_base_v2.py` | `kernel/agent_registry.py` | Agent registry contract |
| `scripts/verify-gate.py` | `kernel/policy.py` | Constitution gates |

---

## 6. Directory Structure After Migration

```
kernel/
├── __init__.py
├── main.py                    # HermesKernel entry point
├── context.py                 # ContextEngine
├── planner.py                 # Planner
├── policy.py                  # PolicyEngine (constitution gates)
├── router.py                  # AgentRouter
├── executor.py                # Executor
├── reflector.py               # Reflector
├── models.py                  # KernelTask, HermesContext, ExecutionResult
├── listeners/
│   ├── __init__.py
│   ├── redis.py               # Redis Stream listener
│   ├── websocket.py           # WebSocket listener
│   ├── http.py                # HTTP listener
│   └── stdin.py               # CLI/stdin listener
└── tests/
    ├── test_context.py
    ├── test_planner.py
    ├── test_policy.py
    ├── test_router.py
    ├── test_executor.py
    └── test_reflector.py
```

The old `apps/jarvis/` files remain during migration, with a deprecation notice:

```python
# apps/jarvis/src/core/orchestrator.py
import warnings
warnings.warn(
    "orchestrator.py is deprecated. Use kernel/ modules (HAS-004).",
    DeprecationWarning, stacklevel=2
)
```

---

## 7. Kernel Events

The Kernel emits these events (HAS-003 schema):

| Event | Trigger | Payload highlights |
|---|---|---|
| `kernel.context.built` | Context created for request | `{ input_length, memories_loaded, rules_applied }` |
| `kernel.task.planned` | Task decomposed | `{ task_count, agents_selected }` |
| `kernel.gate.passed` | Gate passed | `{ gate, task_id }` |
| `kernel.gate.failed` | Gate failed | `{ gate, task_id, rule, fix }` |
| `kernel.task.executed` | Task completed | `{ task_id, agent, duration_ms, cost, status }` |
| `kernel.reflection.completed` | Reflection done | `{ task_id, score, lessons_count, adr_proposed }` |
| `kernel.error` | Kernel-level error | `{ module, error, severity }` |

---

## 8. Success Criteria

- [ ] `kernel/main.py` starts as a standalone process
- [ ] All 6 modules (context, planner, policy, router, executor, reflector) implemented
- [ ] Constitution gates validate every task before execution
- [ ] No direct API calls from Kernel (all via tools/drivers)
- [ ] Old `apps/jarvis/src/core/` files have deprecation warnings
- [ ] All event types emitted in HAS-003 schema
- [ ] Health endpoint responds on known port
- [ ] All existing tests pass after migration
- [ ] Agents_v2 continue working through router
