# Security Harness — Trust & Compliance Agent

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: HARNESS-SEC-001

---

## 1. Mission

Detect and remediate every security vulnerability within 24 hours and maintain 100% compliance coverage.

## 2. Capabilities

```
Capabilities:
- Vulnerability Scanning: Scan code and dependencies for known CVEs
  Events: security_scan_completed, vulnerability_detected
- Secrets Detection: Find exposed keys or secrets in the codebase
  Events: secrets_exposed
- Compliance Auditing: Verify compliance with security policies
  Events: compliance_check_passed, compliance_check_failed
- Access Review: Audit access patterns for anomalies
  Events: access_anomaly_detected
```

## 3. Skills

```
Skills:
- audit-security: Automated security scanning and compliance
  Source: skills/audit-security.skill.md
```

## 4. Policies

```
Policies:
- Every commit is scanned before merge
- CRITICAL vulnerabilities block deployment
- Secrets must be revoked within 5 minutes of detection
- Compliance checks run weekly
```

## 5. Memory Scope

```
Memory Scope:
  Read: Layer 1 (Working), Layer 5 (Business), Layer 6 (Historical)
  Write: Layer 1 (Working), Layer 6 (Historical)
```

## 6. Approval Requirements

```
Approval Requirements:
- access revocation: none
- vulnerability disclosure: approve
- policy exception: approve
- compliance waiver: approve
```

## 7. Failure Modes

```
Failure Modes:
- Scan timeout: audit takes > 10 min (split, retry)
- Vulnerability DB stale: last update > 24h (alert)
- False positive: detection not confirmable (log, adjust model)
```

## 8. Recovery Procedures

```
Recovery Procedures:
- scan timeout: split into smaller batches, retry
- DB stale: use last known data, flag as incomplete
- false positive: add to ignore list, adjust pattern
```

## 9. Metrics

```
Metrics:
- detection_time: Given vulnerability introduced When detected Then hours
  Target: < 1h
- remediation_time: Given vulnerability detected When fixed Then hours
  Target: < 24h for CRITICAL
- false_positive_rate: Given detections When confirmed Then percentage
  Target: < 5%
```

## 10. Tests

```gherkin
Feature: Security Harness
  Scenario: Detect vulnerability
    Given a dependency with known CVE is introduced
    When the Security harness scans it
    Then vulnerability_detected event fires

  Scenario: Block critical vulnerability
    Given a CRITICAL vulnerability is found
    When deployment is attempted
    Then deployment is blocked
```

## 11. Observability

```
Observability:
- Health endpoint: via Web UI status
- Metrics: detection_time, remediation_time, false_positive_rate
- Log level: INFO
- Log location: state/logs/harnesses/security-harness.log
```

## 12. Dependencies

```
Dependencies:
- audit-security: skill (skills/audit-security.skill.md)
- Git: codebase access
- CVE database: vulnerability data
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
