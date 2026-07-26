# openclaw-memory — OpenClaw Memory Plugin

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-OCM-001

---

## 1. Business Objective

Store and retrieve memories via the OpenClaw gateway for cross-session knowledge persistence.

## 2. Inputs (Gherkin)

```gherkin
Given OpenClaw gateway is running
When a memory needs to be stored
Or a stored memory needs to be retrieved
Or memories need to be searched by content
```

## 3. Outputs (Gherkin)

```gherkin
Then memory is stored with metadata and timestamp
And retrieved memory is returned with full context
And search results rank by relevance
```

## 4. Events

```
Events:
- openclaw:memory:stored: new memory persisted
- openclaw:memory:retrieved: existing memory accessed
- openclaw:memory:searched: query executed against memory store
```

## 5. Dependencies

```
Dependencies:
- OpenClaw gateway: port 18789
- Memory store: engram or vector database
- Embedding model: text-to-vector conversion
```

## 6. Tools

```
Tools:
- openclaw_execute(memory_*): store, retrieve, search, update memories
```

## 7. Policies

```
Policies:
- All memories must include source and timestamp metadata
- Memories expire per TTL policy (working/project/organization)
- Personal memories must not be accessible across projects
- Memory operations must complete within 2 seconds
```

## 8. Success Metrics

```gherkin
Success Metrics:
- store_latency: Given memory payload When stored Then milliseconds
  Target: < 500 ms
- search_recall: Given query When results returned Then precision@5
  Target: > 0.8
```

## 9. Failure Conditions

```
Failure Conditions:
- Storage full: memory store capacity exhausted (archive old entries)
- Embedding failure: vector generation error (fall back to keyword search)
- Gateway timeout: memory operation exceeds 5s (retry with backoff)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If storage full → trigger archiving of TTL-expired entries, retry store
2. If embedding fails → fall back to keyword/token search
3. If timeout → retry with exponential backoff (3 attempts)
4. Log all attempts to state/logs/skills/openclaw-memory.log
```

## 11. Business Value

```
Business Value: Unified memory access across all OpenClaw plugins for persistent cross-session knowledge.
```

## 12. Parent OS

```
Parent OS: Knowledge
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: openclaw:memory:stored, openclaw:memory:retrieved, openclaw:memory:searched
- Logs: state/logs/skills/openclaw-memory.log
```
