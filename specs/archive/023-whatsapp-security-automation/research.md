# Phase 0 Research: WhatsApp Security and Automation Bridge

**Feature**: `023-whatsapp-security-automation` | **Date**: 2026-06-10

This document resolves the open technical decisions for the implementation plan, with focus on: (1) WhatsApp Business API vs baileys comparison, (2) security best practices for WhatsApp automation, (3) webhook security patterns, and (4) n8n integration architecture.

---

## 1. WhatsApp Business API vs baileys (WhatsApp Web JS)

### Decision

Use **@whiskeysockets/baileys** (WhatsApp Web JS library) for v1. The WhatsApp Business API is documented as the recommended alternative for production use, but baileys is the pragmatic choice for a local, single-number, self-hosted JARVIS deployment.

### Comparison

| Criteria | WhatsApp Business API (Official) | baileys (Community) |
|----------|----------------------------------|---------------------|
| **Cost** | Free tier (1K conversations/mo), then $0.005-0.08 per conversation | Free (no usage limits) |
| **Approval** | Requires Meta Business Verification (business docs, use case review) | None (clone of WhatsApp Web protocol) |
| **Setup time** | 2-6 weeks (business verification, phone number approval) | 5 minutes (npm install, QR scan) |
| **Protocol** | Official Graph API (REST + Webhooks) | Reverse-engineered WhatsApp Web WebSocket protocol |
| **E2EE** | Full E2EE, Cloud API handles decryption | Full E2EE, client-side decryption via baileys |
| **Multi-device** | Native support (up to 10 devices) | Multi-device protocol support (beta → stable) |
| **Reliability** | 99.9% SLA (via Meta infrastructure) | Best-effort (community-maintained, no SLA) |
| **Rate limits** | Official rate limits (documented, enforced) | No official limits (subject to WhatsApp Web rate limiting) |
| **ToS compliance** | Official — complies with WhatsApp ToS | Unofficial — reverse-engineered, potential ToS violation risk |
| **Message history** | 24h+ message history retention on Cloud API | Real-time only (no Cloud-side history) |
| **Templates** | Requires pre-approved message templates for outbound | No template restriction (send any message) |
| **Local deployment** | Requires cloud or on-premises Business API server | Fully local (no external dependency) |
| **Maintenance** | Meta-managed (API updates handled by Meta) | Community-driven (breaking changes on WhatsApp protocol updates) |
| **Number portability** | Requires dedicated phone number (no existing WA account) | Works with existing WhatsApp number (QR scan) |

### Why baileys for v1

1. **Zero external dependency**: No cloud API to configure, no Meta Business verification, no monthly fees.
2. **Works with existing number**: JARVIS can use an existing WhatsApp account via QR scan — no need for a separate business number.
3. **Local control**: All message processing stays local; no message data is sent to Meta's Cloud API (aligned with JARVIS privacy principles).
4. **Instant setup**: 5-minute setup vs 2-6 weeks for Business API approval.

### Why WhatsApp Business API for v2 (future)

1. **Production reliability**: If JARVIS handles client communication at scale, the Business API's SLA and official support become necessary.
2. **Template messages**: Pre-approved templates are required for outbound notifications in many jurisdictions (GDPR, spam compliance).
3. **Multiple agents**: The Business API supports multiple phone numbers and agent integration natively.

### Risk Mitigation for baileys

| Risk | Mitigation |
|------|------------|
| **ToS violation** | The bridge is for personal/internal use, not a public B2C service. Low risk of enforcement against single-user local deployment. |
| **Protocol breaking changes** | Pin baileys version in `package.json`. Test updates in staging. Subscribe to `@whiskeysockets/baileys` releases. |
| **Connection instability** | Automatic reconnection with exponential backoff (FR-004). PM2 auto-restart on crash. |
| **No SLA** | Bridge is a non-critical component of JARVIS. Core functionality (web UI, memory, MCP) does not depend on WhatsApp. |
| **Rate limiting by WhatsApp** | Implement local rate limiting (per-contact and global) to prevent tripping WhatsApp Web's internal rate limits. |

---

## 2. Security Best Practices for WhatsApp Automation

### Port Security

- **Principle**: Expose only the minimum necessary ports. Bind all HTTP servers to `127.0.0.1` — never `0.0.0.0`.
- **Implementation**: Express server in `src/server.ts` binds to `127.0.0.1` explicitly:
  ```typescript
  app.listen(PORT, '127.0.0.1', () => { ... });
  ```
