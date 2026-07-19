# hermes-demo-request — Hermes Demo Scheduling

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-HDR-001

---

## 1. Business Objective

Capture demo requests and guide prospects to schedule a live Hermes demonstration with clear expectations of what will be shown.

## 2. Inputs (Gherkin)

```gherkin
Given user requests a demo or personal contact
When trigger keywords are detected: "demo", "quiero ver", "me interesa", "contacto", "agendar", "hablar con alguien", "prueba gratis"
```

## 3. Outputs (Gherkin)

```gherkin
Then demo scheduling link is provided
And demo agenda is communicated
And urgency element (founder pricing) is included
```

## 4. Events

```
Events:
- hermes:demo-request:executed: demo request captured
- hermes:demo-request:scheduled: demo appointment booked
```

## 5. Dependencies

```
Dependencies:
- Calendar: demo scheduling system
- Sales team: demo availability
- CRM: lead tracking
```

## 6. Tools

```
Tools:
- llm_chat: compose demo scheduling response
- engram_save: persist demo request lead data
```

## 7. Policies

```
Policies:
- Demo link must be clickable and functional
- Demo agenda must set clear expectations (30 min, live)
- Urgency messaging must be time-bound and honest
- Demo requests must be logged in CRM within 5 minutes
- Founder pricing deadlines must be accurate
```

## 8. Success Metrics

```gherkin
Success Metrics:
- scheduling_time: Given demo request When link sent Then seconds
  Target: < 10 s
- show_rate: Given demos scheduled When attended Then percentage
  Target: > 70%
```

## 9. Failure Conditions

```
Failure Conditions:
- Broken link: demo scheduling URL returns error
- No availability: sales team cannot accommodate request volume
- Duplicate: same prospect requests multiple demos
- Founder pricing expired: deadline passed without update
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If link broken → verify URL, provide manual contact alternative
2. If no availability → queue with priority, notify sales team
3. If duplicate → merge requests, confirm existing booking
4. If pricing expired → update to current offer, notify prospect
5. Log all attempts to state/logs/skills/hermes-demo-request.log
```

## 11. Business Value

```
Business Value: Automated demo scheduling captures leads 24/7 without sales team availability constraints.
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
- Events: hermes:demo-request:executed, hermes:demo-request:scheduled
- Logs: state/logs/skills/hermes-demo-request.log
```
