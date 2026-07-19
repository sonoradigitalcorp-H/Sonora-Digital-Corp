# skills/monitor — System Health Monitoring and Auto-Repair

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-MON-001

---

## 1. Business Objective

Provide 24/7 system health monitoring with auto-repair — checking every service every 5 minutes, automatically restarting failed services, and alerting human operators when auto-repair fails after 3 attempts.

## 2. Inputs (Gherkin)

```gherkin
Given a service registry exists listing all monitored endpoints and services
And health check scripts are defined per service type (HTTP, TCP, process)
When the 5-minute monitoring interval fires OR a manual check is triggered
```

## 3. Outputs (Gherkin)

```gherkin
Then each service health status is checked and recorded
And failed services trigger auto-repair (restart, re-pull, re-deploy)
And incident records are saved to Engram with timestamps
And Telegram alerts are sent if auto-repair fails 3 times
```

## 4. Events

```
Events:
- system:service:up: a service is healthy and operational
- system:service:down: a service failed its health check
- system:service:recovered: a service recovered after auto-repair
- system:alert:critical: auto-repair exhausted, human intervention needed
```

## 5. Dependencies

```
Dependencies:
- Service registry: data — list of all monitored services
- Systemd: service — service lifecycle management
- Docker: service — container health checks
- Prometheus: service — metrics collection (optional)
- Telegram bot: service — alert delivery
- Engram: service — incident history
```

## 6. Tools

```
Tools:
- engram_save: record incidents, recoveries, and status snapshots
- telegram_notify: send critical alerts to ops channel
```

## 7. Policies

```
Policies:
- Health checks must complete within 10 seconds per service
- Auto-repair must attempt 3 times before alerting
- Alerts must include service name, error, and attempt count
- Downtime events must be logged with start and end timestamps
- Monitoring must not trigger on scheduled maintenance windows
- Each service must have a defined max acceptable downtime
```

## 8. Success Metrics

```gherkin
Success Metrics:
- check_interval: Given monitoring loop When checked Then deviation from 5-min schedule
  Target: < 10 sec
- auto_recovery: Given service down When auto-repaired Then recovery rate
  Target: > 85%
- mean_uptime: Given all services When measured over 30 days Then availability
  Target: > 99.5%
```

## 9. Failure Conditions

```
Failure Conditions:
- Monitoring loop crash: the monitor process itself stops (detect via supervisor)
- False positive: service reported down but is actually up (detect via manual verify)
- False negative: service actually down but reported up (detect via user complaint)
- Alert delivery failure: Telegram API unreachable (detect via HTTP timeout)
- Log storage full: Engram write fails (detect via disk usage)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If monitor process crashes → systemd auto-restarts it (restart=always)
2. If false positive detected → recalibrate health check threshold
3. If false negative → add additional health check dimension
4. If Telegram fails → fall back to email notification, retry Telegram
5. If log storage full → rotate logs, archive to cold storage
6. Log all events to state/logs/skills/monitor.log
```

## 11. Business Value

```
Business Value: 24/7 system health with auto-repair. Prevents extended downtime.
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
- ADR: ADR-2026-MON-001
- Events: system:service:up, system:service:down, system:service:recovered, system:alert:critical
- Logs: state/logs/skills/monitor.log
```
