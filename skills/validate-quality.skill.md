# validate-quality — Automated Quality Validation

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-QTY-001

---

## 1. Business Objective

Automatically validate every code change against quality gates before it reaches production.

## 2. Inputs (Gherkin)

```gherkin
Given code change is ready for review
When all automated tests have run
And quality gates are configured
```

## 3. Outputs (Gherkin)

```gherkin
Then code passes linting and type checking
And unit tests pass with > 80% coverage
And integration tests pass
And if all gates pass, quality_pass event fires
And if any gate fails, quality_fail event fires with details
```

## 4. Events

```
Events:
- quality_pass: all validation gates passed
- quality_fail: one or more gates failed
- coverage_report: test coverage snapshot generated
- score_updated: enterprise score recalculated
```

## 5. Dependencies

```
Dependencies:
- Test framework: pytest, ruff, flake8
- Codebase: access to source code
- Coverage tool: coverage reporting
```

## 6. Tools

```
Tools:
- pytest: unit and integration tests
- ruff: linting and formatting
- flake8: style guide enforcement
- coverage: test coverage measurement
```

## 7. Policies

```
Policies:
- Every PR must pass all quality gates before merge
- Test coverage must never decrease
- Linting failures must be fixed, not suppressed
- Quality score must be recalculated on every release
- Validation must complete in under 5 minutes
```

## 8. Success Metrics

```gherkin
Success Metrics:
- validation_time: Given PR submitted When validated Then minutes
  Target: < 3 min
- pass_rate: Given validations in period When passed Then rate
  Target: > 90%
- coverage: Given codebase When measured Then coverage percentage
  Target: > 80%
```

## 9. Failure Conditions

```
Failure Conditions:
- Test flakiness: non-deterministic test failure (retry 3x, investigate if persists)
- Coverage drop: new code without tests (block merge, require tests)
- Tool failure: test runner crashes (escalate to Dev OS)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If test flaky → retry 3 times, if persists → flag as flaky, skip, create issue
2. If coverage drops → identify uncovered lines, block merge, notify author
3. If tool fails → try alternate tool, escalate if all fail
4. Log all attempts to state/logs/skills/validate-quality.log
```

## 11. Business Value

```
Business Value: Eliminates manual code review overhead. Prevents regressions. Estimated 10h/week saved.
```

## 12. Parent OS

```
Parent OS: Quality
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: quality_pass, quality_fail, coverage_report, score_updated
- Logs: state/logs/skills/validate-quality.log
```
