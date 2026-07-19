# skills/deploy — Application Deployment and Infrastructure

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-DPL-001

---

## 1. Business Objective

Deploy applications to production in under 2 minutes — configuring nginx, SSL certificates, systemd services, and DNS — with zero-downtime rollouts and rollback capability.

## 2. Inputs (Gherkin)

```gherkin
Given a deployable artifact exists (built app, Docker image, or source)
And a target host is reachable via SSH
When the deploy pipeline is triggered with deployment configuration
```

## 3. Outputs (Gherkin)

```gherkin
Then the application is deployed to the target host
And nginx reverse proxy is configured with SSL termination
And a systemd service is created and enabled
And the deployment is verified with HTTP 200 health check
And the deploy record is saved to Engram
```

## 4. Events

```
Events:
- deploy:started: a deployment began
- deploy:completed: deployment finished successfully
- deploy:failed: deployment encountered an error
- deploy:rolled_back: a failed deployment was rolled back
```

## 5. Dependencies

```
Dependencies:
- SSH access: service — remote host connectivity
- Nginx: service — reverse proxy and SSL termination
- Docker: service — container management
- Systemd: service — service lifecycle management
- Let's Encrypt: service — SSL certificate provisioning
- Engram: service — deployment registry
```

## 6. Tools

```
Tools:
- bash: execute deployment commands
- scp: transfer artifacts to target host
- docker: build, push, and run containers
- systemctl: manage systemd services
```

## 7. Policies

```
Policies:
- SSL certificates must be provisioned before serving HTTPS
- Health checks must pass (HTTP 200 within 30s) before marking complete
- Rollback must be possible within 60 seconds of failed deployment
- No deployment during blackout windows (configured per tenant)
- All secrets must be injected via environment, never in source
```

## 8. Success Metrics

```gherkin
Success Metrics:
- deploy_time: Given deploy triggered When verified Then total seconds
  Target: < 120 sec
- rollback_time: Given deploy failed When rollback initiated Then seconds to restore
  Target: < 60 sec
- success_rate: Given deployments in period When completed Then success rate
  Target: > 99%
```

## 9. Failure Conditions

```
Failure Conditions:
- SSH timeout: connection to host fails (detect via 10s timeout)
- Nginx config error: invalid syntax (detect via nginx -t exit code)
- SSL provisioning failure: certbot fails (detect via non-zero exit)
- Service failed to start: systemd reports failed status (detect via systemctl status)
- Health check fails: HTTP non-200 response (detect via curl exit code)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If health check fails → immediately trigger rollback to previous version
2. If SSH fails → retry 3x with 5s backoff, escalate to Ops OS
3. If nginx config invalid → restore previous config, reload
4. If SSL fails → deploy with HTTP-only, flag for manual SSL setup
5. If service fails → check journalctl logs, fix config, restart
6. Log all attempts to state/logs/skills/deploy.log
```

## 11. Business Value

```
Business Value: Deployments in under 2 minutes. Estimated 8h/week saved.
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
- ADR: ADR-2026-DPL-001
- Events: deploy:started, deploy:completed, deploy:failed, deploy:rolled_back
- Logs: state/logs/skills/deploy.log
```
