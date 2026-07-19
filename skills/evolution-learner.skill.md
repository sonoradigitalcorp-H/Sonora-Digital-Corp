# evolution-learner — Automatic Session Scoring & Learning

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-EL-001

---

## 1. Business Objective

Automatically score and learn from every interaction to continuously improve the system.

## 2. Inputs (Gherkin)

```gherkin
Given sessions exist in the Session Store
When sessions have not been scored yet
And the Learner Engine is invoked
```

## 3. Outputs (Gherkin)

```gherkin
Then all unscored sessions receive a score (0-10)
And learning metrics are extracted and aggregated
And a report is generated in the requested format
And an improvement tip is provided when patterns exist
```

## 4. Events

```
Events:
- evolution:sessions:scored: fired when batch scoring completes (count of sessions scored)
- evolution:report:generated: fired when a learning report is generated
- evolution:improvement:tip: fired when an improvement tip is available
```

## 5. Dependencies

```
Dependencies:
- Session Store: state/sessions.jsonl (session data source)
- Enterprise Score: metrics/enterprise_score.py (system-level scoring context)
```

## 6. Tools

```
Tools:
- Learner class: evolution/learner.py (core scoring and metrics engine)
- SessionStore: evolution/learner.py (file-based session persistence)
- enterprise_score: metrics/enterprise_score.py (system health context)
```

## 7. Policies

```
Policies:
- Every session must have a unique id before scoring
- Scores are immutable once written (no re-scoring)
- Session data must never contain secrets or PII
- Improvement tips must be data-driven, not hardcoded
- All metrics must be derivable from scored session data
```

## 8. Success Metrics

```gherkin
Success Metrics:
- scoring_throughput: Given batch of N unscored sessions When scored Then N sessions processed
  Target: all pending sessions scored in a single pass
- metrics_accuracy: Given known session outcomes When metrics extracted Then rates match expectations
  Target: 100% match with manually verified test sessions
- report_generation: Given metrics When formatted Then valid output in requested format
  Target: < 100ms generation time
```

## 9. Failure Conditions

```
Failure Conditions:
- Session Store empty: no sessions to score (not a failure, empty state)
- Session data corrupt: JSON parse error on session line (skip and log)
- Invalid session: missing required fields (score reduced to minimum)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If session file is missing → create empty file, report 0 sessions
2. If corrupt line in sessions.jsonl → skip corrupted line, continue processing
3. If scoring throws unexpected error → log error, continue with next session
4. Report failures in state/logs/skills/evolution-learner.log
```

## 11. Business Value

```
Business Value: Continuous system improvement through automatic measurement. Every interaction generates actionable insight. Reduces manual analysis by 100%.
```

## 12. Parent OS

```
Parent OS: Evolution
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: evolution:sessions:scored, evolution:report:generated, evolution:improvement:tip
- Logs: state/logs/skills/evolution-learner.log
```
