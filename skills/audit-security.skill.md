# audit-security — Security Audit & Compliance

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-SEC-001

---

## 1. Business Objective

Detect and remediate security vulnerabilities within 24 hours of introduction.

## 2. Inputs (Gherkin)

```gherkin
Given code is committed or deployed
When automated security scan completes
And vulnerability database is available
```

## 3. Outputs (Gherkin)

```gherkin
Then code is scanned for known vulnerabilities
And dependency tree is audited
And secrets are detected in code
And security_scan_completed event fires
And if vulnerabilities found, vulnerability_detected event fires with details
```

## 4. Events

```
Events:
- security_scan_completed: scan finished successfully
- vulnerability_detected: vulnerability found with severity
- secrets_exposed: potential secret or key in code
- compliance_check_passed: regulatory compliance verified
```

## 5. Dependencies

```
Dependencies:
- Git: access to codebase for scanning
- Vulnerability DB: CVE database access
- .gitignore: secrets exclusion rules
```

## 6. Tools

```
Tools:
- git: log scanning and diff analysis
- python3: pattern matching for secrets detection
- bash: dependency audit scripts
```

## 7. Policies

```
Policies:
- Every commit is scanned before merge
- CRITICAL vulnerabilities block deployment
- Secrets must be revoked immediately on detection
- Compliance checks run weekly
- No secrets may be logged or stored in plain text
```

## 8. Success Metrics

```gherkin
Success Metrics:
- detection_time: Given vulnerability introduced When detected Then hours
  Target: < 1h
- remediation_time: Given vulnerability detected When fixed Then hours
  Target: < 24h for CRITICAL, < 7d for HIGH
- false_positive_rate: Given detections When confirmed Then false rate
  Target: < 5%
```

## 9. Failure Conditions

```
Failure Conditions:
- Scan timeout: dependency audit takes > 10 min (split, retry)
- Vulnerability DB stale: last update > 24h (alert, use cache)
- Permission denied: cannot access repo (escalate to Ops OS)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If scan times out → split into smaller batches, retry
2. If DB stale → use last known data, flag as potentially incomplete
3. If permission denied → verify SSH keys, retry, escalate if persists
4. Log all attempts to state/logs/skills/audit-security.log
```

## 11. Business Value

```
Business Value: Proactive vulnerability detection. Prevents security incidents. Estimated $50k/year in avoided breach costs.
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
- Events: security_scan_completed, vulnerability_detected, secrets_exposed, compliance_check_passed
- Logs: state/logs/skills/audit-security.log
```
