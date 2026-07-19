# hermes-auditor — Hermes Security Auditor

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-HAU-001

---

## 1. Business Objective

Perform security audits and dependency analysis for the Hermes project using senior-level security review.

## 2. Inputs (Gherkin)

```gherkin
Given user requests a security audit
When trigger keywords are detected: "auditar", "auditoria", "seguridad", "vulnerabilidades", "dependencias", "audit"
```

## 3. Outputs (Gherkin)

```gherkin
Then security analysis is performed using the senior auditor prompt
And actionable recommendations are returned with severity levels
And findings are logged for compliance tracking
```

## 4. Events

```
Events:
- hermes:auditor:executed: security audit completed
- hermes:auditor:finding: specific vulnerability identified
```

## 5. Dependencies

```
Dependencies:
- LLM: senior security auditor prompt
- Hermes architecture: FastAPI + Next.js + PostgreSQL + Docker
- Engram: finding persistence
```

## 6. Tools

```
Tools:
- llm_complete: execute senior auditor prompt with user context
- engram_save: persist audit findings
```

## 7. Policies

```
Policies:
- Findings must be classified by severity (critical/high/medium/low)
- Critical findings must trigger immediate notification
- Audit results must be logged to compliance trail
- Recommendations must be actionable and prioritized
```

## 8. Success Metrics

```gherkin
Success Metrics:
- audit_time: Given audit request When completed Then minutes
  Target: < 1 min
- finding_coverage: Given attack surface When audited Then percentage covered
  Target: > 90%
```

## 9. Failure Conditions

```
Failure Conditions:
- LLM hallucination: auditor generates incorrect recommendations
- Context missing: insufficient information for meaningful audit
- False positives: non-issues flagged as vulnerabilities
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If LLM hallucination suspected → verify against known security docs
2. If context missing → ask user for specific scope details
3. If false positives → log for model tuning, adjust prompt
4. Log all attempts to state/logs/skills/hermes-auditor.log
```

## 11. Business Value

```
Business Value: On-demand senior security audits without hiring a dedicated security engineer.
```

## 12. Parent OS

```
Parent OS: Knowledge
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: hermes:auditor:executed, hermes:auditor:finding
- Logs: state/logs/skills/hermes-auditor.log
```
