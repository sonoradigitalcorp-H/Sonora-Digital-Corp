# hermes-watchdog-status — Hermes System Health Status

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-HWS-001

---

## 1. Business Objective

Provide real-time system health status and service availability information via Telegram, enabling remote infrastructure monitoring.

## 2. Inputs (Gherkin)

```gherkin
Given user requests system status
When trigger keywords are detected: "sistema", "estado del sistema", "health", "servicios", "todo bien", "cómo está el sistema", "como esta el sistema"
```

## 3. Outputs (Gherkin)

```gherkin
Then API health status is retrieved from the status endpoint
And response includes API, database, and Redis status
And version information is displayed
```

## 4. Events

```
Events:
- hermes:watchdog-status:executed: health check completed
```

## 5. Dependencies

```
Dependencies:
- Hermes API: status endpoint at http://api:8000/status
- Network: internal connectivity between Telegram and Hermes API
```

## 6. Tools

```
Tools:
- http_get: retrieve health status from Hermes API endpoint
```

## 7. Policies

```
Policies:
- Health checks must complete within 5 seconds
- Internal endpoint must not be exposed externally
- Failed checks must not reveal internal stack details
- Response must be formatted for Telegram markdown
- Service degradation must trigger incident:detected event
```

## 8. Success Metrics

```gherkin
Success Metrics:
- check_time: Given status request When completed Then seconds
  Target: < 3 s
- uptime: Given checks in period When all services healthy Then percentage
  Target: > 99.5%
```

## 9. Failure Conditions

```
Failure Conditions:
- API unreachable: status endpoint not responding (network issue)
- Partial data: one or more health checks fail (partial degradation)
- Timeout: status check exceeds 10s (assume degraded)
- Internal error: API returns 500 (escalate)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If API unreachable → retry 3 times with 2s backoff
2. If partial data → report which services are down, identify pattern
3. If timeout → flag as degraded, notify Ops OS
4. If internal error → capture response, escalate to Ops OS
5. Log all attempts to state/logs/skills/hermes-watchdog-status.log
```

## 11. Business Value

```
Business Value: Remote system monitoring from Telegram eliminates need for SSH or dashboard access for basic health checks.
```

## 12. Parent OS

```
Parent OS: Knowledge
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: hermes:watchdog-status:executed
- Logs: state/logs/skills/hermes-watchdog-status.log
```
