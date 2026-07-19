# hermes-mystic-info — Hermes & Mystic Partnership

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-HMI-001

---

## 1. Business Objective

Explain the relationship between Hermes and Mystic AI, positioning the combined value proposition for enterprise prospects.

## 2. Inputs (Gherkin)

```gherkin
Given user asks about Mystic or the Hermes-Mystic relationship
When trigger keywords are detected: "mystic", "que es mystic", "mystic y hermes", "mystic ia", "quien es mystic"
```

## 3. Outputs (Gherkin)

```gherkin
Then Hermes and Mystic roles are explained with distinct value propositions
And combined enterprise offering is positioned
And availability per plan tier is communicated
```

## 4. Events

```
Events:
- hermes:mystic-info:executed: partnership explanation delivered
```

## 5. Dependencies

```
Dependencies:
- Product knowledge: Mystic AI capabilities
- Pricing: enterprise plan details
```

## 6. Tools

```
Tools:
- llm_chat: compose partnership overview response
```

## 7. Policies

```
Policies:
- Both products must be positioned as complementary, not competing
- Mystic must be presented as enterprise-only
- Brand voice must reflect the "shadow" mystique
- Response must include upgrade path for current users
```

## 8. Success Metrics

```gherkin
Success Metrics:
- response_time: Given Mystic query When answered Then seconds
  Target: < 5 s
- upgrade_inquiries: Given info delivered When user asks about enterprise Then percentage
  Target: > 20%
```

## 9. Failure Conditions

```
Failure Conditions:
- Confusing narrative: user unsure of distinction between products
- Missing enterprise context: no upgrade path mentioned
- Tone mismatch: overly mystical without business substance
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If confusing → clarify with concrete examples of each product's role
2. If missing upgrade path → append plan comparison and pricing
3. If tone mismatch → rebalance with practical business benefits
4. Log all attempts to state/logs/skills/hermes-mystic-info.log
```

## 11. Business Value

```
Business Value: Positions combined Hermes + Mystic value for enterprise upsell without human sales intervention.
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
- Events: hermes:mystic-info:executed
- Logs: state/logs/skills/hermes-mystic-info.log
```
