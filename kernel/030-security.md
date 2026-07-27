# Security — Secrets, Access & Compliance

**Audit ID**: SEC-001

---

## Secrets Policy {#secrets-policy}

- All secrets in `.env` (gitignored)
- `.env.example` has placeholders, never real values
- No API keys in code, config files, or commits
- If a secret is committed, rotate it immediately

## Service Access {#service-access}

| Service | Port | Access |
|---------|------|--------|
| Neo4j | 7687 | localhost only |
| Qdrant | 6333 | localhost only |
| PostgreSQL | 5432 | localhost only |
| Redis | 6379 | localhost only, password required |
| crw scraper | 3000 | localhost only |
| MCP Gateway | 18989 | JWT auth required |

## Compliance {#compliance}

- All agent tool calls pass through Vectimus policy engine
- All actions are logged to append-only audit log
- Every evaluation produces an Ed25519-signed receipt
- Policy violations trigger Telegram alert

## Incident Response {#incident-response}

1. Detection → Guardian detects anomaly
2. Containment → Vectimus denies further actions
3. Investigation → Audit log reviewed
4. Recovery → Affected service restored
5. Learning → Lesson written to Engram
