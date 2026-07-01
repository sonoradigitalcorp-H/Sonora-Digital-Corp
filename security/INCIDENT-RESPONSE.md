# Incident Response Plan — Native Agent OS

## Severity Levels

| Level | Color | Response Time | Examples |
|-------|-------|---------------|----------|
| P0 | 🔴 Critical | < 15 min | Data breach, auth compromise, gateway down |
| P1 | 🟠 High | < 1 hour | Secrets leaked, service down, rate limit bypass |
| P2 | 🟡 Medium | < 4 hours | Failed audit, degraded performance |
| P3 | 🟢 Low | < 24 hours | Minor vulnerability, cosmetic issue |

## Response Steps

### 1. Detect
- Monitor alerts GitHub Actions (monitor.yml)
- Autonomous.sh healthcheck cada 15 min
- MCP Gateway health endpoint

### 2. Contain
- Revoke compromised tokens: `sdc mcp auth revoke <tenant>`
- Disable access: `sdc mcp auth disable <client_id>`
- Kill suspicious agents: `sdc agent kill <name>`

### 3. Investigate
- Check audit log: `sdc audit run`
- Check MCP logs: `sdc agent logs <name>`
- Check events: `tail -100 state/logs/events.jsonl`

### 4. Recover
- Restart gateway: `sudo systemctl restart sonora-mcp-gateway.service`
- Rotate secrets: `sdc audit rotate-secrets`
- Restore from backup: `sdc backup restore <date>`

### 5. Document
- Create incident report
- Update security policies
- Emit `incident_resolved` event

## Recovery Scripts

```bash
# Emergency: revoke all tokens and force re-auth
sdc mcp auth revoke --all

# Emergency: isolate a tenant
sdc mcp auth disable abe-fenix

# Verify gateway integrity
sdc audit run
```
