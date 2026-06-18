# Support Harness — Client Care Agent

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: HARNESS-SUP-001

---

## 1. Mission

Resolve 80% of support tickets within 5 minutes while maintaining > 4.5/5.0 customer satisfaction.

## 2. Capabilities

```
Capabilities:
- Ticket Resolution: Classify and resolve incoming support tickets
  Events: ticket_received, ticket_resolved, ticket_escalated
- Knowledge Base: Auto-build KB from resolved tickets
  Events: kb_entry_created, kb_entry_updated
- Satisfaction Tracking: Measure and report customer satisfaction
  Events: satisfaction_recorded
```

## 3. Skills

```
Skills:
- resolve-ticket: Classify, resolve, and escalate support tickets
  Source: skills/resolve-ticket.skill.md
```

## 4. Policies

```
Policies:
- Tickets are classified within 30 seconds of receipt
- P1 tickets are escalated to human within 2 minutes
- Every resolution is added to knowledge base
- Customer is notified at every status change
```

## 5. Memory Scope

```
Memory Scope:
  Read: Layer 1 (Working), Layer 4 (Customer), Layer 5 (Business)
  Write: Layer 1 (Working), Layer 4 (Customer), Layer 6 (Historical)
```

## 6. Approval Requirements

```
Approval Requirements:
- ticket escalation: none
- refund > $100: approve
- account deletion: approve
- SLA waiver: approve
```

## 7. Failure Modes

```
Failure Modes:
- Ticket misclassification: wrong category assigned (review, retrain)
- Resolution not found: KB returns no match (escalate, create entry)
- Customer dissatisfied: rating < 3 (escalate to human, review)
```

## 8. Recovery Procedures

```
Recovery Procedures:
- misclassification: log error, reassign, update classification model
- no resolution: escalate to human with full context
- dissatisfied: auto-escalate to senior support, tag for review
```

## 9. Metrics

```
Metrics:
- first_response_time: Given ticket received When first response Then seconds
  Target: < 30s
- resolution_rate: Given tickets in period When resolved Then percentage
  Target: > 80%
- customer_satisfaction: Given resolved tickets When rated Then average
  Target: > 4.5 / 5.0
```

## 10. Tests

```gherkin
Feature: Support Harness
  Scenario: Resolve known issue
    Given a ticket matching a known resolution
    When the Support harness processes it
    Then the ticket is resolved automatically
    And ticket_resolved event fires

  Scenario: Escalate unknown issue
    Given a ticket with no matching KB entry
    When resolution is attempted
    Then ticket_escalated event fires
```

## 11. Observability

```
Observability:
- Health endpoint: via Web UI status
- Metrics: first_response_time, resolution_rate, customer_satisfaction
- Log level: INFO
- Log location: state/logs/harnesses/support-harness.log
```

## 12. Dependencies

```
Dependencies:
- resolve-ticket: skill (skills/resolve-ticket.skill.md)
- Engram DB: knowledge base storage
- Support platform API: ticket management
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
