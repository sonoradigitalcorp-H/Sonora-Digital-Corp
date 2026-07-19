# hermes-qualify — Hermes Prospect Qualification

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-HQL-001

---

## 1. Business Objective

Qualify sales prospects by collecting key business information through structured questions via Telegram.

## 2. Inputs (Gherkin)

```gherkin
Given user sends a message expressing interest in Hermes
When intent keywords are detected: "contratar", "cuanto cuesta", "precio", "planes", "me interesa"
```

## 3. Outputs (Gherkin)

```gherkin
Then structured qualification questions are sent to the user
And user response data is collected for lead scoring
And qualified leads are forwarded to Sales OS
```

## 4. Events

```
Events:
- hermes:qualify:executed: qualification flow completed
- hermes:qualify:lead_captured: prospect data saved
```

## 5. Dependencies

```
Dependencies:
- Telegram bot: message send/receive
- Lead store: prospect database
- LLM: response analysis
```

## 6. Tools

```
Tools:
- llm_chat: analyze prospect responses
- engram_save: persist lead data
- telegram_send: deliver qualification questions
```

## 7. Policies

```
Policies:
- Lead data must be stored with consent flag
- Qualification questions must be answered before pricing is shared
- Prospects who decline must not be contacted again for 30 days
```

## 8. Success Metrics

```gherkin
Success Metrics:
- qualification_rate: Given prospects in period When qualified Then percentage
  Target: > 40%
- response_rate: Given questions sent When answered Then percentage
  Target: > 60%
```

## 9. Failure Conditions

```
Failure Conditions:
- User ghosts: prospect stops responding mid-qualification
- Invalid data: prospect provides non-actionable responses
- Duplicate: same prospect qualified twice in 24h
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If user ghosts → send one follow-up after 24h, then archive
2. If invalid data → ask clarifying question, max 3 attempts
3. If duplicate → merge with existing lead record
4. Log all attempts to state/logs/skills/hermes-qualify.log
```

## 11. Business Value

```
Business Value: Automated prospect qualification collecting 5 data points in under 2 minutes.
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
- Events: hermes:qualify:executed, hermes:qualify:lead_captured
- Logs: state/logs/skills/hermes-qualify.log
```