- **Verification**: `ss -tlnp | grep node` must show only `127.0.0.1:PORT` with no `0.0.0.0:*` listeners.
- **Reference**: [OWASP Transport Layer Protection](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html)

### API Key Authentication

- **Principle**: All webhook endpoints require authentication. Use bearer tokens in headers (not query parameters — they appear in server logs).
- **Constant-time comparison**: Use `crypto.timingSafeEqual` to prevent timing attacks:
  ```typescript
  function validateApiKey(provided: string): boolean {
    const expected = loadApiKey();
    if (provided.length !== expected.length) return false;
    return crypto.timingSafeEqual(Buffer.from(provided), Buffer.from(expected));
  }
  ```
- **Key rotation**: Support rotation via config reload (SIGHUP). Old key remains valid for a grace period (configurable, default 60s) to avoid race conditions during rotation.
- **Storage**: API key in `config/whatsapp/api_key.txt` (gitignored) or `WHATSAPP_API_KEY` env var. File auto-generated if missing.
- **Reference**: [OWASP REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)

### Webhook Security

- **HTTPS only**: All webhook URLs MUST use HTTPS. TLS certificate validation is required (not disabled with `NODE_TLS_REJECT_UNAUTHORIZED=0`).
- **Request signing**: For v2, consider webhook payload signing (HMAC-SHA256 with shared secret) to verify webhook origin.
- **IP allowlisting**: If n8n is on a known IP, add IP filtering as an additional layer (not a substitute for API key auth).
- **Timeouts**: Webhook delivery timeout (default 30s) prevents slow n8n workflows from blocking the bridge.

### Message Privacy

- **Principle**: The bridge is a pipe, not a store. Message content is forwarded to n8n and discarded. Only metadata (from, timestamp, message_id) is available for logging.
- **Allowlist fail-closed**: Empty allowlist = all messages blocked. This is the safe default.
- **Group chat isolation**: Group chat processing is OFF by default (FR-007). If enabled, must be explicitly configured per group.
- **No message body in logs**: Message text is never logged at INFO/WARN/ERROR/CRITICAL levels. Only DEBUG level (with hourly rotation, 24h retention) may include message bodies for troubleshooting.

### Rate Limiting

- **Per-contact**: 10 messages/minute default. Prevents a single contact from flooding the bridge.
- **Global**: 100 messages/minute default. Prevents total message volume from overwhelming the bridge or n8n.
- **Temporary blocks**: 3 violations in 10 minutes → 5-minute block for the contact.
- **Algorithm**: Sliding window (not fixed window) to avoid burst at window boundaries. In-memory only — resets on restart.

### Authentication State Security

- Baileys auth state (multi-device credentials) is persisted to disk as encrypted JSON.
- File permissions: `600` (owner read/write only).
- File location: `config/whatsapp/auth/` — gitignored, outside the web root.

---

## 3. n8n Integration Architecture

### Workflow Pattern

```
WhatsApp Contact → baileys Bridge → [allowlist → filters → rate limit → auth → router]
  → POST to n8n webhook → n8n workflow (onboarding/content/fallback)
  → n8n response (reply instructions) → baileys Bridge → WhatsApp Contact
```

### n8n Webhook Payload (Bridge → n8n)

```json
{
  "from": "+521234567890",
  "body": "start",
  "timestamp": 1718000000,
  "message_id": "ABEGkR1QwX...",
  "contact_name": "Juan Pérez",
  "message_type": "text",
  "has_media": false
}
```

### n8n Webhook Response (n8n → Bridge)

```json
{
  "action": "send_message",
  "to": "+521234567890",
  "text": "¡Bienvenido! Por favor comparte tu correo electrónico para comenzar.",
  "media_url": null
}
```

For media delivery:
```json
{
  "action": "send_media",
  "to": "+521234567890",
  "text": "Aquí tienes el audio solicitado",
  "media_url": "https://n8n.internal/audio/file.mp3",
  "media_type": "audio"
}
```

### Webhook Endpoints (Bridge)

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/health` | GET | No | Healthcheck (localhost only) |
| `/webhook/whatsapp` | POST | X-API-Key | Receive n8n workflow results (outbound sends) |

### Keyword-to-Webhook Routing

Configured in `config.yaml`:

```yaml
webhooks:
  onboarding:
    keyword: "start"
    url: "https://localhost:5678/webhook/whatsapp-onboarding"
    timeout: 30
  content_audio:
    keyword: "audio"
    url: "https://localhost:5678/webhook/whatsapp-content"
    timeout: 60
  content_guide:
    keyword: "guia"
    url: "https://localhost:5678/webhook/whatsapp-content"
    timeout: 60
  fallback:
    keyword: null  # unmatched keywords go here
    url: "https://localhost:5678/webhook/whatsapp-fallback"
    timeout: 30
