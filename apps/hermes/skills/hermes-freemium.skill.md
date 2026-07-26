# hermes-freemium — Hermes Freemium Activation

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-HFR-001

---

## 1. Business Objective

Activate free trial accounts with clear expectations of included and excluded features, collecting minimal onboarding data.

## 2. Inputs (Gherkin)

```gherkin
Given user requests free trial or demo access
When trigger keywords are detected: "prueba", "gratis", "trial", "probar", "freemium", "quiero probar", "sin costo", "demo gratis", "acceso gratis"
```

## 3. Outputs (Gherkin)

```gherkin
Then trial terms are communicated with feature scope
And user is prompted for onboarding data (name, company, employees, regime)
And trial activation instructions are provided
```

## 4. Events

```
Events:
- hermes:freemium:executed: freemium flow initiated
- hermes:freemium:activated: trial account created
```

## 5. Dependencies

```
Dependencies:
- Hermes billing: trial account provisioning
- User store: prospect data collection
```

## 6. Tools

```
Tools:
- llm_chat: compose trial offer response
- engram_save: store prospect onboarding data
```

## 7. Policies

```
Policies:
- Trial must be no-credit-card for first 7 days
- Included and excluded features must be transparent
- Onboarding data must be collected before activation
- Trial expiry must be communicated upfront
```

## 8. Success Metrics

```gherkin
Success Metrics:
- activation_time: Given trial request When activated Then minutes
  Target: < 5 min
- trial_to_paid: Given trials started When converted Then percentage
  Target: > 20%
```

## 9. Failure Conditions

```
Failure Conditions:
- Activation failure: provisioning system error
- Data incomplete: insufficient onboarding info to activate
- Duplicate: user already has active trial
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If activation fails → retry provisioning, escalate if persists
2. If data incomplete → ask specific missing fields only
3. If duplicate → remind user of existing trial, offer upgrade path
4. Log all attempts to state/logs/skills/hermes-freemium.log
```

## 11. Business Value

```
Business Value: Self-serve trial activation in under 5 minutes eliminates sales barrier to product evaluation.
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
- Events: hermes:freemium:executed, hermes:freemium:activated
- Logs: state/logs/skills/hermes-freemium.log
```
