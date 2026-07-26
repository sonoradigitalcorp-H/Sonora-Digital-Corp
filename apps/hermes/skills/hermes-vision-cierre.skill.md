# hermes-vision-cierre — Hermes Objection Handling & Closing

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-HVC-001

---

## 1. Business Objective

Handle sales objections and guide prospects toward trial commitment using empathy and vision-based framing.

## 2. Inputs (Gherkin)

```gherkin
Given user expresses disinterest or objection
When trigger keywords are detected: "no me interesa", "ya tengo contador", "es muy caro", "lo pienso", "después", "ahorita no", "no necesito", "estoy bien así", "no sé si sirva"
```

## 3. Outputs (Gherkin)

```gherkin
Then objection is acknowledged with empathy
And future-vision comparison is presented
And free trial offer is extended without pressure
```

## 4. Events

```
Events:
- hermes:vision-cierre:executed: objection handling completed
```

## 5. Dependencies

```
Dependencies:
- LLM: empathetic objection handling
- Product knowledge: trial offer details
```

## 6. Tools

```
Tools:
- llm_chat: compose objection response with vision framing
```

## 7. Policies

```
Policies:
- Objections must be acknowledged before countering
- Pressure tactics must never be used
- Trial offer must be no-commitment (no credit card)
- User choice must be respected without follow-up spam
```

## 8. Success Metrics

```gherkin
Success Metrics:
- objection_rate: Given objections in period When handled Then percentage with positive outcome
  Target: > 25%
- trial_conversion: Given objection handled When trial accepted Then percentage
  Target: > 10%
```

## 9. Failure Conditions

```
Failure Conditions:
- Pushy tone: user perceives pressure (flag for review)
- Objection not addressed: generic response misses specific concern
- User blocked: repeated attempts after clear rejection
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If pushy tone detected → rephrase with more empathy
2. If objection not addressed → ask clarifying question to understand specific concern
3. If user blocks → cease contact, log as unqualified
4. Log all attempts to state/logs/skills/hermes-vision-cierre.log
```

## 11. Business Value

```
Business Value: Recovers 25% of lost opportunities through structured objection handling without human intervention.
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
- Events: hermes:vision-cierre:executed
- Logs: state/logs/skills/hermes-vision-cierre.log
```