```

Matching strategy: longest-prefix match, case-insensitive. The `fallback` target receives all messages whose keyword does not match any configured trigger.

---

## 4. Logging and Observability

### Structured Log Format (pino)

```json
{
  "level": 30,
  "time": 1718000000123,
  "pid": 12345,
  "hostname": "jarvis",
  "component": "allowlist",
  "correlation_id": "msg_abc123",
  "msg": "Message from unauthorized contact dropped",
  "from": "+529876543210",
  "message_id": "ABEGkR1QwX..."
}
```

### Log Severity Mapping

| Severity | When | Retention |
|----------|------|-----------|
| DEBUG | Message tracing, allowed message details (includes body) | 24h, rotated hourly |
| INFO | Config loaded, connection established, message forwarded | 7 days, rotated 10MB |
| WARN | Auth failure, allowlist drop, rate limit warning | 30 days, rotated 10MB |
| ERROR | Webhook failure, connection drop, retry exhaustion | 90 days, rotated 10MB |
| CRITICAL | Auth state corrupted, unrecoverable error | 90 days + alert |

---

## 5. Alternatives Considered

### go-whatsapp / whatsmeow (Go)

A Go implementation of the WhatsApp Web protocol (`whatsmeow` by tulir). More performant than Node.js baileys but would introduce a new language into the JARVIS stack (currently Python + TypeScript). Rejected for v1 — baileys keeps the stack consistent.

### whatsapp-web.js (Node.js, Puppeteer-based)

Another Node.js WhatsApp library that uses Puppeteer to control WhatsApp Web in a headless browser. More reliable for some use cases but heavier (Chrome/Chromium dependency, ~300MB+). Rejected — baileys uses the WebSocket protocol directly (no browser), making it lighter and faster.

### Direct HTTP API to Meta Graph

Using the WhatsApp Cloud API directly without any middleware. Rejected — requires business verification, adds cloud dependency, and sends message data to Meta's servers.

### MQTT/Redis for n8n communication

Instead of webhooks, use Redis pub/sub or MQTT for bridge-to-n8n communication. Rejected for v1 — webhooks are simpler, n8n supports them natively, and they provide natural retry semantics via HTTP response codes.

---

## 6. Resolved Unknowns Summary

| Topic | Resolution |
|-------|------------|
| WhatsApp protocol | `@whiskeysockets/baileys` (WhatsApp Web JS) via WebSocket — not official Business API |
| Port security | All HTTP servers bind to `127.0.0.1` only |
| API key comparison | `crypto.timingSafeEqual` — constant time |
| Webhook security | HTTPS only, X-API-Key header, TLS cert validation, 30s timeout, 3 retries |
| Message privacy | Content ephemeral — bridge forwards then discards. Only metadata logged |
| Allowlist behavior | Fail-closed — empty allowlist = all messages blocked |
| Group chat | OFF by default — must be explicitly configured |
| Rate limiting | In-memory sliding window, per-contact + global, temporary blocks |
| Logging | Structured JSON (pino), severity levels, correlation IDs, rotation per severity |
| n8n integration | HTTP webhooks, JSON payload, keyword-based routing |
| Process management | PM2 for Node.js bridge |
| Message queue | In-memory queue (max 1000), flush on reconnect |
| Auth state encryption | baileys built-in multi-device encryption, file permissions 600 |

**All NEEDS CLARIFICATION resolved. Ready for implementation.**

## Sources

- [@whiskeysockets/baileys](https://github.com/WhiskeySockets/Baileys) — WhatsApp Web JS library
- [WhatsApp Business API docs](https://developers.facebook.com/docs/whatsapp/cloud-api) — Official Meta API
- [OWASP REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
- [OWASP Transport Layer Protection](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html)
- [Node.js crypto.timingSafeEqual](https://nodejs.org/api/crypto.html#crypto_crypto_timingsafeequal_a_b)
- [pino structured logger](https://getpino.io/) — Node.js logging
- [n8n webhook documentation](https://docs.n8n.io/workflows/triggers/webhook/)
- [whatsmeow (Go)](https://github.com/tulir/whatsmeow) — Alternative Go implementation
- [whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js) — Puppeteer-based alternative
