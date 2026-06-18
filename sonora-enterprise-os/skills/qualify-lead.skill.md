# qualify-lead — Lead Scoring & Qualification

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-QL-001

---

## 1. Business Objective

Automatically score and qualify incoming leads by fit and intent, reducing manual triage time to zero.

## 2. Inputs (Gherkin)

```gherkin
Given a lead_received event with contact data
When contact has email AND source is valid
And contact is not in suppression list
```

## 3. Outputs (Gherkin)

```gherkin
Then lead scored with fit_score (0-100) AND intent_score (0-100)
And if combined_score >= 80 then lead_qualified event fires
And if combined_score < 80 then lead_disqualified event fires
```

## 4. Events

```
Events:
- lead_qualified: fired when score >= 80
- lead_disqualified: fired when score < 80
```

## 5. Dependencies

```
Dependencies:
- Contact data: from lead_received event payload
- Scoring model: built-in rule-based (configurable)
```

## 6. Tools

```
Tools:
- scoring-engine: built-in Python logic in skill
- suppression-list: state/suppression-list.json
```

## 7. Policies

```
Policies:
- No lead may be qualified without valid email
- Disqualified leads must include reason in event payload
- Scoring thresholds are configurable via state/scoring-config.json
```

## 8. Success Metrics

```gherkin
Success Metrics:
- lead_qualification_time: Given lead_received When qualified Then seconds elapsed
  Target: < 5 seconds
- qualification_accuracy: Given qualified leads When converted Then rate = converted/qualified
  Target: > 30%
```

## 9. Failure Conditions

```
Failure Conditions:
- Missing email: lead automatically disqualified with reason "missing_email"
- Invalid source: lead automatically disqualified with reason "invalid_source"
- Scoring timeout: if scoring takes > 10s, fall back to manual queue
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If scoring fails → log error, move lead to manual_review queue
2. If suppression list unavailable → proceed without suppression, flag for review
3. Retry up to 3 times with exponential backoff
```

## 11. Business Value

```
Business Value: Eliminates manual lead triage. Estimated 10h/week saved at current volume.
```

## 12. Parent OS

```
Parent OS: Sales
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: lead_received → lead_qualified | lead_disqualified
- Logs: state/logs/skills/qualify-lead.log
```
