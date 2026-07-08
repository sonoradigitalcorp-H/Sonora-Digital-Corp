# Quality Harness — Validation & Testing Agent

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: HARNESS-QTY-001

---

## 1. Mission

Validate every code change against automated quality gates before it reaches production.

## 2. Capabilities

```
Capabilities:
- Test Execution: Run unit, integration, and E2E tests automatically
  Events: test_run_completed, test_run_failed
- Coverage Tracking: Measure and enforce test coverage thresholds
  Events: coverage_report
- Quality Gating: Block releases that fail quality thresholds
  Events: quality_pass, quality_fail
- Enterprise Scoring: Calculate and report enterprise score
  Events: score_updated
```

## 3. Skills

```
Skills:
- validate-quality: Automated quality validation and gating
  Source: skills/validate-quality.skill.md
```

## 4. Policies

```
Policies:
- Every PR must pass all quality gates before merge
- Test coverage must never decrease
- Quality score is recalculated on every release
- Validation must complete in under 5 minutes
```

## 5. Memory Scope

```
Memory Scope:
  Read: Layer 1 (Working), Layer 2 (Task), Layer 3 (Project)
  Write: Layer 1 (Working), Layer 6 (Historical)
```

## 6. Approval Requirements

```
Approval Requirements:
- quality override: approve
- coverage threshold change: approve
- test skip: notify
```

## 7. Failure Modes

```
Failure Modes:
- Test flakiness: non-deterministic failure (retry 3x, flag)
- Coverage drop: new code untested (block, notify)
- Tool failure: runner crashes (escalate)
```

## 8. Recovery Procedures

```
Recovery Procedures:
- test flaky: retry 3x, flag if persists, create issue
- coverage drop: identify uncovered lines, block merge
- tool failure: try alternate tool, escalate if all fail
```

## 9. Metrics

```
Metrics:
- validation_time: Given PR submitted When validated Then minutes
  Target: < 3 min
- pass_rate: Given validations in period When passed Then percentage
  Target: > 90%
- coverage: Given codebase When measured Then percentage
  Target: > 80%
```

## 10. Tests

```gherkin
Feature: Quality Harness
  Scenario: Validate passing PR
    Given a PR passes all quality gates
    When validation completes
    Then quality_pass event fires

  Scenario: Block failing PR
    Given a PR fails tests
    When validation runs
    Then quality_fail event fires
    And merge is blocked
```

## 11. Observability

```
Observability:
- Health endpoint: via Web UI status
- Metrics: validation_time, pass_rate, coverage
- Log level: INFO
- Log location: state/logs/harnesses/quality-harness.log
```

## 12. Dependencies

```
Dependencies:
- validate-quality: skill (skills/validate-quality.skill.md)
- pytest: test framework
- ruff/flake8: linters
- coverage: test coverage tool
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
