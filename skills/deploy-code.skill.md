# deploy-code — Automated Code Deployment

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-DEV-001

---

## 1. Business Objective

Deploy code from PR merge to production in under 2 minutes with zero manual steps.

## 2. Inputs (Gherkin)

```gherkin
Given a PR is merged to main branch
When CI passes all checks (tests, lint, typecheck)
And deployment slot is available
```

## 3. Outputs (Gherkin)

```gherkin
Then code is deployed to staging
And staging passes smoke tests
And code is promoted to production
And deployment_completed event fires
Or if any step fails, deployment_failed event fires
```

## 4. Events

```
Events:
- deployment_started: CI passes, deployment begins
- deployment_completed: code is live in production
- deployment_failed: any deployment step fails
- rollback_completed: automatic rollback finishes
```

## 5. Dependencies

```
Dependencies:
- Git: source code and CI/CD
- Docker: container builds and registry
- Systemd: service restart
```

## 6. Tools

```
Tools:
- git: pull, checkout, merge
- docker: build, tag, push, run
- systemctl: restart services
- curl: smoke test endpoints
```

## 7. Policies

```
Policies:
- Every deployment must pass CI first
- Staging must pass smoke tests before production
- Rollback must be available for every release
- No deployments between 22:00 and 06:00 without approval
- Max deployment time: 5 minutes before auto-rollback
```

## 8. Success Metrics

```gherkin
Success Metrics:
- deployment_time: Given trigger When deployed Then minutes elapsed
  Target: < 2 min
- deployment_success_rate: Given deployments in period When succeeded Then rate
  Target: > 99%
- rollback_time: Given failure When rolled back Then seconds elapsed
  Target: < 30s
```

## 9. Failure Conditions

```
Failure Conditions:
- Build fails: docker build exit code != 0 (abort, notify)
- Smoke tests fail: health endpoint returns non-200 (rollback)
- Service won't restart: systemctl restart fails (rollback)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If build fails → notify Dev OS, do NOT deploy
2. If smoke test fails → auto-rollback to previous version
3. If service fails to restart → rollback and escalate to Ops OS
4. Log all attempts to state/logs/skills/deploy-code.log
```

## 11. Business Value

```
Business Value: Eliminates manual deployments. Reduces MTTR from 15min to <2min. Estimated 8h/week saved.
```

## 12. Parent OS

```
Parent OS: Dev
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: deployment_started, deployment_completed, deployment_failed, rollback_completed
- Logs: state/logs/skills/deploy-code.log
```
