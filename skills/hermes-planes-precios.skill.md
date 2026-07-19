# hermes-planes-precios — Hermes Plans & Pricing

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-HPP-001

---

## 1. Business Objective

Present Hermes subscription plans and pricing to prospects with clear plan comparison and CTA.

## 2. Inputs (Gherkin)

```gherkin
Given user asks about pricing or plans
When trigger keywords are detected: "cuanto cuesta", "precio", "planes", "paquetes", "tarifa hermes", "contratar hermes", "suscripcion hermes"
```

## 3. Outputs (Gherkin)

```gherkin
Then pricing table is presented with all plan tiers
And plan features are listed per tier
And CTA for demo or free trial is included
```

## 4. Events

```
Events:
- hermes:planes-precios:executed: pricing information delivered
```

## 5. Dependencies

```
Dependencies:
- Pricing data: current plan prices and features
- Product catalog: feature-per-tier mapping
```

## 6. Tools

```
Tools:
- llm_chat: format and deliver pricing response
```

## 7. Policies

```
Policies:
- Pricing must reflect current active plans
- All tiers must be shown with clear price anchors
- Features differentiating tiers must be explicit
- CTA must be included in every pricing response
- Prices must be in Mexican pesos (MXN)
```

## 8. Success Metrics

```gherkin
Success Metrics:
- response_time: Given price query When answered Then seconds
  Target: < 3 s
- conversion_rate: Given pricing viewed When prospect takes next step Then percentage
  Target: > 15%
```

## 9. Failure Conditions

```
Failure Conditions:
- Pricing outdated: displayed prices do not match current billing
- Missing tier: a plan is omitted from the response
- Format broken: markdown table renders incorrectly in Telegram
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If outdated → verify against billing system, update static response
2. If missing tier → check catalog completeness, regenerate
3. If format broken → restructure as plain text list
4. Log all attempts to state/logs/skills/hermes-planes-precios.log
```

## 11. Business Value

```
Business Value: Automated pricing transparency eliminates sales friction and speeds up purchase decisions.
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
- Events: hermes:planes-precios:executed
- Logs: state/logs/skills/hermes-planes-precios.log
```
