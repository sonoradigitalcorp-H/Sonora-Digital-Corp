# HAS-003 — Hermes Architecture Standard: Event Mesh

**Status:** Draft v1
**Domain:** events
**Updated:** 2026-07-08
**Depends on:** HAS-000

---

## 1. Purpose

Define the event contract for the entire system. Nothing calls functions directly — everything publishes events. This decouples every component and enables the Event Mesh as the nervous system of the OS.

---

## 2. Event Schema

Every event in the system follows this exact schema:

```json
{
  "id": "evt_<ulid>",
  "type": "<domain>.<action>.<status>",
  "version": 1,
  "timestamp": "2026-07-08T19:00:00Z",
  "source": "<agent_or_service_name>",
  "tenant": "<tenant_id>",
  "correlation_id": "<uuid>",
  "causation_id": "<parent_event_id>",
  "subject": {
    "type": "artist | track | campaign | video | user | system",
    "id": "<entity_id>"
  },
  "payload": {},
  "metadata": {
    "cost": 0.0,
    "latency_ms": 0,
    "model": "ollama/qwen3:4b-64k",
    "agent": "planner"
  }
}
```

### Field requirements

| Field | Required | Description |
|---|---|---|
| `id` | Always | ULID-based unique ID |
| `type` | Always | `domain.action.status` e.g. `artist.data_sync.completed` |
| `version` | Always | Schema version (integer, starts at 1) |
| `timestamp` | Always | ISO8601 UTC |
| `source` | Always | Who produced this event |
| `tenant` | Always | Multi-tenant isolation |
| `correlation_id` | Always | Traces a request across all services |
| `causation_id` | Optional | Links to the event that caused this one |
| `subject` | Always | What entity this event is about |
| `payload` | Always | Domain-specific data (can be empty `{}`) |
| `metadata` | Always | Observability data |

---

## 3. Event Registry

All event types are documented in `state/events/catalog.yaml`:

```yaml
events:
  - type: artist.data_sync.completed
    version: 1
    description: "Artist data has been synced from all providers"
    subject_type: artist
    payload:
      artists_synced:
        type: array
        items:
          artist_id: string
          updated: boolean
          delta: object
    emitted_by: [collector, sync-cron]
    destinations: [abe-service, analytics, memory]

  - type: track.published
    version: 1
    description: "A track has been published to distribution platforms"
    subject_type: track
    payload:
      track_id: string
      title: string
      artist_id: string
      platforms: string[]
    emitted_by: [publish-capability]
    destinations: [crm, analytics, revenue]

  - type: video.generated
    version: 1
    description: "A video has been generated"
    subject_type: video
    payload:
      video_id: string
      type: "talking_head | lipsync | short | lyric"
      duration_seconds: int
      cost: float
    emitted_by: [video-agent, fal-wrapper]
    destinations: [messaging, crm, storage]

  - type: revenue.updated
    version: 1
    description: "Revenue data has been updated"
    subject_type: artist
    payload:
      artist_id: string
      period: string
      amount: float
      platform: string
    emitted_by: [revenue-pipeline]
    destinations: [finance, crm, dashboard]

  - type: campaign.created
    version: 1
    description: "A marketing campaign has been created"
    subject_type: campaign
    emitted_by: [marketing-agent]
    destinations: [analytics, finance, crm]

  - type: agent.action.executed
    version: 1
    description: "An agent completed an action"
    subject_type: system
    payload:
      agent: string
      action: string
      duration_ms: int
      cost: float
      success: boolean
    emitted_by: [all_agents]
    destinations: [observability, evolution, cost]

  - type: system.error.occurred
    version: 1
    description: "A system error occurred"
    subject_type: system
    payload:
      source: string
      error: string
      stack: string
      severity: "warning | error | critical"
    emitted_by: [all_services]
    destinations: [observability, alerts, evolution]

  - type: constitution.gate.violation
    version: 1
    description: "A constitution gate was violated"
    subject_type: system
    payload:
      gate: string
      rule: string
      agent: string
      action: string
      severity: string
    emitted_by: [constitution-engine]
    destinations: [alerts, audit, evolution]

  - type: evolution.adr.proposed
    version: 1
    description: "The Evolution Engine proposes an ADR"
    subject_type: system
    payload:
      adr_id: string
      title: string
      reason: string
      score: int
    emitted_by: [evolution-engine]
    destinations: [notifications, process]
```

---

## 4. Event Producers & Consumers

```
PRODUCERS                              CONSUMERS
──────────                             ──────────
Collectors ──► artist.data_sync        ├── ABE Service (dashboard update)
Agents     ──► agent.action.executed   ├── CRM (lead tracking)
Skills     ──► video.generated         ├── Analytics (trend detection)
Kernel     ──► constitution.gate.*     ├── Memory (long-term storage)
Evolution  ──► evolution.adr.proposed  ├── Evolution Engine (learning)
Git hooks  ──► git.commit              ├── Observability (metrics, cost)
                                        ├── n8n (workflows)
                                        └── Telegram (alerts)
```

---

## 5. Current Implementation → HAS Contract

| Current | HAS contract | Migration |
|---|---|---|
| `scripts/emit-event.py` | Standardized event producer | Update to new schema |
| `state/events/catalog.yaml` | Formalized in HAS-003 | Update format |
| `state/events/events.jsonl` | Event log (append-only) | Keep as-is |
| Memory events in `memory/learning/` | Emit via Event Bus instead | Migrate to events.jsonl |
| n8n webhooks | Consume from Event Bus | Keep as-is (already event-driven) |

---

## 6. Producer Script

`scripts/emit-event.py` is updated to enforce the schema:

```bash
python3 scripts/emit-event.py \
  --type "artist.data_sync.completed" \
  --source "collector" \
  --tenant "abe-music" \
  --subject-type "artist" \
  --subject-id "6727f51e" \
  --payload '{"artists_synced": 7}' \
  --correlation-id "$(uuidgen)"
```

This validates against `state/events/catalog.yaml` before emitting.

---

## 7. Directory Structure

```
state/events/
├── catalog.yaml          # Schema registry (all event types)
├── events.jsonl          # Append-only event log
├── producers.yaml        # Who produces what
└── consumers.yaml        # Who consumes what
```

---

## 8. Success Criteria

- [ ] Every event follows the HAS schema
- [ ] `state/events/catalog.yaml` updated with all event types
- [ ] `scripts/emit-event.py` validates against catalog before emitting
- [ ] Events.jsonl is the single append-only log
- [ ] No more ad-hoc event files (`memory/learning/events.jsonl` migrated)
- [ ] All existing consumers continue working
- [ ] Correlation IDs trace requests across all services
