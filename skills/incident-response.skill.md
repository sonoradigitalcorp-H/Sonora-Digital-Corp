# incident-response — Structured Incident Response Runbook

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-IR-001

---

## 1. Business Objective

Execute a structured incident response runbook with detection, diagnosis, recovery, and post-mortem phases to minimize mean time to resolve.

## 2. Inputs (Gherkin)

```gherkin
Given system is operational
When an anomaly is detected by monitoring
Or a user reports a service disruption
```

## 3. Outputs (Gherkin)

```gherkin
Then incident is detected and classified by severity
And root cause is diagnosed
And service is recovered within SLA
And post-mortem is documented in engram
```

## 4. Events

```
Events:
- incident:detected: anomaly identified and incident created
- incident:diagnosed: root cause determined
- incident:resolved: service restored to normal
```

## 5. Dependencies

```
Dependencies:
- Health check system: health_all endpoint
- Notification channels: Telegram, WhatsApp
- Engram: post-mortem persistence
- LLM: diagnostic assistant
```

## 6. Tools

```
Tools:
- health_all: collect health status from all services
- engram_save: persist post-mortem to long-term memory
- telegram_notify: send alerts to incident channel
- llm_chat: analyze logs and suggest root cause
```

## 7. Policies

```
Policies:
- Every incident must be logged regardless of severity
- Response must follow runbook order: detect → diagnose → recover → post-mortem
- Post-mortem must be completed within 24 hours of resolution
- Critical incidents require Ops OS escalation within 5 minutes
```

## 8. Success Metrics

```gherkin
Success Metrics:
- mttd: Given incident occurs When detected Then minutes
  Target: < 2 min
- mttr: Given incident detected When resolved Then minutes
  Target: < 15 min
- post_mortem_rate: Given resolved incidents When documented Then percentage
  Target: 100%
```

## 9. Failure Conditions

```
Failure Conditions:
- Detection missed: monitoring fails to alert (escalate to Ops)
- Recovery fails: runbook steps unsuccessful (escalate to senior engineer)
- Escalation fails: notify channel unreachable (use backup channel)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If detection missed → check health_all manually, review recent logs
2. If recovery fails → try alternate recovery path, escalate if still failing
3. If escalation fails → send via backup channel (SMS, email), page on-call
4. Log all attempts to state/logs/skills/incident-response.log
```

## 11. Business Value

```
Business Value: MTTR reduced by 60%. Every incident has a runbook.
```

## 12. Parent OS

```
Parent OS: Ops
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: incident:detected, incident:diagnosed, incident:resolved
- Logs: state/logs/skills/incident-response.log
```
