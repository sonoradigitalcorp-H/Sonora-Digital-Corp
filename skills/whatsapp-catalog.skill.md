# whatsapp-catalog — WhatsApp Catalog Skill

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-WA-CAT-001

---

## 1. Business Objective

```
Business Objective: Allow clients to browse and request services via WhatsApp using the catalog.
```

---

## 2. Inputs (Gherkin)

```gherkin
Given a client sends a WhatsApp message
And the text contains catalog keywords (catálogo, servicios, productos, planes)
When the webhook emits "whatsapp:catalog:requested"
```

---

## 3. Outputs (Gherkin)

```gherkin
Then the catalog is formatted as a WhatsApp-friendly message
And the response is sent to the client
And the requested item is logged for sales follow-up
```

---

## 4. Events

```
Events:
- whatsapp:catalog:requested: client asks for catalog
- whatsapp:message:sent: catalog response delivered
- sales:lead:qualified: item of interest identified
```

---

## 5. Dependencies

```
Dependencies:
- state/whatsapp/catalog.json: service catalog (data)
- wacli_mcp: WhatsApp messaging (service)
- sales-agent: lead qualification (agent)
```

---

## 6. Tools

```
Tools:
- whatsapp_send_text: send catalog message
- whatsapp_create_wa_me_link: generate links for specific items
- whatsapp_send_file: send catalog PDF/image if needed
```

---

## 7. Policies

```
Policies:
- Always respond within 10 seconds
- Include prices in MXN and tokens
- Show delivery times and revision counts
- Never promise unavailable services
- Track which item the client clicked/requested
```

---

## 8. Success Metrics

```gherkin
Success Metrics:
- catalog_response_time: Given request When response sent Then seconds
  Target: < 10s
- conversion_rate: Given catalog sent When service purchased Then rate
  Target: > 15%
- clarity_score: Given catalog message When client asks no follow-up price questions Then rate
  Target: > 80%
```

---

## 9. Failure Conditions

```
Failure Conditions:
- catalog.json missing or invalid: send apology and escalate
- wacli not authenticated: queue response
- Client asks for service not in catalog: suggest closest alternatives
```

---

## 10. Recovery Procedure

```
Recovery Procedure:
1. If catalog file missing → load default backup
2. If wacli down → queue response in SQLite
3. If unknown item → ask clarifying question
4. Log all requests to state/logs/whatsapp-catalog.log
```

---

## 11. Business Value

```
Business Value: Turns WhatsApp into a 24/7 sales channel. Estimated 20% increase in qualified leads.
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
- ADR: ADR-20260719-WHATSAPP-OS-FASE1
- Events: whatsapp:catalog:requested, whatsapp:message:sent, sales:lead:qualified
- Logs: state/logs/whatsapp-catalog.log
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
