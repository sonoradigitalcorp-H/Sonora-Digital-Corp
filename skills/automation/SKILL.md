# skills/automation — Operational Workflow Automation

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-AUT-001

---

## 1. Business Objective

Reduce manual operational tasks by 80% through scheduled bash/python automation pipelines, cron-managed workflows, and self-healing job retries.

## 2. Inputs (Gherkin)

```gherkin
Given a workflow definition exists in the automation registry
And the workflow trigger conditions are met (cron, webhook, or manual)
When the execution environment is ready and resources are available
```

## 3. Outputs (Gherkin)

```gherkin
Then the workflow executes all defined steps in order
And each step's output is logged and checked for errors
And the workflow status is recorded (completed, failed, or partial)
```

## 4. Events

```
Events:
- automation:workflow:started: a workflow began execution
- automation:workflow:completed: a workflow finished successfully
- automation:workflow:failed: a workflow encountered an unrecoverable error
```

## 5. Dependencies

```
Dependencies:
- Shell environment: service — bash, python3 runtime
- Cron daemon: service — scheduled execution
- Filesystem: data — script storage and log output
- Lock file system: data — prevent concurrent workflow execution
```

## 6. Tools

```
Tools:
- bash: execute shell commands and scripts
- python3: run Python automation scripts
- cron: schedule recurring workflows
```

## 7. Policies

```
Policies:
- Every workflow must have a defined timeout (default 30 min)
- Workflows must not execute concurrently with the same lock ID
- All stdout/stderr must be captured to logs
- Failed workflows must trigger the recovery procedure automatically
- Cron expressions must be validated before registration
```

## 8. Success Metrics

```gherkin
Success Metrics:
- completion_rate: Given workflows triggered When completed Then success rate
  Target: > 98%
- execution_time: Given workflow started When finished Then duration vs estimate
  Target: < 120% of estimate
- recovery_rate: Given workflow failed When retried Then success rate
  Target: > 80%
```

## 9. Failure Conditions

```
Failure Conditions:
- Script crash: non-zero exit code (detect via exit status check)
- Timeout: workflow exceeds max duration (detect via timeout signal)
- Resource exhaustion: disk full or OOM (detect via system metrics)
- Lock conflict: concurrent execution detected (detect via lock file check)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. Capture exit code and last 20 lines of output
2. Retry up to 3 times with exponential backoff (10s, 30s, 60s)
3. If all retries fail → escalate to Ops OS with full log bundle
4. Release lock file regardless of outcome
5. Log final status to state/logs/skills/automation.log
```

## 11. Business Value

```
Business Value: Reduces manual ops by 80%. Estimated 5h/week saved.
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
- ADR: ADR-2026-AUT-001
- Events: automation:workflow:started, automation:workflow:completed, automation:workflow:failed
- Logs: state/logs/skills/automation.log
```
