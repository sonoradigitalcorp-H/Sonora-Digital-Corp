# crm-client — Client Relationship Management

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-CRM-001

---

## 1. Business Objective

Manage client contacts with persistent CRM storage, search across name/phone/company, and automatic sync to Engram/Qdrant/Neo4j/Events for RAG and knowledge graph enrichment.

## 2. Inputs (Gherkin)

```gherkin
Given a contact with name, phone, and company
When the contact is created or updated
Then the contact is stored in CRM SQLite with a unique crm_id
And synced to Engram (layer 3, customer)
And synced to Qdrant (vector index for semantic search)
And synced to Neo4j (graph: Contact → BELONGS_TO → Tenant)
And an event is emitted to events.jsonl

Given a search query with name, phone, or company
When CRM search is executed
Then matching contacts are returned ranked by relevance
```

## 3. Outputs (Gherkin)

```gherkin
Then contact is upserted in CRM SQLite database
And contact data is stored in Engram as key contact:{crm_id}
And contact vector point is created in Qdrant collection kb_{tenant}
And Contact node with BELONGS_TO edge is created in Neo4j
And event crm:contact:upserted is written to events.jsonl
And search returns list of Contact objects with relevance ordering
```

## 4. Events

```
Events:
- crm:contact:upserted: contact created or updated in CRM
- crm:contact:synced: contact synced to Engram/Qdrant/Neo4j
- crm:search:executed: search performed across contacts
```

## 5. Dependencies

```
Dependencies:
- Python 3.14+
- SQLite3 (stdlib)
- httpx (for Qdrant/Neo4j HTTP sync)
- Engram MCP server (port 8900, for memory storage)
- Qdrant (port 6333, for vector search)
- Neo4j (port 7687, for knowledge graph)
- Events file: state/events/events.jsonl
```

## 6. Tools

```
Tools:
- crm_client_add(name, phone, company, email, source, tags): create/update contact
- crm_client_search(query): search contacts by name/phone/company
- crm_client_get(crm_id): get contact details by ID
- crm_client_list(limit): list recent contacts
- crm_client_sync(crm_id): sync specific contact to all stores
- crm_client_sync_all(tenant): sync all contacts to all stores
```

## 7. Policies

```
Policies:
- Each contact MUST have a unique crm_id (prefix CT-{timestamp}-{uuid})
- Phone numbers MUST be stored in E.164 format without +
- Company field SHOULD be normalized to lowercase for search
- Sync to Engram is ALWAYS synchronous (primary store)
- Sync to Qdrant/Neo4j is BEST EFFORT (async, non-blocking)
- Events ALWAYS written before sync operations
- Tags MUST be comma-separated, lowercase
- Contact data MUST NOT include secrets or API keys
```

## 8. Success Metrics

```gherkin
Success Metrics:
- add_latency: Given contact data When creating Then stored in < 100ms (SQLite)
- sync_latency: Given stored contact When syncing Then Engram write < 50ms
- search_latency: Given query When searching Then results in < 200ms
- uptime: Given CRM module in period When accessed Then available > 99.9%
```

## 9. Failure Conditions

```
Failure Conditions:
- SQLite write failure: disk full or permissions error (log + retry)
- Engram sync failure: Engram DB corrupted or locked (skip, log event)
- Qdrant sync failure: Qdrant not running or connection refused (log, continue)
- Neo4j sync failure: Neo4j not running or auth error (log, continue)
- Search query timeout: slow FTS query (fallback to LIKE with timeout limit)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If SQLite fails → check disk space and permissions on clients/aztrotech/crm/crm.db
2. If Engram fails → check engram_mcp service, restart if needed
3. If Qdrant fails → docker restart sdc-qdrant, run crm_client_sync_all
4. If Neo4j fails → docker restart sdc-neo4j, run crm_client_sync_all
5. Run `python3 -m clients.aztrotech.crm.client list` to verify CRM is accessible
6. Run `python3 -m clients.aztrotech.crm.client sync-all --tenant aztrotech` to re-sync all
```

## 11. Business Value

```
Business Value: Centralized client registry enables personalized RAG, tracks client history across channels, feeds Engram memory for context-aware conversations, and builds the Neo4j knowledge graph for relationship discovery.
```

## 12. Parent OS

```
Parent OS: Sales OS — unified customer data platform
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: ADR-20260721-CRM-ARCHITECTURE
- Events: crm:contact:upserted, crm:contact:synced, crm:search:executed
- Logs: state/logs/skills/crm-client.log
- Tests: tests/clients/test_crm.py
```
