# Initiative: improve-automation-coverage

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: initiative-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: INIT-001

---

## 1. Objective

Increase automation coverage from current baseline to > 80% by formalizing existing manual monitoring ops into the Ops Harness.

## 2. Hypothesis

```
Hypothesis: We believe that formalizing existing health checks and recovery scripts into the Ops Harness
will result in measurable automation coverage increase, reduced MTTR, and fewer founder interruptions.
```

## 3. Metric

```
Metric: automation_coverage
Gherkin: Given operational tasks in period When automated by system Then coverage = automated / total * 100
```

## 4. Target

```
Target: > 80% automation coverage (current baseline: ~60%)
```

## 5. Deadline

```
Deadline: 2026-07-17 (30 days from creation)
```

## 6. Kill Criteria

```
Kill Criteria:
- No measurable improvement in automation_coverage after 14 days
- Ops Harness causes more incidents than it prevents
- Founder dependency index does not decrease in first month
```

## 7. Scale Criteria

```
Scale Criteria:
- automation_coverage > 80% for 2 consecutive weeks
- MTTR reduced by > 50% from baseline
- Founder dependency index decreases by > 10%
```

## 8. Required Capabilities

```
Required Capabilities:
- Service Monitoring: Ops OS (existing — autonomous.sh)
- Incident Recovery: Ops OS (existing — systemctl/docker scripts)
- Backup Management: Ops OS (existing — backup.sh)
```

## 9. Expected Value

```
Expected Value:
- Automation: 20% increase in automation coverage (60% → 80%)
- Time saved: ~10h/week in manual monitoring
- Knowledge: 1 new harness, 1 new skill (monitor-service), 1 ADR
- Independence: Founder no longer needs to check service health manually
```

## 10. Parent OS

```
Parent OS: Ops
```

---

## Enterprise Score

| Metric | Score (0-10) | Justification |
|--------|-------------|---------------|
| Revenue Impact | 3 | Indirect — reduced downtime protects revenue |
| Scalability | 6 | Harness pattern scales to all 10 OS |
| Reusability | 8 | Ops Harness template reuses AGENT-HARNESS-TEMPLATE |
| Automation Impact | 9 | Directly increases automation coverage 60% → 80% |
| Knowledge Impact | 7 | Creates ADR, harness, skill for future reference |
| Reliability | 8 | Formal monitoring reduces MTTR from 15min to <2min |
| Founder Independence | 8 | Founder no longer manually checks services |
| Operational Simplicity | 7 | Consolidates 5 scripts into 1 harness |
| Customer Value | 5 | Indirect — fewer outages means happier customers |
| FinOps Efficiency | 3 | No FinOps tracking yet — baseline being established this session |

**Total Score: 64/100** ✅ (passes ≥ 60 threshold)

---

## Long-Term Survival Test

| Horizon | Impact | Risk |
|---------|--------|------|
| 1 Year | Standardized Ops across all services | Low — harness is template-based |
| 3 Years | Ops OS becomes self-healing system | Low — auto-recovery already works |
| 5 Years | Infrastructure runs without human Ops | Medium — depends on infrastructure stability |
| 10 Years | Full autonomy for standard ops | Low — principles are infrastructure-agnostic |

---

## Approval

```
Score: 64/100
Verdict: Approved
Approved by: Strategy OS
Date: 2026-06-17
```
