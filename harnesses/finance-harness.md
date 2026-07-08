# Finance Harness — Financial Operations Agent

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: HARNESS-FIN-001

---

## 1. Mission

Track every dollar with zero manual effort and alert before any budget is exceeded.

## 2. Capabilities

```
Capabilities:
- Cost Tracking: Automatically log and categorize all AI and infra costs
  Events: cost_recorded, financial_summary
- Budget Management: Track spending against budget allocations
  Events: budget_alert, budget_exceeded
- Revenue Tracking: Log and report revenue from all sources
  Events: revenue_recorded
- Invoice Generation: Auto-generate invoices for customers
  Events: invoice_generated
```

## 3. Skills

```
Skills:
- track-finance: Automated financial tracking and reporting
  Source: skills/track-finance.skill.md
```

## 4. Policies

```
Policies:
- Every AI call is logged to FinOps before execution
- Budget reports generated daily
- Alerts fire when any category exceeds 80% of budget
- All financial data is stored in Historical Memory
```

## 5. Memory Scope

```
Memory Scope:
  Read: Layer 5 (Business)
  Write: Layer 1 (Working), Layer 5 (Business), Layer 6 (Historical)
```

## 6. Approval Requirements

```
Approval Requirements:
- budget override: approve
- invoice > $1k: approve
- cost category change: notify
```

## 7. Failure Modes

```
Failure Modes:
- FinOps file corrupt: JSON parse error (restore from backup)
- Revenue API down: cannot fetch revenue data (use last known)
- Budget data stale: no data in > 24h (alert)
```

## 8. Recovery Procedures

```
Recovery Procedures:
- FinOps corrupt: restore from .bak, log corruption
- Revenue API down: use cached data, flag as estimated
- Budget stale: project from historical trends
```

## 9. Metrics

```
Metrics:
- tracking_coverage: Given financial events When logged Then percentage
  Target: > 99%
- report_accuracy: Given reported costs When reconciled Then variance
  Target: < 1%
- alert_latency: Given budget exceeded When alerted Then seconds
  Target: < 60s
```

## 10. Tests

```gherkin
Feature: Finance Harness
  Scenario: Track AI call cost
    Given an AI call is made
    When the Finance harness logs it
    Then cost is recorded in finops.jsonl
    And cost_recorded event fires

  Scenario: Daily budget report
    Given it is 08:00 daily
    When the Finance harness generates report
    Then financial_summary event fires
```

## 11. Observability

```
Observability:
- Health endpoint: via Web UI status
- Metrics: tracking_coverage, report_accuracy, alert_latency
- Log level: INFO
- Log location: state/logs/harnesses/finance-harness.log
```

## 12. Dependencies

```
Dependencies:
- track-finance: skill (skills/track-finance.skill.md)
- finops.sh: cost calculation
- State: state/finops.jsonl
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
