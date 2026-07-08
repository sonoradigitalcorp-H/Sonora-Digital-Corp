# Knowledge Harness — Enterprise Memory Agent

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: HARNESS-KNW-001

---

## 1. Mission

Capture every decision, lesson, and artifact into persistent memory so the enterprise never forgets.

## 2. Capabilities

```
Capabilities:
- Knowledge Capture: Store decisions and lessons from all OS
  Events: knowledge_stored, lesson_learned
- Vector Indexing: Index knowledge for semantic search in Qdrant
  Events: knowledge_indexed
- Knowledge Graph: Link related knowledge in Neo4j
  Events: knowledge_linked
- Retroactive Sync: Backfill knowledge from event store periodically
  Events: knowledge_batch_synced
```

## 3. Skills

```
Skills:
- capture-knowledge: Store and index enterprise knowledge
  Source: skills/capture-knowledge.skill.md
```

## 4. Policies

```
Policies:
- Every stored item must have source and timestamp
- No sensitive data (secrets, keys) may be stored
- Engram is primary store (always available), Qdrant is secondary
- Knowledge must be tagged with at least one OS category
- Retroactive sync runs every 6 hours
```

## 5. Memory Scope

```
Memory Scope:
  Read: Layer 4 (Customer), Layer 5 (Business), Layer 6 (Historical), Layer 7 (Eternal)
  Write: Layer 6 (Historical), Layer 7 (Eternal)
```

## 6. Approval Requirements

```
Approval Requirements:
- knowledge deletion: approve
- mass import (> 100 items): notify
- schema change: approve
```

## 7. Failure Modes

```
Failure Modes:
- Engram DB locked: concurrent write conflict (retry 3x)
- Qdrant unavailable: vector DB down (use Engram only, flag)
- Neo4j unavailable: graph DB down (use Engram only, flag)
- Storage full: disk space exhausted (rotate old knowledge, alert)
```

## 8. Recovery Procedures

```
Recovery Procedures:
- Engram locked: retry after 100ms up to 3x, fallback to JSONL
- Qdrant down: continue with Engram, re-index when Qdrant recovers
- Neo4j down: continue with Engram, re-link when Neo4j recovers
- Storage full: archive knowledge older than 1 year, free space
```

## 9. Metrics

```
Metrics:
- storage_time: Given content When stored Then milliseconds
  Target: < 500ms
- storage_success: Given attempts in period When succeeded Then rate
  Target: > 99%
- retrieval_latency: Given query When retrieved Then milliseconds
  Target: < 200ms
- knowledge_coverage: Given decisions in period When captured Then percentage
  Target: > 95%
```

## 10. Tests

```gherkin
Feature: Knowledge Harness
  Scenario: Capture decision
    Given a decision is made by any OS
    When the Knowledge harness captures it
    Then it is stored in Engram DB
    And knowledge_stored event fires

  Scenario: Index in vector DB
    Given knowledge is stored in Engram
    When vector indexing runs
    Then it is indexed in Qdrant
    And knowledge_indexed event fires
```

## 11. Observability

```
Observability:
- Health endpoint: via Web UI status
- Metrics: storage_time, storage_success, retrieval_latency, knowledge_coverage
- Log level: INFO
- Log location: state/logs/harnesses/knowledge-harness.log
```

## 12. Dependencies

```
Dependencies:
- capture-knowledge: skill (skills/capture-knowledge.skill.md)
- Engram DB: state/engram.db (primary storage)
- Qdrant: localhost:6333 (vector index)
- Neo4j: localhost:7687 (knowledge graph)
```

---

## Validation Checklist

- [x] Mission is one sentence, measurable
- [x] All capabilities map to events
- [x] All skills reference existing skill definitions
- [x] All policies are enforceable
- [x] Memory scope is defined for read and write
- [x] Approval requirements cover all critical actions
- [x] All failure modes have recovery procedures
- [x] All metrics have Gherkin definitions
- [x] Tests exist and pass
- [x] Observability endpoints are defined
- [x] All dependencies are documented
