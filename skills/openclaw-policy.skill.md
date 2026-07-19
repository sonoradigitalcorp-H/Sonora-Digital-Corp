# openclaw-policy — OpenClaw Policy Plugin

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-OCP-001

---

## 1. Business Objective

Execute constitution policy checks via the OpenClaw gateway to ensure all actions comply with organizational rules.

## 2. Inputs (Gherkin)

```gherkin
Given OpenClaw gateway is running
When an action requires policy validation
Or a constitution rule needs to be evaluated against a request
```

## 3. Outputs (Gherkin)

```gherkin
Then policy check is executed against the constitution
And pass/fail result is returned with explanation
And violations are logged for audit
```

## 4. Events

```
Events:
- openclaw:policy:checked: policy evaluation completed
- openclaw:policy:violation: action blocked by policy
```

## 5. Dependencies

```
Dependencies:
- OpenClaw gateway: port 18789
- Constitution: YAML policy files in constitution/
- Policy engine: rule evaluation runtime
```

## 6. Tools

```
Tools:
- openclaw_execute(policy_check): evaluate action against constitution policies
```

## 7. Policies

```
Policies:
- All policy evaluations must be logged for audit trail
- Deny-by-default: any unmatched policy results in denial
- Policy overrides require explicit approval from Security OS
- Policy check results must be returned within 5 seconds
```

## 8. Success Metrics

```gherkin
Success Metrics:
- check_time: Given policy request When evaluated Then milliseconds
  Target: < 500 ms
- violation_capture: Given policy violations in period When logged Then percentage
  Target: 100%
```

## 9. Failure Conditions

```
Failure Conditions:
- Engine failure: policy evaluation runtime error (escalate to Security)
- Constitution missing: policy files not found (restore from backup)
- Timeout: check exceeds 10s (fall back to deny-by-default)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If engine fails → restart policy engine, re-evaluate
2. If constitution missing → restore from git, verify integrity
3. If timeout → deny by default, log incident, notify Security OS
4. Log all attempts to state/logs/skills/openclaw-policy.log
```

## 11. Business Value

```
Business Value: Automated constitution compliance for every action without manual review.
```

## 12. Parent OS

```
Parent OS: Security
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: openclaw:policy:checked, openclaw:policy:violation
- Logs: state/logs/skills/openclaw-policy.log
```
