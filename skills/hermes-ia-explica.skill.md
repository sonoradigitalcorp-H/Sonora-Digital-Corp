# hermes-ia-explica — Hermes AI Explainer

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-HIE-001

---

## 1. Business Objective

Explain AI, automation, and technology concepts in simple language for non-technical business owners.

## 2. Inputs (Gherkin)

```gherkin
Given user asks about AI or automation concepts
When trigger keywords are detected: "qué es ia", "inteligencia artificial", "automatizar", "cómo funciona hermes", "n8n", "workflow"
```

## 3. Outputs (Gherkin)

```gherkin
Then concept is explained with everyday analogies
And practical benefit for Mexican SMEs is highlighted
And technical jargon is minimized or defined
```

## 4. Events

```
Events:
- hermes:ia-explica:executed: concept explanation delivered
```

## 5. Dependencies

```
Dependencies:
- LLM: technology educator prompt
- Business context: Mexican SME pain points
```

## 6. Tools

```
Tools:
- llm_complete: execute explainer prompt with user message
```

## 7. Policies

```
Policies:
- Explanations must use analogies to everyday business situations
- Technical terms must be followed by plain-language definition
- Every explanation must include practical SME benefit
- Examples must reference Mexican business context
```

## 8. Success Metrics

```gherkin
Success Metrics:
- explanation_time: Given question When answered Then seconds
  Target: < 10 s
- comprehension_rate: Given explanations in period When followed by positive reaction Then percentage
  Target: > 80%
```

## 9. Failure Conditions

```
Failure Conditions:
- Over-technical: LLM uses jargon despite prompt guardrails
- Off-topic: response does not connect to practical benefit
- Length: explanation exceeds Telegram message limit
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If over-technical → re-prompt with simpler language instruction
2. If off-topic → re-focus on Mexican SME practical benefit
3. If too long → truncate, offer to elaborate on specific point
4. Log all attempts to state/logs/skills/hermes-ia-explica.log
```

## 11. Business Value

```
Business Value: Democratizes AI understanding for non-technical business owners, reducing adoption friction.
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
- Events: hermes:ia-explica:executed
- Logs: state/logs/skills/hermes-ia-explica.log
```
