# Dev Harness — Software Delivery Agent

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: HARNESS-DEV-001

---

## 1. Mission

Deliver working software to production every day with zero manual deployment steps.

## 2. Capabilities

```
Capabilities:
- Code Deployment: Build, test, and deploy code automatically
  Events: deployment_started, deployment_completed, deployment_failed
- Feature Management: Track features from spec to production
  Events: feature_created, feature_reviewed, feature_shipped
- Rollback: Revert to previous version on failure
  Events: rollback_completed
```

## 3. Skills

```
Skills:
- deploy-code: Automated code build and deployment pipeline
  Source: skills/deploy-code.skill.md
```

## 4. Policies

```
Policies:
- Every deployment must pass CI checks first
- Staging must verify before production promotion
- Rollback must be tested weekly
- Feature flags must be used for risky changes
```

## 5. Memory Scope

```
Memory Scope:
  Read: Layer 1 (Working), Layer 2 (Task), Layer 3 (Project)
  Write: Layer 1 (Working), Layer 3 (Project), Layer 6 (Historical)
```

## 6. Approval Requirements

```
Approval Requirements:
- production deploy: none (auto if CI passes)
- rollback: none (auto on smoke test failure)
- feature flag toggle: notify
- infrastructure change: approve
```

## 7. Failure Modes

```
Failure Modes:
- Build failure: compilation error or test failure (notify, block)
- Smoke test fail: staging health check fails (auto-rollback)
- Deployment timeout: deploy takes > 10 min (investigate, escalate)
```

## 8. Recovery Procedures

```
Recovery Procedures:
- build failure: report error details, block pipeline
- smoke test fail: auto-rollback to last known good version
- deployment timeout: abort deploy, investigate infrastructure
```

## 9. Metrics

```
Metrics:
- deployment_frequency: Given period When deploys completed Then count
  Target: > 1 per day
- lead_time: Given commit When production Then hours
  Target: < 1h
- change_failure_rate: Given deployments When cause incident Then percentage
  Target: < 5%
```

## 10. Tests

```gherkin
Feature: Dev Harness
  Scenario: Deploy code to production
    Given a PR is merged to main
    When CI passes
    Then deployment completes
    And deployment_completed event fires

  Scenario: Rollback on failure
    Given a deployment fails smoke tests
    When auto-rollback triggers
    Then previous version is restored
```

## 11. Observability

```
Observability:
- Health endpoint: via Web UI status
- Metrics: deployment_frequency, lead_time, change_failure_rate
- Log level: INFO
- Log location: state/logs/harnesses/dev-harness.log
```

## 12. Dependencies

```
Dependencies:
- deploy-code: skill (skills/deploy-code.skill.md)
- Git: source code and CI
- Docker: container builds
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
