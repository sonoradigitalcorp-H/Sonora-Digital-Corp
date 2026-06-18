# Strategy Harness — Direction & Growth Agent

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: HARNESS-STR-001

---

## 1. Mission

Generate weekly strategic reviews with enterprise score trends, initiative health, and actionable kill/recommend decisions.

## 2. Capabilities

```
Capabilities:
- Enterprise Scoring: Calculate enterprise score from event data
  Events: score_updated
- Initiative Review: Evaluate all active initiatives weekly
  Events: health_review_completed
- Kill/Scale Decisions: Recommend termination or scaling of initiatives
  Events: kill_recommendation, scale_recommendation
- Strategic Alerting: Alert when enterprise score drops below threshold
  Events: strategic_alert
```

## 3. Skills

```
Skills:
- plan-strategy: Strategic planning and weekly reviews
  Source: skills/plan-strategy.skill.md
```

## 4. Policies

```
Policies:
- Weekly reviews generated every Monday 08:00
- Enterprise score calculated from event data (not manual)
- Kill recommendations require majority OS approval
- No initiative runs beyond 60 days without review
```

## 5. Memory Scope

```
Memory Scope:
  Read: All layers (1-7)
  Write: Layer 6 (Historical), Layer 7 (Eternal)
```

## 6. Approval Requirements

```
Approval Requirements:
- initiative kill: approve (after majority recommendation)
- initiative scale: approve
- strategy pivot: approve
- enterprise score below 60: escalate to founder
```

## 7. Failure Modes

```
Failure Modes:
- Data unavailable: event store empty (use last known)
- Score error: missing metric (estimate, flag)
- Review timeout: aggregation > 5 min (cache, incremental)
```

## 8. Recovery Procedures

```
Recovery Procedures:
- data unavailable: use last known score, flag as estimated
- score error: skip problematic metric, note in report
- timeout: cache intermediate results, resume incrementally
```

## 9. Metrics

```
Metrics:
- review_time: Given trigger When report generated Then minutes
  Target: < 2 min
- recommendation_accuracy: Given recommendations When evaluated Then percentage
  Target: > 80%
- score_improvement: Given 30d period When compared Then trend
  Target: positive
```

## 10. Tests

```gherkin
Feature: Strategy Harness
  Scenario: Calculate enterprise score
    Given event data is available
    When the Strategy harness calculates score
    Then all 10 metrics are evaluated
    And score_updated event fires

  Scenario: Weekly review
    Given it is Monday 08:00
    When weekly review triggers
    Then health_review_completed event fires
```

## 11. Observability

```
Observability:
- Health endpoint: via Web UI status
- Metrics: review_time, recommendation_accuracy, score_improvement
- Log level: INFO
- Log location: state/logs/harnesses/strategy-harness.log
```

## 12. Dependencies

```
Dependencies:
- plan-strategy: skill (skills/plan-strategy.skill.md)
- Event store: state/logs/events.jsonl
- FinOps: state/finops.jsonl
- Initiatives: initiatives/*.md
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
