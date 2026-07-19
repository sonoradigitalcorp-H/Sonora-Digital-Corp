# openclaw-whatsapp — OpenClaw WhatsApp Plugin

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-OCW-001

---

## 1. Business Objective

Send and receive WhatsApp messages via the OpenClaw gateway without direct wacli dependency.

## 2. Inputs (Gherkin)

```gherkin
Given OpenClaw gateway is running on port 18789
When a message needs to be sent to a WhatsApp contact
Or a new incoming message is received from WhatsApp
```

## 3. Outputs (Gherkin)

```gherkin
Then message is sent via WhatsApp with delivery confirmation
And incoming messages are routed to the appropriate handler
And message history is persisted for context
```

## 4. Events

```
Events:
- openclaw:whatsapp:sent: outbound message delivered
- openclaw:whatsapp:received: inbound message processed
```

## 5. Dependencies

```
Dependencies:
- OpenClaw gateway: port 18789
- WhatsApp account: linked device or API token
- Message store: conversation history database
```

## 6. Tools

```
Tools:
- openclaw_execute(whatsapp_send): send message to WhatsApp number
- openclaw_execute(whatsapp_receive): poll or listen for incoming messages
```

## 7. Policies

```
Policies:
- Outbound messages must be rate-limited to avoid spam flags
- Inbound messages must be processed within 5 seconds
- Message content must be sanitized before processing
- Media files must be scanned for malware before forwarding
```

## 8. Success Metrics

```gherkin
Success Metrics:
- send_latency: Given send request When delivered Then seconds
  Target: < 3 s
- delivery_rate: Given sent messages in period When confirmed Then percentage
  Target: > 98%
```

## 9. Failure Conditions

```
Failure Conditions:
- Gateway unreachable: OpenClaw port not responding (restart gateway)
- Auth failure: WhatsApp session expired (re-link device)
- Rate limited: WhatsApp imposed temporary ban (cool down, rotate)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If gateway unreachable → restart openclaw-gateway service
2. If auth fails → re-authenticate via QR code or API token refresh
3. If rate limited → implement backoff, notify operator
4. Log all attempts to state/logs/skills/openclaw-whatsapp.log
```

## 11. Business Value

```
Business Value: WhatsApp access via OpenClaw without direct wacli dependency.
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
- Events: openclaw:whatsapp:sent, openclaw:whatsapp:received
- Logs: state/logs/skills/openclaw-whatsapp.log
```
