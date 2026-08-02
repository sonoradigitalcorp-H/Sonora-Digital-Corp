# HAS-005 — Hermes Architecture Standard: Capability Bus

**Status:** Draft v1
**Domain:** capabilities
**Updated:** 2026-07-08
**Depends on:** HAS-000, HAS-004
**Replaces:** concept of "modules" — system is now organized by capabilities

---

## 1. Purpose

Define the structure, lifecycle, and contracts for Capabilities. A Capability is a business-aligned unit of functionality — the system does what it can do, not what modules it has.

The Capability Bus is the registry where all capabilities live, and the router that connects agents to capabilities.

---

## 2. What is a Capability?

A capability is NOT a module. It is a **capacity** the system has. Each capability contains everything needed to perform a business function:

```
capability/
├── capability.yaml          # Manifest: id, name, description, version
├── agent.py / agent.yaml    # Agent(s) that fulfill this capability
├── workflow.yaml           # Steps to execute
├── prompts/                # Prompts for the agent
│   ├── system.md
│   └── user.md
├── skills/                 # Concrete executors
│   ├── skill_a.py
│   └── skill_b.py
├── memory/                 # Memory config for this capability
│   ├── working.yaml
│   └── semantic.yaml
├── policies.yaml           # Cost limits, allowed models, security rules
├── events.yaml             # Events this capability emits
├── tests/
│   ├── test_capability.py
│   └── test_workflow.py
└── README.md               # Human-readable docs
```

### Manifest (`capability.yaml`):

```yaml
id: generate-video
name: Generate Video
version: 1.0.0
domain: music
description: "Generate talking head or lipsync videos from audio + image"
entry:
  agent: video-agent
  trigger: video.generate
dependencies:
  - skill: fal-ai
  - skill: ffmpeg
  - memory: working
  - memory: semantic
policies:
  max_cost: 0.50
  allowed_models: ["fal-ai/sync-lipsync"]
  timeout_seconds: 120
events:
  emits: ["video.generated", "video.failed"]
  consumes: ["track.published", "campaign.created"]
```

---

## 3. Capability Types

| Type | Description | Example | Agent Needed |
|---|---|---|---|
| **Core** | System capability — always available | `search-knowledge`, `memory-store` | No (direct skill) |
| **Business** | Domain-specific business function | `generate-video`, `analyze-artist`, `publish-track` | Yes |
| **Integration** | External system bridge | `spotify-sync`, `youtube-upload`, `stripe-payment` | Yes |
| **Cognitive** | AI reasoning capability | `research-topic`, `draft-contract`, `score-artist` | Yes |
| **Automation** | Workflow trigger | `daily-sync`, `alert-on-error`, `backup-db` | No (cron) |

---

## 4. Capability Registry

All capabilities are registered in `capabilities/index.yaml`:

```yaml
capabilities:
  - id: generate-video
    path: capabilities/generate-video/
    type: business
    domain: music
    version: 1.0.0
    status: active          # active | deprecated | experimental
    agent: video-agent
    cost_tier: 2            # 1=cheap, 5=expensive

  - id: analyze-artist
    path: capabilities/analyze-artist/
    type: cognitive
    domain: music
    version: 1.0.0
    status: active
    agent: research-agent
    cost_tier: 3

  - id: publish-track
    path: capabilities/publish-track/
    type: business
    domain: music
    version: 0.5.0
    status: experimental
    agent: marketing-agent
    cost_tier: 1

  - id: search-knowledge
    path: capabilities/search-knowledge/
    type: core
    domain: system
    version: 1.0.0
    status: active
    agent: null              # direct skill
    cost_tier: 1
```

---

## 5. Capability Lifecycle

```
EXPERIMENTAL ──> ACTIVE ──> DEPRECATED ──> REMOVED
     │              │            │
     │         ┌────┴────┐      │
     │         │         │      │
     ▼         ▼         ▼      ▼
  Test in     Used in   No new   Code
  dev only    prod      users    deleted
```

- **Experimental**: New capability, may change without notice. Not in prod routing.
- **Active**: Fully supported. All policies enforced. Cost tracked.
- **Deprecated**: Still works but no new development. Produces deprecation events.
- **Removed**: Code deleted. Only historical events remain.

Transition requires ADR (Architecture Decision Record).

---

## 6. Capability Bus (Runtime)

The Capability Bus is the runtime that connects agents to capabilities. It is part of the Kernel (HAS-004):

```python
class CapabilityBus:
    def __init__(self, registry_path: str = "capabilities/index.yaml"):
        self.registry = self._load_registry(registry_path)
        self.cache: dict[str, Capability] = {}

    async def resolve(self, capability_id: str) -> Capability:
        """Load a capability by ID (cached)."""
        if capability_id not in self.cache:
            manifest = self.registry[capability_id]
            self.cache[capability_id] = Capability(manifest)
        return self.cache[capability_id]

    async def execute(self, capability_id: str, context: HermesContext) -> ExecutionResult:
        """Execute a capability with given context."""
        cap = await self.resolve(capability_id)

        # 1. Policy check
        gates = await PolicyEngine.validate(cap.policies, context)
        if not gates.passed:
            return ExecutionResult(status="rejected", gates=gates)

        # 2. Load agent (if needed)
        agent = None
        if cap.manifest.agent:
            agent = await AgentRouter.resolve(cap.manifest.agent)

        # 3. Execute workflow
        result = await WorkflowEngine.execute(cap.workflow, context, agent)

        # 4. Emit events
        for event_type in cap.manifest.events.emits:
            await EventBus.emit(event_type, result)

        return result

    def discover(self, query: str | None = None) -> list[CapabilityManifest]:
        """List all capabilities matching query."""
        if not query:
            return list(self.registry.values())
        return [
            c for c in self.registry.values()
            if query.lower() in c.name.lower() or query.lower() in c.id.lower()
        ]

    def health(self, capability_id: str) -> CapabilityHealth:
        """Health metrics for a capability."""
        cap = self.cache.get(capability_id)
        if not cap:
            return CapabilityHealth(status="unknown")
        return CapabilityHealth(
            status=cap.manifest.status,
            last_execution=cap.last_execution,
            error_rate=cap.error_rate,
            avg_latency_ms=cap.avg_latency_ms,
        )
```

