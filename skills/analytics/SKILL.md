# skills/analytics — Business Intelligence Reporting

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-ANL-001

---

## 1. Business Objective

Automate 90% of ad-hoc business reporting across all tenants, generating revenue dashboards, stream metrics, and KPI summaries daily with zero human intervention.

## 2. Inputs (Gherkin)

```gherkin
Given Hasura database contains tenant data (transactions, streams, artists)
And an analytics schedule is configured (daily, weekly, monthly)
When the scheduled trigger fires OR a user requests a report
```

## 3. Outputs (Gherkin)

```gherkin
Then a structured report is generated with revenue, trends, and KPIs
And the report is saved to Engram for future reference
And a notification is sent to the requesting tenant's channel
```

## 4. Events

```
Events:
- analytics:report:generated: a report was produced and saved
- analytics:metric:updated: a tracked metric changed beyond threshold
- analytics:schedule:missed: the daily pipeline did not complete
```

## 5. Dependencies

```
Dependencies:
- Hasura: service — source of all tenant data
- Engram: service — storage for report history and patterns
- RAG index: data — enrichment context for LLM analysis
- LLM provider: service — generates natural-language analysis
```

## 6. Tools

```
Tools:
- hasura_query: fetch artists, transactions, streams from Hasura
- engram_search: retrieve past reports and patterns
- rag_search: fetch enrichment context from knowledge base
- llm_chat: generate executive summaries and recommendations
```

## 7. Policies

```
Policies:
- Only access data from the requesting tenant (tenant isolation)
- Never expose PII or financial details in reports
- Reports must be generated within 60 seconds
- All generated reports must be saved to Engram for audit trail
- Schedule must fire at 08:00 daily; if missed, retry at 09:00
```

## 8. Success Metrics

```gherkin
Success Metrics:
- report_time: Given report request When generated Then seconds
  Target: < 30 sec
- coverage: Given scheduled reports When delivered Then percent on time
  Target: > 95%
- accuracy: Given manual audit When compared to automated report Then match rate
  Target: > 99%
```

## 9. Failure Conditions

```
Failure Conditions:
- Data source unavailable: Hasura connection fails (detect via HTTP timeout)
- Empty result set: query returns zero rows (detect via row count)
- LLM failure: analysis generation errors (detect via API error code)
- Tenant isolation breach: cross-tenant data leak (detect via audit log review)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If Hasura fails → retry 3x with 5s backoff, if still down → alert Ops OS
2. If empty result → check data freshness, re-query with wider date range
3. If LLM fails → retry once, if persists → generate template-based report
4. Log all attempts to state/logs/skills/analytics.log
5. Escalate persistent failures to Quality OS for metric recalibration
```

## 11. Business Value

```
Business Value: Automates 90% of ad-hoc reporting. Estimated 10h/week saved.
```

## 12. Parent OS

```
Parent OS: Quality
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: ADR-2026-ANL-001
- Events: analytics:report:generated, analytics:metric:updated, analytics:schedule:missed
- Logs: state/logs/skills/analytics.log
```
