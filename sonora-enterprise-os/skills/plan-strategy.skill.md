# plan-strategy — Strategic Planning & Review

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-STR-001

---

## 1. Business Objective

Generate weekly strategic reviews with actionable insights, enterprise score trends, and kill/recommend decisions.

## 2. Inputs (Gherkin)

```gherkin
Given weekly review timer triggers (every Monday 08:00)
Or on-demand request from founder
When enterprise data is available (metrics, events, initiatives)
```

## 3. Outputs (Gherkin)

```gherkin
Then enterprise score is calculated from 10 metrics
And initiative statuses are reviewed
And kill/recommend decisions are generated
And health_review_completed event fires with full report
```

## 4. Events

```
Events:
- health_review_completed: weekly review finished
- kill_recommendation: initiative recommended for termination
- scale_recommendation: initiative recommended for scaling
- strategic_alert: enterprise score dropped below threshold
```

## 5. Dependencies

```
Dependencies:
- Enterprise metrics: metrics/enterprise-score.md
- Event store: state/logs/events.jsonl
- FinOps data: state/finops.jsonl
- Initiatives: initiatives/*.md
```

## 6. Tools

```
Tools:
- python3: data aggregation and scoring
- finops.sh: financial data access
- sqlite3: Engram DB for historical comparison
```

## 7. Policies

```
Policies:
- Weekly reviews are generated every Monday
- Enterprise score must be calculated from event data (not manual)
- Kill recommendations require majority of OS approval
- No initiative may run beyond 60 days without review
- Strategic decisions must be stored in Historical Memory
```

## 8. Success Metrics

```gherkin
Success Metrics:
- review_time: Given trigger When report generated Then minutes
  Target: < 2 min
- recommendation_accuracy: Given recommendations When evaluated Then accuracy
  Target: > 80%
- score_improvement: Given 30d period When score compared Then delta
  Target: positive trend
```

## 9. Failure Conditions

```
Failure Conditions:
- Data unavailable: event store empty or corrupt (use last known)
- Score calculation error: missing metric data (estimate, flag)
- Review timeout: data aggregation > 5 min (incremental, cache)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If data unavailable → use last known enterprise score, flag as estimated
2. If score error → skip problematic metric, note in report
3. If timeout → cache intermediate results, resume incrementally
4. Log all attempts to state/logs/skills/plan-strategy.log
```

## 11. Business Value

```
Business Value: Automated strategic oversight. Eliminates manual review prep. Estimated 4h/week saved.
```

## 12. Parent OS

```
Parent OS: Strategy
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: health_review_completed, kill_recommendation, scale_recommendation, strategic_alert
- Logs: state/logs/skills/plan-strategy.log
```
