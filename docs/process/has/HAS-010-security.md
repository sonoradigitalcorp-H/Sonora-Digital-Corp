# HAS-010 — Hermes Architecture Standard: Security & Governance

**Status:** Draft v1
**Domain:** security
**Updated:** 2026-07-08
**Depends on:** HAS-000, HAS-001, HAS-004, HAS-006

---

## 1. Purpose

Define security contracts, agent authentication, secrets management, and audit framework for the Hermes OS.

---

## 2. Agent Authentication

Every agent-to-agent call requires authentication:

```python
@dataclass
class AgentCredentials:
    agent_id: str
    token: str                    # JWT with agent_id + capabilities
    capabilities: list[str]       # What this agent is allowed to do
    expires_at: int               # Unix timestamp
```

Agents authenticate to the Kernel with a machine-local Unix socket (no network exposure). Cross-machine calls use mTLS.

## 3. Secrets Management

All secrets stored encrypted, never in code:

```
secrets/
├── .env                          # Local dev (gitignored)
├── .env.production               # Production (encrypted with age)
├── .env.production.age           # age-encrypted
└── keys/
    ├── age.pub                   # Public key
    └── age.key                   # Private key (gitignored)
```

## 4. Security Gates (Constitution)

The Constitution Engine (HAS-001) validates these specific security rules:

- **SEC-001**: No 0.0.0.0 binding (use 127.0.0.1)
- **SEC-002**: All secrets must be encrypted at rest
- **SEC-003**: No hardcoded API keys — use environment variables
- **SEC-004**: Agents cannot access files outside their domain
- **SEC-005**: All network calls must use TLS

## 5. Audit Trail

Every security-relevant event is logged:

```json
{
  "event": "security.access_denied",
  "timestamp": "2026-07-08T19:00:00Z",
  "agent": "builder",
  "resource": "secrets/production.age",
  "reason": "Agent not authorized for domain: finance",
  "action_taken": "blocked"
}
```

## 6. Events

| Event | Trigger | Severity |
|---|---|---|
| `security.access_denied` | Agent denied access to resource | warning |
| `security.auth_failed` | Authentication failed | error |
| `security.secret_rotated` | Secret updated | info |
| `security.threat_detected` | Suspicious pattern | critical |
