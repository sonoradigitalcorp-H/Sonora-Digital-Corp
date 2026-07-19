# niche-tacos-el-fogon-catalog — Tacos El Fogon Catalog Skill

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-NICHE-restaurante-CAT-001

---

## 1. Business Objective

```
Business Objective: Allow Tacos El Fogon clients to browse and request niche services via WhatsApp using the catalog.
```

---

## 2. Inputs (Gherkin)

```gherkin
Given a client sends a WhatsApp message to the Tacos El Fogon niche
And the text contains catalog triggers: menú, reserva, restaurante
When the niche catalog agent processes the request
```

---

## 3. Outputs (Gherkin)

```gherkin
Then the Tacos El Fogon catalog is formatted as a WhatsApp-friendly message
And the response is sent to the client with service options
And the requested item is logged for sales follow-up
And the client receives a wa.me link to purchase the service
```

---

## 4. Events

```
Events:
- niche:restaurante:catalog:requested: client asks for catalog
- niche:restaurante:service:selected: client picks a service
- niche:restaurante:catalog:sent: catalog delivered
- niche:restaurante:lead:qualified: client intent identified
```

---

## 5. Dependencies

```
Dependencies:
- state/niches/tacos-el-fogon/catalog.json: niche service catalog (data)
- state/niches/tacos-el-fogon/pricing.json: niche pricing (data)
- wacli_mcp: WhatsApp messaging (service)
- sales-agent: lead qualification (agent)
```

---

## 6. Tools

```
Tools:
- whatsapp_send_text: send catalog message
- whatsapp_send_file: send catalog image/PDF
- whatsapp_create_wa_me_link: generate purchase links
- catalog_filter: filter services by client need
```

---

## 7. Policies

```
Policies:
- Always respond within 10 seconds
- Always include prices in MXN and token costs
- Show delivery times per service
- Never promise unavailable services
- Track which service the client selected
```

---

## 8. Success Metrics

```gherkin
Success Metrics:
- catalog_response_time: Given request When response sent Then seconds
  Target: < 10s
- conversion_rate: Given catalog sent When service purchased Then rate
  Target: > 20%
- satisfaction_score: Given purchase completed When no complaints Then rate
  Target: > 90%
```

---

## 9. Failure Conditions

```
Failure Conditions:
- Catalog file missing: send apology and escalate to support
- wacli not authenticated: queue and retry
- Client asks for service not in niche catalog: suggest similar options
```

---

## 10. Recovery Procedure

```
Recovery Procedure:
1. If catalog missing → load default restaurante backup from templates
2. If wacli down → queue response in SQLite retry table
3. If unknown service → ask clarifying question
4. Log all requests to state/logs/niche-tacos-el-fogon-catalog.log
```

---

## 11. Business Value

```
Business Value: Turns WhatsApp into a 24/7 Tacos El Fogon sales channel. Estimated 30% increase in qualified leads per niche.
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
- Events: niche:restaurante:catalog:requested, niche:restaurante:service:selected, niche:restaurante:catalog:sent, niche:restaurante:lead:qualified
- Logs: state/logs/niche-tacos-el-fogon-catalog.log
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
