# hermes-consciencia — Hermes SAT Awareness & Regularization

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-HCO-001

---

## 1. Business Objective

Address user concerns about SAT compliance, late filings, and fear of penalties through empathetic education and clear regularization guidance.

## 2. Inputs (Gherkin)

```gherkin
Given user expresses concern about SAT compliance or late declarations
When trigger keywords are detected: "cuánto pierdo", "cuanto me cuesta no tener", "me puede multar", "tengo miedo al sat", "no sé si estoy bien", "estoy al corriente", "me preocupa el sat", "nunca he declarado", "llevo meses sin declarar", "años sin declarar"
```

## 3. Outputs (Gherkin)

```gherkin
Then user is informed about what SAT already knows
And discount timeline for late filing penalties is explained
And regularization offer is extended without judgment
```

## 4. Events

```
Events:
- hermes:consciencia:executed: compliance awareness delivered
- hermes:consciencia:regularization: user enters regularization flow
```

## 5. Dependencies

```
Dependencies:
- SAT knowledge: penalty schedules and discount periods
- Hermes services: regularization and filing capabilities
- LLM: empathetic communication
```

## 6. Tools

```
Tools:
- llm_chat: compose compliance awareness response
- engram_save: persist regularization lead data
```

## 7. Policies

```
Policies:
- Responses must be empathetic, never judgmental
- Penalty information must be legally accurate
- Discount timelines must reflect current SAT regulations
- User must never be pressured into regularization
- Regularization path must be offered as optional next step
```

## 8. Success Metrics

```gherkin
Success Metrics:
- response_time: Given concern When answered Then seconds
  Target: < 5 s
- regularization_rate: Given concerns addressed When user enters flow Then percentage
  Target: > 30%
```

## 9. Failure Conditions

```
Failure Conditions:
- Incorrect penalty info: outdated discount percentages
- Fear escalation: response increases user anxiety instead of calming
- User overwhelm: too much information at once
- Legal liability: advice that could be construed as legal counsel
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If penalty info outdated → verify against current SAT regulations
2. If fear escalates → acknowledge concern, simplify to first step only
3. If user overwhelmed → offer one step at a time, not the full plan
4. If legal concern → disclaim as informational, recommend certified accountant
5. Log all attempts to state/logs/skills/hermes-consciencia.log
```

## 11. Business Value

```
Business Value: Converts compliance anxiety into actionable regularization, capturing high-intent leads.
```

## 12. Parent OS

```
Parent OS: Support
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: hermes:consciencia:executed, hermes:consciencia:regularization
- Logs: state/logs/skills/hermes-consciencia.log
```
