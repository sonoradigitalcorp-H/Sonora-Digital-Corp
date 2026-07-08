# capture-knowledge — Knowledge Capture & Storage

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-CK-001

---

## 1. Business Objective

Capture all decisions, lessons, and artifacts into persistent memory so no knowledge is ever lost.

## 2. Inputs (Gherkin)

```gherkin
Given content to be stored (decision, lesson, artifact, event summary)
When source is identified (chat, code, decision, external)
And content passes validation (non-empty, has source, has timestamp)
```

## 3. Outputs (Gherkin)

```gherkin
Then knowledge stored in Engram DB
And knowledge indexed in Vector DB (if available)
And knowledge node created in Knowledge Graph (if available)
And knowledge_stored event fires with asset_id
```

## 4. Events

```
Events:
- knowledge_stored: fired when content is successfully stored
- knowledge_indexed: fired when vector index completes
```

## 5. Dependencies

```
Dependencies:
- Engram DB: state/engram.db (always available)
- Vector DB (optional): Qdrant at localhost:6333
- Knowledge Graph (optional): Neo4j at localhost:7687
```

## 6. Tools

```
Tools:
- sqlite3: for Engram DB storage
- httpx/curl: for optional Qdrant indexing
- json: for serialization
```

## 7. Policies

```
Policies:
- Every stored item must have a source attribute
- Every stored item must have a timestamp
- No sensitive data (secrets, keys) may be stored
- Content must be tagged with at least one category
- Store to Engram first (always available), then async to Qdrant
```

## 8. Success Metrics

```gherkin
Success Metrics:
- storage_time: Given content When stored Then milliseconds elapsed
  Target: < 500ms
- storage_success_rate: Given attempts in period When succeeded Then rate
  Target: > 99%
- retrieval_latency: Given query When retrieved Then milliseconds
  Target: < 200ms
```

## 9. Failure Conditions

```
Failure Conditions:
- Engram DB locked: concurrent write conflict (retry up to 3x)
- Engram DB corrupt: database integrity error (rebuild from backup)
- Vector DB unavailable: log warning, continue with Engram only
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If Engram write fails → retry after 100ms, up to 3 times
2. If all retries fail → write to fallback file state/knowledge-fallback.jsonl
3. If Qdrant unavailable → skip vector index, flag for later sync
4. Report failure in state/logs/skills/capture-knowledge.log
```

## 11. Business Value

```
Business Value: Zero knowledge loss. All decisions recoverable. Founder dependency reduced by eliminating need to remember.
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
- Events: knowledge_stored
- Logs: state/logs/skills/capture-knowledge.log
```
