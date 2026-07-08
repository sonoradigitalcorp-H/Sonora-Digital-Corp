# track-finance — Automated Financial Tracking

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-FIN-001

---

## 1. Business Objective

Track every dollar spent and earned across AI operations, infrastructure, and services with zero manual bookkeeping.

## 2. Inputs (Gherkin)

```gherkin
Given financial data is available (AI calls, infra costs, revenue)
When scheduled trigger fires (daily)
Or on-demand trigger fires (manual request)
```

## 3. Outputs (Gherkin)

```gherkin
Then AI costs are calculated from finops.jsonl
And infrastructure costs are estimated
And revenue data is aggregated
And financial_summary event fires
And if costs exceed budget, budget_alert event fires
```

## 4. Events

```
Events:
- financial_summary: daily cost and revenue snapshot
- budget_alert: spending exceeds allocated budget
- invoice_generated: customer invoice created
- revenue_recorded: revenue event logged
```

## 5. Dependencies

```
Dependencies:
- FinOps data: state/finops.jsonl
- Infrastructure: Docker, VPS monitoring
- Revenue data: Stripe API or store data
```

## 6. Tools

```
Tools:
- finops.sh: cost calculation and reporting
- curl: API calls for platform data
- python3: aggregation and analysis
```

## 7. Policies

```
Policies:
- Every AI call must be logged to FinOps before execution
- Budget reports are generated daily
- Alerts fire when any category exceeds 80% of budget
- Monthly financial reviews are stored in Historical Memory
```

## 8. Success Metrics

```gherkin
Success Metrics:
- tracking_coverage: Given financial events When logged Then percentage of all events tracked
  Target: > 99%
- report_accuracy: Given reported costs When reconciled Then variance
  Target: < 1%
- alert_latency: Given budget exceedance When alerted Then seconds
  Target: < 60s
```

## 9. Failure Conditions

```
Failure Conditions:
- FinOps file corrupt: JSON parse error (rebuild from backup)
- API unreachable: revenue source down (use last known data)
- Budget data stale: no data in > 24h (alert, use estimates)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If FinOps file corrupt → restore from .bak, log corruption event
2. If API unreachable → use cached data, flag as estimated
3. If data stale → use projected values based on historical trends
4. Log all attempts to state/logs/skills/track-finance.log
```

## 11. Business Value

```
Business Value: Zero-effort financial tracking. Eliminates manual bookkeeping. Estimated 3h/week saved.
```

## 12. Parent OS

```
Parent OS: Finance
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: financial_summary, budget_alert, invoice_generated, revenue_recorded
- Logs: state/logs/skills/track-finance.log
```
