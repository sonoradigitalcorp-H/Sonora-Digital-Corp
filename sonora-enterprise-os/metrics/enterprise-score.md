# Enterprise Score — Sonora Digital Corp

**Version**: 1.0.0
**Audit ID**: METRICS-SCORE-001

---

Every initiative must score ≥ 60 to be approved. Score is calculated from 9 metrics, each weighted equally (max 10 points each).

---

## Score Formula

```
Enterprise Score = SUM(metric_score for all 9 metrics) / 9
```

Each metric scored 0–10:
- 0–3: Poor
- 4–6: Acceptable
- 7–8: Good
- 9–10: Excellent

---

## The 9 Metrics

### 1. Revenue Impact

| Dimension | Value |
|-----------|-------|
| Gherkin | Given initiative When revenue projected Then score = impact/total_revenue * 10 |
| Weight | 10/100 |
| Source | Finance OS — `revenue_recorded` event |
| Target | > $1k/month per initiative |

### 2. Scalability

| Dimension | Value |
|-----------|-------|
| Gherkin | Given initiative When users multiplied by N Then score = can_handle_10x |
| Weight | 10/100 |
| Source | Ops OS — `scaled_up` event |
| Target | Handles 10x current load without redesign |

### 3. Reusability

| Dimension | Value |
|-----------|-------|
| Gherkin | Given initiative When implemented Then score = other_OS_that_can_use / total_OS |
| Weight | 10/100 |
| Source | Agent OS — skill registry |
| Target | Reusable by ≥ 3 other OS |

### 4. Automation Impact

| Dimension | Value |
|-----------|-------|
| Gherkin | Given initiative When deployed Then score = automated_steps / total_steps |
| Weight | 10/100 |
| Source | Agent OS — `agent_spawned` event |
| Target | > 80% of steps automated |

### 5. Knowledge Impact

| Dimension | Value |
|-----------|-------|
| Gherkin | Given initiative When completed Then score = ADRs_created / total_decisions |
| Weight | 10/100 |
| Source | Knowledge OS — `adr_created` event |
| Target | ADR coverage > 90% |

### 6. Reliability

| Dimension | Value |
|-----------|-------|
| Gherkin | Given initiative When running for 30d Then score = uptime_percentage / 10 |
| Weight | 10/100 |
| Source | Ops OS — `service_down` event |
| Target | > 99.9% uptime |

### 7. Founder Independence

| Dimension | Value |
|-----------|-------|
| Gherkin | Given initiative When operating Then score = automated_decisions / total_decisions |
| Weight | 10/100 |
| Source | Strategy OS — `health_review_completed` event |
| Target | > 90% decisions without founder |

### 8. Operational Simplicity

| Dimension | Value |
|-----------|-------|
| Gherkin | Given initiative When maintained Then score = 10 - (components / max_components) |
| Weight | 10/100 |
| Source | Ops OS — monitoring data |
| Target | < 5 components per initiative |

### 9. Customer Value

| Dimension | Value |
|-----------|-------|
| Gherkin | Given initiative When measured Then score = customer_satisfaction / 10 |
| Weight | 10/100 |
| Source | Support OS — `satisfaction_recorded` event |
| Target | > 4.5 / 5.0 |

---

## Scoring Thresholds

| Score | Verdict | Action |
|-------|---------|--------|
| ≥ 90 | Exceptional | Scale immediately |
| 80–89 | Strong | Approve and fund |
| 70–79 | Good | Approve with monitoring |
| 60–69 | Acceptable | Approve conditionally |
| 40–59 | Weak | Require improvements |
| < 40 | Poor | Kill or reject |

---

## Calculation Frequency

| Update | Trigger | By |
|--------|---------|----|
| Per initiative | At creation | Quality OS |
| Per initiative | After completion | Quality OS |
| Enterprise-wide | Weekly | Strategy OS |
| Enterprise-wide | Quarterly | Strategy OS |

---

## Audit Trail

Every score change is recorded:

```gherkin
Given enterprise score is calculated
When weekly review triggers
Then score_updated event fires
And score stored in Historical Memory
And delta from previous score recorded
And if score < 60 then kill_recommendation generated
```
