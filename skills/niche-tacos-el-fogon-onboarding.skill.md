# niche-tacos-el-fogon-onboarding — Tacos El Fogon Onboarding Skill

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-NICHE-restaurante-ONB-001

---

## 1. Business Objective

```
Business Objective: Convert incoming WhatsApp leads into onboarded Tacos El Fogon clients without human intervention.
```

---

## 2. Inputs (Gherkin)

```gherkin
Given a WhatsApp message arrives from an unknown number
And the webhook emits "niche:restaurante:message:received"
And the message contains keywords: menú, reserva, restaurante
When the restaurante onboarding agent processes the message
```

---

## 3. Outputs (Gherkin)

```gherkin
Then the client receives a welcome message with Tacos El Fogon services
And the niche catalog is shared via WhatsApp
And a lead record is created in the CRM
And the client can request any of: Menú digital, Promociones, Reservaciones
```

---

## 4. Events

```
Events:
- niche:restaurante:message:received: incoming message detected
- niche:restaurante:onboarding:started: new client begins onboarding
- niche:restaurante:onboarding:completed: client finishes onboarding
- niche:restaurante:catalog:sent: catalog delivered via WhatsApp
```

---

## 5. Dependencies

```
Dependencies:
- wacli_mcp: WhatsApp messaging (service)
- state/niches/tacos-el-fogon/catalog.json: service catalog (data)
- state/niches/tacos-el-fogon/pricing.json: pricing data (data)
- engram_mcp: memory persistence (service)
```

---

## 6. Tools

```
Tools:
- whatsapp_send_text: send onboarding welcome
- whatsapp_send_catalog: share niche catalog
- whatsapp_create_wa_me_link: generate wa.me links for services
- lead_capture: register lead in CRM
```

---

## 7. Policies

```
Policies:
- Never send spam or unsolicited messages
- Always respond within 10 seconds
- Include prices in MXN
- Track every interaction in the event bus
- Escalate to human if client asks 3+ clarifying questions
```

---

## 8. Success Metrics

```gherkin
Success Metrics:
- onboarding_time: Given message received When completed Then minutes
  Target: < 3 min
- catalog_click_rate: Given catalog sent When client selects service Then rate
  Target: > 40%
- response_time: Given message received When first reply sent Then seconds
  Target: < 10s
```

---

## 9. Failure Conditions

```
Failure Conditions:
- Catalog file missing: respond with generic message and escalate
- wacli not authenticated: queue message and retry
- Client requests unavailable service: suggest alternatives
- Duplicate phone: route to existing tenant
```

---

## 10. Recovery Procedure

```
Recovery Procedure:
1. If catalog missing → load default restaurante backup
2. If wacli down → queue in SQLite retry table
3. If unknown request → ask clarifying question
4. Log all failures to state/logs/niche-tacos-el-fogon-onboarding.log
```

---

## 11. Business Value

```
Business Value: Automates 100% of Tacos El Fogon inbound onboarding via WhatsApp. Estimated 10h/week saved per niche.
```

---

## 12. Parent OS

```
Parent OS: Sales
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
- ADR: ADR-20260719-NICHE-restaurante
- Events: niche:restaurante:message:received, niche:restaurante:onboarding:started, niche:restaurante:onboarding:completed, niche:restaurante:catalog:sent
- Logs: state/logs/niche-tacos-el-fogon-onboarding.log
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
