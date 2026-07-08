# monitor-service — Service Health Monitoring

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-MS-001

---

## 1. Business Objective

Proactively monitor all critical services and auto-recover from failures before they impact customers.

## 2. Inputs (Gherkin)

```gherkin
Given a list of service endpoints with health check URLs
When scheduled trigger fires (every 5 min by default)
And retry count < max_retries (default: 3)
```

## 3. Outputs (Gherkin)

```gherkin
Then each service returns health status (UP/DOWN/DEGRADED)
And if any service is DOWN, service_down event fires
And auto-recovery procedure starts
And if all services UP, service_healthy event fires
```

## 4. Events

```
Events:
- service_down: fired when health check fails after max_retries
- service_recovered: fired when recovery succeeds
- service_degraded: fired when response time > threshold (2s)
- service_healthy: fired when all services pass health check
```

## 5. Dependencies

```
Dependencies:
- Systemd services: jarvis-webui, hermes-gateway, openclaw-gateway
- Docker containers: jarvis-neo4j, jarvis-qdrant, infra-postgres, infra-redis, hermes-api
- health check config: state/health-config.json
```

## 6. Tools

```
Tools:
- curl: for HTTP health checks
- systemctl: for systemd service status
- docker: for container health checks
- ss: for port listening checks
```

## 7. Policies

```
Policies:
- Every monitored service must have a health endpoint
- Retry 3 times before declaring DOWN
- Recovery must verify health before declaring RECOVERED
- No alert for the same service more than once per hour (debounce)
```

## 8. Success Metrics

```gherkin
Success Metrics:
- detection_time: Given service failure When detected Then seconds elapsed
  Target: < 30 seconds
- recovery_time: Given service down When recovered Then minutes elapsed
  Target: < 2 minutes
- false_positives: Given DOWN events When service was actually UP Then count
  Target: < 1% of checks
```

## 9. Failure Conditions

```
Failure Conditions:
- Network unreachable: cannot reach health endpoint (log, retry)
- Auth failure: health endpoint requires auth not configured (alert)
- Timeout: health check takes > 10s (log as degraded, not down)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. For systemd services: `systemctl restart <service>`
2. For Docker containers: `docker restart <container>`
3. After restart, wait 10s and re-check health
4. If recovery fails after 3 attempts → escalate to Ops OS
5. Log all recovery attempts to state/logs/monitor-service.log
```

## 11. Business Value

```
Business Value: Eliminates manual health checks. Estimated 5h/week saved. Reduces MTTR from ~15min to <2min.
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
- Events: service_down, service_recovered, service_degraded, service_healthy
- Logs: state/logs/skills/monitor-service.log
```
