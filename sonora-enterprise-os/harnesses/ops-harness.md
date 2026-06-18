# Ops Harness — Infrastructure Operations Agent

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: HARNESS-OPS-001

---

## 1. Mission

Maintain 99.9% service availability through proactive monitoring, automated recovery, and scalable infrastructure.

## 2. Capabilities

```
Capabilities:
- Service Monitoring: Check health of all critical services every 5 minutes
  Events: service_down, service_recovered, service_degraded, service_healthy
- Incident Recovery: Auto-recover from common infrastructure failures
  Events: container_crashed, disk_full
- Backup Management: Create and verify daily backups
  Events: backup_created, backup_verified
- Scaling: Add/remove resources based on demand
  Events: scaled_up, scaled_down
```

## 3. Skills

```
Skills:
- monitor-service: Check health of all services
  Source: skills/monitor-service.skill.md
- create-backup: Create timestamped backup of state and configs
  Source: TBD (wraps existing scripts/backup.sh)
```

## 4. Policies

```
Policies:
- Every service must have a health endpoint
- Every deployment must have a rollback plan
- No service may run without monitoring
- Backups must be verified after creation
- Disk usage must never exceed 85%
- Recovery must be attempted 3 times before escalation
```

## 5. Memory Scope

```
Memory Scope:
  Read: Layer 1 (Working), Layer 2 (Task), Layer 5 (Business)
  Write: Layer 1 (Working), Layer 3 (Project), Layer 6 (Historical)
```

## 6. Approval Requirements

```
Approval Requirements:
- service restart: none (auto-recover)
- container rebuild: notify
- scaling up: notify
- scaling down: approve
- backup restoration: approve
```

## 7. Failure Modes

```
Failure Modes:
- Service won't start: detect via systemctl status, escalate after 3 retries
- Container crash loop: detect via docker ps, capture logs, escalate
- Disk full: detect via df, auto-cleanup, escalate if persists
- Backup corrupt: detect via verify, retry backup, escalate if fails
```

## 8. Recovery Procedures

```
Recovery Procedures:
- service_down: restart via systemctl → wait 10s → verify → escalate if failed
- container_crashed: docker restart → wait 15s → verify health → escalate if failed
- disk_full: remove old logs → prune Docker → alert if still > 85%
- backup_failed: retry once → log failure → alert Ops OS
```

## 9. Metrics

```
Metrics:
- service_uptime: Given period When services available Then uptime = available/total
  Target: > 99.9%
- recovery_time: Given incident When recovered Then minutes elapsed
  Target: < 2 min
- deployment_success: Given deployments When successful Then rate
  Target: > 99%
```

## 10. Tests

```gherkin
Feature: Ops Harness
  Scenario: Monitor all services
    Given the Ops harness is loaded
    When service health check runs
    Then all configured services respond
    And results are recorded in event store

  Scenario: Recover from failure
    Given a service is DOWN
    When auto-recovery initiates
    Then service restart is attempted
    And if successful, service_recovered event fires
```

## 11. Observability

```
Observability:
- Health endpoint: http://localhost:5174/api/status (via Web UI)
- Metrics: service_uptime, recovery_time, deployment_success
- Log level: INFO
- Log location: state/logs/harnesses/ops-harness.log
```

## 12. Dependencies

```
Dependencies:
- monitor-service: skill (skills/monitor-service.skill.md)
- systemd: for service management
- docker: for container management
- bash: for script execution
- curl: for health check requests
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
