# Sales Harness — Go-to-Market Agent

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: HARNESS-SLS-001

---

## 1. Mission

Drive predictable revenue growth by automating lead qualification, outreach, and pipeline management.

## 2. Capabilities

```
Capabilities:
- Lead Scoring: Evaluate and score leads based on behavior and fit
  Events: lead_scored, lead_qualified, lead_disqualified
- Pipeline Management: Track deals through sales stages
  Events: deal_created, deal_moved, deal_won, deal_lost
- Outreach Automation: Send personalized follow-ups on schedule
  Events: outreach_sent, response_received
```

## 3. Skills

```
Skills:
- qualify-lead: Score and qualify incoming leads
  Source: skills/qualify-lead.skill.md
```

## 4. Policies

```
Policies:
- Every lead must be scored within 5 minutes of acquisition
- No follow-up may be sent outside business hours (08:00-20:00)
- Lead data must never be stored outside Engram or CRM
- Deal stage changes must be auditable
```

## 5. Memory Scope

```
Memory Scope:
  Read: Layer 1 (Working), Layer 4 (Customer)
  Write: Layer 1 (Working), Layer 4 (Customer), Layer 6 (Historical)
```

## 6. Approval Requirements

```
Approval Requirements:
- lead disqualified: notify
- deal > $10k: approve
- outreach to existing customer: none
- discount > 20%: approve
```

## 7. Failure Modes

```
Failure Modes:
- Lead data incomplete: required fields missing (flag, request more data)
- CRM API down: cannot read/write pipeline (queue, retry)
- Scoring timeout: lead scoring takes > 30s (fallback to manual)
```

## 8. Recovery Procedures

```
Recovery Procedures:
- lead data incomplete: request enrichment from source, hold in queue
- CRM API down: cache locally, sync when available
- scoring timeout: use heuristic rules, flag for review
```

## 9. Metrics

```
Metrics:
- lead_to_deal_rate: Given qualified leads When converted Then percentage
  Target: > 20%
- pipeline_velocity: Given deal creation When closed Then days
  Target: < 30d
- response_rate: Given outreach sent When responded Then percentage
  Target: > 15%
```

## 10. Tests

```gherkin
Feature: Sales Harness
  Scenario: Score incoming lead
    Given a new lead is received
    When the Sales harness processes it
    Then the lead is scored and stored
    And lead_scored event fires

  Scenario: Qualify high-value lead
    Given a lead with score > 80
    When qualification runs
    Then lead_qualified event fires
```

## 11. Observability

```
Observability:
- Health endpoint: via Web UI status
- Metrics: lead_to_deal_rate, pipeline_velocity, response_rate
- Log level: INFO
- Log location: state/logs/harnesses/sales-harness.log
```

## 12. Dependencies

```
Dependencies:
- qualify-lead: skill (skills/qualify-lead.skill.md)
- Engram DB: lead storage
- CRM API: pipeline management
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
