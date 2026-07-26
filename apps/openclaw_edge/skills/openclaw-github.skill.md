# openclaw-github — OpenClaw GitHub Plugin

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-OCG-001

---

## 1. Business Objective

Manage GitHub repositories, pull requests, and issues via the OpenClaw gateway for automated DevOps workflows.

## 2. Inputs (Gherkin)

```gherkin
Given OpenClaw gateway is running
When a repository operation is requested
Or a PR needs creation, review, or merge
Or an issue needs triage or update
```

## 3. Outputs (Gherkin)

```gherkin
Then repository is created or updated
And PR is opened with description and labels
And issue is created or updated with metadata
```

## 4. Events

```
Events:
- openclaw:github:repo_created: repository initialized
- openclaw:github:pr_opened: pull request created
- openclaw:github:issue_updated: issue modified
```

## 5. Dependencies

```
Dependencies:
- OpenClaw gateway: port 18789
- GitHub token: with repo and org permissions
- GitHub API: REST and GraphQL endpoints
```

## 6. Tools

```
Tools:
- openclaw_execute(github_*): execute GitHub operations (repo, pr, issue, workflow)
```

## 7. Policies

```
Policies:
- All GitHub operations must use short-lived tokens
- PR descriptions must follow conventional commit format
- Repository names must match naming convention
- Destructive operations (delete, force-push) require confirmation
```

## 8. Success Metrics

```gherkin
Success Metrics:
- operation_time: Given GitHub request When completed Then seconds
  Target: < 5 s
- success_rate: Given GitHub operations in period When succeeded Then percentage
  Target: > 98%
```

## 9. Failure Conditions

```
Failure Conditions:
- Auth failure: token expired or insufficient scope (rotate token)
- Rate limit: GitHub API 403 (wait for reset window)
- Gateway error: OpenClaw bridge not responding (restart)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If auth fails → refresh token, verify scopes, retry operation
2. If rate limited → wait for reset, queue operations
3. If gateway error → restart openclaw-gateway, verify GitHub endpoint
4. Log all attempts to state/logs/skills/openclaw-github.log
```

## 11. Business Value

```
Business Value: Automated GitHub operations from any workflow without manual API calls.
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
- Events: openclaw:github:repo_created, openclaw:github:pr_opened, openclaw:github:issue_updated
- Logs: state/logs/skills/openclaw-github.log
```
