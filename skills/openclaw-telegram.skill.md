# openclaw-telegram — OpenClaw Telegram Plugin

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-OCT-001

---

## 1. Business Objective

Send and receive Telegram messages via the OpenClaw gateway for sales and support channels.

## 2. Inputs (Gherkin)

```gherkin
Given OpenClaw gateway is running on port 18789
When a message needs to be sent to a Telegram chat
Or a new incoming Telegram message is received
```

## 3. Outputs (Gherkin)

```gherkin
Then message is sent to the target Telegram chat
And incoming messages are parsed and routed to the skill handler
And message history is stored for conversation continuity
```

## 4. Events

```
Events:
- openclaw:telegram:sent: outbound Telegram message delivered
- openclaw:telegram:received: inbound Telegram message processed
```

## 5. Dependencies

```
Dependencies:
- OpenClaw gateway: port 18789
- Telegram bot token: registered with BotFather
- Chat store: conversation threads database
```

## 6. Tools

```
Tools:
- openclaw_execute(telegram_send): send message to Telegram chat
- openclaw_execute(telegram_receive): poll or listen for new messages
```

## 7. Policies

```
Policies:
- Messages must respect Telegram's rate limits (30/s)
- Bot responses must be under 4096 characters (Telegram limit)
- Media must be compressed to Telegram's size limits
- Commands must be validated before execution
```

## 8. Success Metrics

```gherkin
Success Metrics:
- send_latency: Given send request When delivered Then seconds
  Target: < 2 s
- uptime: Given gateway in period When responding Then percentage
  Target: > 99.5%
```

## 9. Failure Conditions

```
Failure Conditions:
- Gateway unreachable: OpenClaw not responding (restart gateway)
- Bot token revoked: Telegram invalidated token (regenerate with BotFather)
- Rate limit hit: too many requests (implement queue with backoff)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If gateway unreachable → restart openclaw-gateway service
2. If token revoked → create new bot token, update config
3. If rate limited → backoff 30s, retry with queue
4. Log all attempts to state/logs/skills/openclaw-telegram.log
```

## 11. Business Value

```
Business Value: Telegram messaging integrated into OpenClaw for unified multi-channel communication.
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
- Events: openclaw:telegram:sent, openclaw:telegram:received
- Logs: state/logs/skills/openclaw-telegram.log
```
