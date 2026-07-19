# whatsapp-onboarding — WhatsApp Onboarding Skill

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-WA-ONB-001

---

## 1. Business Objective

```
Business Objective: Convert incoming WhatsApp messages into fully onboarded clients without human intervention.
```

---

## 2. Inputs (Gherkin)

```gherkin
Given a WhatsApp message arrives from an unknown number
And the webhook emits "whatsapp:message:received"
And the message contains a valid onboarding code or onboarding intent
When the onboarding agent processes the message
```

---

## 3. Outputs (Gherkin)

```gherkin
Then the client is associated with a tenant
And the onboarding flow begins in 5 steps
And Engram + Qdrant + Neo4j records are created
And a welcome message is sent via WhatsApp
```

---

## 4. Events

```
Events:
- whatsapp:message:received: incoming message detected
- onboarding:started: new client begins onboarding
- onboarding:completed: client finishes 5-step flow
- whatsapp:message:sent: welcome message delivered
```

---

## 5. Dependencies

```
Dependencies:
- wacli_mcp: WhatsApp messaging (service)
- onboarding_mcp: code generation and validation (service)
- engram_mcp: memory persistence (service)
- state/whatsapp/catalog.json: service catalog (data)
```

---

## 6. Tools

```
Tools:
- whatsapp_send_text: send onboarding messages
- onboarding_generate: create activation code
- onboarding_validate: validate code and activate tenant
- onboarding_flow_step: get message for each step
```

---

## 7. Policies

```
Policies:
- Never send spam or unsolicited messages
- Always ask for consent before storing personal data
- If code is invalid or expired, respond with clear instructions
- Limit onboarding flow to 5 steps maximum
- Record every interaction in the event bus
```

---

## 8. Success Metrics

```gherkin
Success Metrics:
- onboarding_time: Given message received When completed Then minutes
  Target: < 5 min
- completion_rate: Given clients who start onboarding When complete Then rate
  Target: > 70%
- response_time: Given message received When first reply sent Then seconds
  Target: < 10s
```

---

## 9. Failure Conditions

```
Failure Conditions:
- Invalid onboarding code: respond with retry instructions
- Expired code (>6h): request new code
- wacli not authenticated: queue message and alert
- Duplicate phone: route to existing tenant
```

---

## 10. Recovery Procedure

```
Recovery Procedure:
1. If code invalid → send example and ask partner
2. If expired → generate new code via onboarding_mcp
3. If wacli down → queue in SQLite retry table
4. Log all failures to state/logs/whatsapp-onboarding.log
```

---

## 11. Business Value

```
Business Value: Automates 100% of inbound onboarding. Estimated 5h/week saved per 50 clients.
```

---

## 12. Parent OS

```
Parent OS: Support
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
- ADR: ADR-20260719-WHATSAPP-OS-FASE1
- Events: whatsapp:message:received, onboarding:started, onboarding:completed, whatsapp:message:sent
- Logs: state/logs/whatsapp-onboarding.log
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
