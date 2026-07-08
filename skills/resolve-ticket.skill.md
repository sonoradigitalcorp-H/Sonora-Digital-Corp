# resolve-ticket — Automated Ticket Resolution

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-SUP-001

---

## 1. Business Objective

Resolve 80% of incoming support tickets within 5 minutes without human intervention.

## 2. Inputs (Gherkin)

```gherkin
Given a support ticket is created
When ticket has structured data (category, priority, description)
And knowledge base contains relevant entries
```

## 3. Outputs (Gherkin)

```gherkin
Then ticket is classified by category and priority
And resolution is attempted from knowledge base
And if resolved, ticket_closed event fires
And if unresolved, ticket_escalated event fires with context
```

## 4. Events

```
Events:
- ticket_received: new ticket created
- ticket_resolved: ticket closed successfully
- ticket_escalated: ticket requires human intervention
- satisfaction_recorded: customer provides feedback
```

## 5. Dependencies

```
Dependencies:
- Knowledge OS: access to Engram DB for resolution lookup
- Support platform: API access for ticket CRUD
```

## 6. Tools

```
Tools:
- sqlite3: query Engram DB for known resolutions
- curl: interact with support platform API
- python3: classification and matching logic
```

## 7. Policies

```
Policies:
- Every ticket must be classified within 30 seconds
- P1 tickets must be escalated to human within 2 minutes
- Resolution suggestions must cite knowledge source
- Customer must be notified at every status change
```

## 8. Success Metrics

```gherkin
Success Metrics:
- resolution_time: Given ticket received When resolved Then minutes elapsed
  Target: < 5 min for automated, < 30 min for escalated
- auto_resolution_rate: Given tickets in period When auto-resolved Then rate
  Target: > 80%
- customer_satisfaction: Given closed ticket When rated Then score
  Target: > 4.5 / 5.0
```

## 9. Failure Conditions

```
Failure Conditions:
- Unclassified ticket: auto-classification confidence < 70% (flag for review)
- No resolution found: knowledge base has no match (escalate)
- API unreachable: support platform down (queue, retry)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If classification fails → default to medium priority, flag for review
2. If no resolution found → escalate with full context to Support OS
3. If API unreachable → queue locally, retry every 30s up to 10 times
4. Log all attempts to state/logs/skills/resolve-ticket.log
```

## 11. Business Value

```
Business Value: Eliminates 80% of manual support work. Estimated 10h/week saved per support agent.
```

## 12. Parent OS

```
Parent OS: Support
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: ticket_received, ticket_resolved, ticket_escalated, satisfaction_recorded
- Logs: state/logs/skills/resolve-ticket.log
```
