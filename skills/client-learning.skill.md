# Skill — Client Learning Loop

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-CLIENT-LEARNING-001

---

Every skill definition must include all 14 fields below. A skill is not valid unless all fields are complete.

---

## 1. Business Objective

Every client interaction improves the system for all clients. When a client asks something, the system learns from it and gets smarter for the next client.

```
Business Objective: Increase system intelligence per-interaction by 0.1% by capturing every client message, detecting cross-client patterns, and generating actionable niche insights.
```

---

## 2. Inputs (Gherkin)

```gherkin
Given a client sends a message via WhatsApp, Telegram, or API
And a ClientStore is available at memory/clients/{client_id}/
When the interaction is recorded
```

---

## 3. Outputs (Gherkin)

```gherkin
Then the interaction is saved to interactions.jsonl
And the client profile is updated with new totals and satisfaction
And cross-client patterns are re-evaluated
And niche insights are refreshed
```

---

## 4. Events

```
Events:
- client:interaction: fired when any client interaction is recorded
- client:updated: fired when a client profile is updated
- client:pattern:detected: fired when a new cross-client pattern emerges
```

---

## 5. Dependencies

```
Dependencies:
- memory/client_store.py: data (ClientStore interface)
- evolution/client_learner.py: service (ClientLearner analysis)
- state/events/events.jsonl: data (event log)
```

---

## 6. Tools

```
Tools:
- ClientStore: read/write per-client YAML/JSONL files
- ClientLearner: analyze clients, niches, and cross-client patterns
- Client API (/clients): HTTP interface exposing learning data
```

---

## 7. Policies

```
Policies:
- No PII is included in cross-client patterns (aggregated only)
- Client data is never shared between tenants
- Deactivated clients are excluded from niche statistics
```

---

## 8. Success Metrics

```
Success Metrics:
- Pattern detection rate: Given 10 clients with similar behavior, When analyze_all is called, Then at least 1 cross-client pattern is found
  Target: 100% of runs with >=3 clients in same niche
- Client analysis: Given a client with >=1 interaction, When analyze_client is called, Then total_interactions>0 and success_rate is computed
  Target: 100%
```

---

## 9. Failure Conditions

```
Failure Conditions:
- Corrupted profile YAML: detection via yaml.safe_load exception → recovery via _ensure_profile
- Missing client directory: auto-created on first save_interaction
- Empty interactions.jsonl: handled gracefully (returns [])
```

---

## 10. Recovery Procedure

```
Recovery Procedure:
1. If profile.yaml is corrupted, call _ensure_profile to recreate with defaults
2. If interactions.jsonl has malformed lines, skip them and process valid ones
3. If client directory is missing, it is created on first write
```

---

## 11. Business Value

```
Business Value: Each client interaction increases system intelligence. After 100 clients, the system can predict niche service preferences with 80%+ accuracy, reducing onboarding friction and increasing conversion.
```

---

## 12. Parent OS

```
Parent OS: Support-OS
```

---

## 13. Version

```
Version: 1.0.0
```

---

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: client:interaction, client:updated, client:pattern:detected
- Logs: state/events/events.jsonl
```

---

## Validation Checklist

- [x] Business objective is quantified
- [x] Inputs are defined in Gherkin
- [x] Outputs are defined in Gherkin
- [x] All events are registered in event catalog
- [x] Dependencies are documented
- [x] Tools are listed
- [x] Policies are enforceable
- [x] Success metrics have targets
- [x] Failure conditions are detectable
- [x] Recovery procedure exists
- [x] Business value is quantified
- [x] Parent OS is specified
- [x] Version is set
- [x] Audit trail is documented