---

## 7. First Capabilities (ABE Music)

These are the capabilities we extract from existing code first:

| Capability | Extracted From | Priority |
|---|---|---|
| `sync-artist-data` | `collectors/` + `scrapers/` | P0 — daily sync |
| `analyze-artist` | `apps/jarvis/src/core/abe_music.py` + SIGNAL | P0 — ABE dashboard |
| `generate-video` | `clon-digital/orchestrator/` + `fal-wrapper/` | P1 — clon-digital |
| `publish-track` | `apps/jarvis/src/core/sales_pipeline.py` | P1 — distribution |
| `search-knowledge` | `apps/jarvis/src/core/rag.py` | P0 — all agents need this |
| `score-artist` | SIGNAL score engine | P1 — ABE analytics |
| `manage-crm` | `apps/jarvis/src/core/sdc_business.py` | P2 — ABE relationships |
| `process-payment` | `mystika/api/services/` | P2 — monetization |

### Migration Path

Each capability is extracted one at a time:

```
1. Create capabilities/<id>/ directory
2. Move relevant code into skills/ subdirectory
3. Write capability.yaml manifest
4. Write prompts/ for the agent
5. Register in capabilities/index.yaml
6. Update Kernel router to know about it
7. Old code path still works (deprecation warning)
8. After 1 month, remove old code
```

---

## 8. Workflow Engine

Each capability has a workflow. Workflows are sequences of steps, not DAGs:

```yaml
# capabilities/sync-artist-data/workflow.yaml
id: sync-artist-data
version: 1
steps:
  - id: fetch-spotify
    skill: spotify-skill
    action: fetch_artist
    params:
      artist_id: "${input.artist_id}"
    timeout: 30s

  - id: fetch-youtube
    skill: youtube-skill
    action: fetch_stats
    params:
      artist_id: "${input.artist_id}"
    timeout: 30s

  - id: merge-data
    skill: data-skill
    action: merge
    params:
      sources: ["${steps.fetch-spotify.result}", "${steps.fetch-youtube.result}"]
    depends_on: ["fetch-spotify", "fetch-youtube"]

  - id: store-results
    skill: memory-skill
    action: store
    params:
      data: "${steps.merge-data.result}"
      memory_type: business
    depends_on: ["merge-data"]

  - id: emit-event
    skill: event-skill
    action: emit
    params:
      type: "artist.data_sync.completed"
      payload: "${steps.store-results.result}"
    depends_on: ["store-results"]
```

Steps run in parallel where possible (no `depends_on` = parallel).

---

## 9. Capability Discovery

Agents discover capabilities through the Kernel:

```python
# Agent asks Kernel:
capabilities = await kernel.discover_capabilities("generate video")
# Returns: [CapabilityManifest(id="generate-video", ...)]

# Agent asks Kernel to execute:
result = await kernel.execute_capability("generate-video", context)
```

This means agents never import capabilities directly. They ask the Kernel.

---

## 10. Events

| Event | Trigger | Payload |
|---|---|---|
| `capability.registered` | New capability added | `{ id, version, type, domain }` |
| `capability.activated` | Status → active | `{ id }` |
| `capability.deprecated` | Status → deprecated | `{ id, reason, replacement }` |
| `capability.executed` | Capability ran | `{ id, duration_ms, cost, status }` |
| `capability.health.changed` | Health status changed | `{ id, error_rate, avg_latency }` |

---

## 11. Directory Structure After Migration

```
capabilities/
├── index.yaml                       # Global registry
├── sync-artist-data/
│   ├── capability.yaml
│   ├── workflow.yaml
│   ├── prompts/
│   ├── skills/
│   ├── policies.yaml
│   ├── events.yaml
│   └── tests/
├── analyze-artist/
│   ├── capability.yaml
│   ├── workflow.yaml
│   ├── prompts/
│   ├── skills/
│   ├── policies.yaml
│   ├── events.yaml
│   └── tests/
├── generate-video/
│   └── ...
├── publish-track/
│   └── ...
├── search-knowledge/
│   └── ...
└── bus.py                           # CapabilityBus runtime
```

---

## 12. Success Criteria

- [ ] `capabilities/index.yaml` exists with first 4 capabilities registered
- [ ] `CapabilityBus` resolves and executes capabilities
- [ ] Agents discover capabilities through Kernel (not direct import)
- [ ] Workflow engine runs steps in parallel where possible
- [ ] Each capability has its own policies, prompts, skills, and tests
- [ ] Old code paths emit deprecation warnings
- [ ] All existing tests pass after migration
- [ ] `capability.executed` event emitted for every execution
- [ ] Health endpoint reports per-capability metrics
