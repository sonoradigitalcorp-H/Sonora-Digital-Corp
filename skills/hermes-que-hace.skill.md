# hermes-que-hace — Hermes Capability Overview

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-HQH-001

---

## 1. Business Objective

Provide a comprehensive overview of Hermes capabilities across fiscal, accounting, customs, and AI domains.

## 2. Inputs (Gherkin)

```gherkin
Given user asks what Hermes does
When trigger keywords are detected: "que hace hermes", "para que sirve hermes", "como funciona hermes", "hermes puede", "beneficios de hermes", "hermes vs contador"
```

## 3. Outputs (Gherkin)

```gherkin
Then full capability overview is returned with domains
And comparison with traditional accountant is provided
And CTA for demo is included
```

## 4. Events

```
Events:
- hermes:que-hace:executed: capability overview delivered
```

## 5. Dependencies

```
Dependencies:
- Hermes product catalog: current feature list
- Pricing data: plan comparison
```

## 6. Tools

```
Tools:
- llm_chat: compose capability overview response
```

## 7. Policies

```
Policies:
- Response must cover all Hermes domains: fiscal, accounting, customs, AI
- Comparison must be factual, not disparaging
- CTA must offer demo or free trial
- Response must be within Telegram length limits
```

## 8. Success Metrics

```gherkin
Success Metrics:
- response_time: Given query When answered Then seconds
  Target: < 5 s
- engagement_rate: Given overview sent When user continues conversation Then percentage
  Target: > 50%
```

## 9. Failure Conditions

```
Failure Conditions:
- Information outdated: feature list does not reflect current product
- Too long: response exceeds Telegram message limit
- No CTA: user receives info without next step
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If outdated → verify against current catalog, regenerate
2. If too long → summarize by domain, offer deep dive per domain
3. If no CTA → append demo/trial offer in follow-up
4. Log all attempts to state/logs/skills/hermes-que-hace.log
```

## 11. Business Value

```
Business Value: Instant product education reduces sales cycle by answering common questions automatically.
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
- Events: hermes:que-hace:executed
- Logs: state/logs/skills/hermes-que-hace.log
```
