# Feature Specification: WhatsApp Security and Automation Bridge

**Feature Branch**: `023-whatsapp-security-automation`

**Created**: 2026-06-10

**Status**: Draft

**Input**: WhatsApp bridge integration for JARVIS with strict security boundaries, message privacy, and n8n-based workflow automation for client onboarding, content delivery, and communication routing.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Secure WhatsApp Bridge Startup (Priority: P1)

JARVIS starts a WhatsApp session using baileys (WhatsApp Web JS) with automatic reconnection, port security (bind to 127.0.0.1 only, expose no unnecessary ports), and credential persistence. The bridge MUST NOT initiate outbound messages or read conversations from unknown contacts.

**Why this priority**: Without a secure bridge, no WhatsApp functionality exists. This is the foundation — any vulnerability here compromises all downstream features. Port binding and credential storage security are non-negotiable.

**Independent Test**: Can be tested by starting the bridge, verifying it binds only to `127.0.0.1`, that `ss -tlnp` shows no unexpected listening ports, and that no outbound connections other than WhatsApp Web (wss://web.whatsapp.com) are established.

**Acceptance Scenarios**:

1. **Given** JARVIS is started with WhatsApp enabled, **When** the bridge initializes, **Then** it binds to `127.0.0.1` only and no port is exposed on `0.0.0.0`.
2. **Given** the bridge is running, **When** an unauthenticated request hits the webhook port, **Then** the request is rejected with 401/403 and logged.
3. **Given** a valid authentication state file exists, **When** the bridge restarts, **Then** it reuses the existing session without requiring a new QR scan.
4. **Given** a QR scan is required, **When** the QR code is displayed, **Then** no other WhatsApp session data or credentials are exposed in the QR output.
5. **Given** the bridge is running, **When** a message arrives from an unknown contact, **Then** the message is logged but NOT read/stored/processed unless an explicit whitelist rule matches.

---

### User Story 2 - Message Filtering and Privacy Gates (Priority: P1)

Only messages from authorized contacts are processed. All other messages are silently dropped (not stored). Authorization is a deterministic allowlist — the system NEVER processes messages from numbers not on the allowlist.

**Why this priority**: Message privacy is constitutionally required. Processing messages from unauthorized contacts violates user trust and could expose JARVIS to spam, abuse, or data leaks.

**Independent Test**: Send messages to the bridge from an unauthorized number and verify they are logged at DEBUG level but never stored, forwarded to n8n, or trigger any workflow. Then authorize the number and verify subsequent messages ARE processed.

**Acceptance Scenarios**:

1. **Given** a contact allowlist with `+521234567890` authorized, **When** a message arrives from `+521234567890`, **Then** the message is passed to the message processing pipeline.
2. **Given** a contact allowlist without `+529876543210`, **When** a message arrives from `+529876543210`, **Then** the message is logged at DEBUG level and silently dropped — no persistent storage, no n8n trigger, no response.
3. **Given** an empty allowlist, **When** ANY message arrives, **Then** ALL messages are dropped (fail-closed behavior).
4. **Given** a message from an authorized contact, **When** the message body passes content filters, **Then** it is forwarded to the configured webhook/n8n endpoint.
5. **Given** a message that fails content filtering (e.g., binary blob, oversized >4096 chars), **When** it arrives from an authorized contact, **Then** it is rejected with a logged warning and not forwarded.

---

### User Story 3 - Webhook Endpoint Authentication (Priority: P1)

The webhook endpoint that receives messages from WhatsApp and forwards them to n8n/Hermes validates every request with a rotating API key. Requests without a valid key are rejected with 401.

**Why this priority**: The webhook endpoint is the gateway between the WhatsApp bridge and automation. Without authentication, any actor could inject fake messages or trigger unauthorized workflows.

**Independent Test**: Send requests to the webhook endpoint with missing, expired, and valid API keys. Verify that only valid keys are accepted (200) and all others return 401 with no processing.

**Acceptance Scenarios**:

1. **Given** a valid API key configured, **When** an HTTP request includes the key in the `X-API-Key` header, **Then** the request is authenticated and processed.
2. **Given** a valid API key, **When** a request uses an expired or rotated key, **Then** the request returns 401 and is logged as a security event.
3. **Given** no `X-API-Key` header, **When** any request arrives, **Then** it returns 401 immediately without processing the body.
4. **Given** an API key rotation event, **When** the key is rotated in config, **Then** the old key is invalidated within 60 seconds and new requests require the new key.

---

### User Story 4 - n8n Workflow Automation for Client Onboarding (Priority: P2)

When an authorized contact sends a keyword-triggered message (e.g., "start", "registro", "onboarding"), the bridge routes it to an n8n webhook that runs a client onboarding workflow. The workflow collects profile data, stores it, and sends a confirmation via WhatsApp. The n8n workflow is the only consumer of message data — JARVIS itself never stores message content from onboarding flows.

**Why this priority**: Client onboarding is the primary business use case. It validates the entire pipeline: message receipt → allowlist check → webhook auth → n8n workflow → response. Delivers measurable value: automated client intake.

**Independent Test**: Send "start" from an authorized contact and verify the n8n workflow fires, a response is sent back, and the client profile is created in the configured store. Verify no message content is stored by the WhatsApp bridge itself.

**Acceptance Scenarios**:

1. **Given** an authorized contact, **When** the contact sends "start" or "registro", **Then** the message is forwarded to the n8n onboarding webhook and the contact receives a confirmation message within 5 seconds.
2. **Given** the n8n onboarding workflow is running, **When** it completes successfully, **Then** the contact receives a personalized welcome message with next steps.
3. **Given** the n8n webhook is down, **When** a message is forwarded, **Then** the bridge logs the delivery failure and queues the message (max 3 retries, 30s apart).
4. **Given** a message that triggers onboarding, **When** the contact is already onboarded, **Then** the workflow returns "already registered" and JARVIS sends a polite reminder instead of re-creating the profile.

---

### User Story 5 - n8n Workflow Automation for Content Delivery (Priority: P2)

Authorized contacts can request content (audio, video, documents, or information) via keyword commands. The n8n workflow handles content lookup, access control, and delivery. Content is sent via WhatsApp message attachments or links.

**Why this priority**: Content delivery is the second primary business use case — enabling automated responses to client content requests without manual intervention.

**Independent Test**: Send a content request keyword from an authorized contact and verify the n8n workflow responds with the correct content (file or link) within 10 seconds.

**Acceptance Scenarios**:

1. **Given** an authorized contact, **When** the contact sends a content request keyword (e.g., "audio", "guia"), **Then** the bridge routes it to the n8n content delivery webhook and the contact receives the requested content.
2. **Given** a contact requests content they don't have access to, **When** the n8n workflow checks permissions, **Then** the contact receives a "not authorized" message and the attempt is logged.
3. **Given** a content request for a non-existent item, **When** the n8n workflow cannot find the content, **Then** the contact receives a "not found" message with a list of available content.
4. **Given** large content (>16MB), **When** n8n attempts to send via WhatsApp, **Then** the workflow falls back to sending a download link instead of the file directly.

---

### User Story 6 - Rate Limiting and Abuse Prevention (Priority: P2)

The WhatsApp bridge enforces per-contact and global rate limits to prevent abuse, spam, and accidental flooding. Rate limits are configurable and logged.

**Why this priority**: Without rate limits, a misconfigured n8n workflow, a bug, or a malicious actor could flood the contact with messages or exhaust API quotas.

**Independent Test**: Send messages at increasing frequency from a test contact and verify that rate limit thresholds are enforced: messages beyond the limit are queued or dropped with a logged warning.

**Acceptance Scenarios**:

1. **Given** a per-contact rate limit of 10 messages/minute, **When** a contact sends 12 messages in 60 seconds, **Then** messages 11 and 12 are queued and processing resumes after the rate window resets.
2. **Given** a global rate limit of 100 messages/minute, **When** all contacts combined exceed 100 messages in 60 seconds, **Then** excess messages are queued with priority ordering (first-come-first-serve).
3. **Given** a contact exceeds the rate limit 3 times in 10 minutes, **When** they send another message, **Then** the contact is temporarily blocked for 5 minutes and the event is logged as a security incident.
4. **Given** rate limit configuration changes, **When** config is reloaded, **Then** new rate limits take effect within 60 seconds without restarting the bridge.

---

### User Story 7 - Error Handling and Logging (Priority: P3)

All bridge operations log to a structured logger with severity levels. Errors, authentication failures, rate limit breaches, and connection drops are logged with context. Logs are locally stored with rotation.

**Why this priority**: Without proper logging, debugging bridge issues is impossible. This is essential for maintenance and security auditing.

**Independent Test**: Induce each error condition (bad auth, connection drop, webhook timeout, rate limit hit) and verify that a structured log entry is created with the correct severity and context.

**Acceptance Scenarios**:

1. **Given** the bridge is running, **When** a connection drop occurs, **Then** an ERROR-level log entry is created with the error type, timestamp, and reconnection attempt count.
2. **Given** a webhook delivery failure, **When** retries are exhausted, **Then** a CRITICAL-level log entry is created with the message ID, webhook URL, and last error.
3. **Given** an authentication failure, **When** an invalid API key is presented, **Then** a WARN-level log entry is created with the source IP, timestamp, and endpoint.
4. **Given** a rate limit breach, **When** a contact is temporarily blocked, **Then** an INFO-level log entry is created with the contact number and block duration.
5. **Given** log rotation is configured, **When** the log file reaches 10MB, **Then** it is rotated and compressed automatically.

---

### Edge Cases

- **QR scan timeout**: if the QR code is not scanned within 60 seconds, the bridge MUST emit a new QR code; after 3 timeouts it MUST stop and log an ERROR.
- **Multi-device pairing**: baileys uses multi-device protocol; the bridge MUST handle the case where the phone is offline and messages need to be queued by WhatsApp servers.
- **Connection lost during message send**: if the connection drops while sending a response, the bridge MUST retry once; if the retry fails, it MUST return an error to n8n and log the failure.
- **Webhook endpoint unreachable**: if the n8n webhook is unreachable (DNS failure, connection refused), the bridge MUST NOT crash — it MUST log the error and retry.
- **API key file missing on startup**: if the API key file does not exist, the bridge MUST generate a new key and log the generation as an INFO event.
- **Allowlist file missing**: if no allowlist is configured, the bridge MUST operate in fail-closed mode (all messages dropped) and emit a WARN-level log every 5 minutes.
- **Message contains media with no caption**: media messages without captions from authorized contacts are forwarded with metadata but minimal processing (no OCR, no content inspection).
- **Concurrent webhook calls**: if n8n takes longer than the configured timeout (default 30s), the bridge MUST timeout and not block subsequent messages.
- **Very high message volume (>1000/min)**: the bridge MUST backpressure by queuing and tail-dropping messages beyond a buffer size (configurable, default 5000).

## Requirements *(mandatory)*

### Functional Requirements

**Bridge Core**

- **FR-001**: The WhatsApp bridge MUST use baileys (WhatsApp Web JS) as the underlying protocol implementation and MUST run as a standalone process.
- **FR-002**: The bridge MUST bind all HTTP servers to `127.0.0.1` only and MUST NOT expose any port on `0.0.0.0`.
- **FR-003**: The bridge MUST persist authentication state to disk (encrypted) and MUST reuse it across restarts without requiring a new QR scan.
- **FR-004**: The bridge MUST support automatic reconnection with exponential backoff (1s, 2s, 4s, 8s, max 60s) on connection drops.

**Message Security**

- **FR-005**: The bridge MUST implement a contact allowlist that is checked for EVERY incoming message before any processing occurs.
- **FR-006**: The bridge MUST NOT store, forward, or process messages from contacts NOT on the allowlist (fail-closed).
- **FR-007**: The bridge MUST NOT read, process, or store messages from group chats unless explicitly configured with a group allowlist (OFF by default).
- **FR-008**: The bridge MUST strip all message content after forwarding to the webhook — JARVIS memory stores only message metadata (sender, timestamp, message ID), never the text/content of messages.

**API Key Authentication**

- **FR-009**: Every webhook endpoint exposed by the bridge MUST require an `X-API-Key` header for authentication.
- **FR-010**: API keys MUST be configurable via environment variable (`WHATSAPP_API_KEY`) and a local file (`config/whatsapp/api_key.txt`).
- **FR-011**: API key rotation MUST be supported by reading the config on SIGHUP or at startup; runtime rotation MUST take effect within 60 seconds.
- **FR-012**: API key comparison MUST use constant-time string comparison to prevent timing attacks.

**n8n Integration**

- **FR-013**: The bridge MUST forward authorized messages to configurable n8n webhook URLs via POST with JSON body containing `{ from, body, timestamp, message_id, contact_name }`.
- **FR-014**: The bridge MUST support at least 3 distinct n8n webhook targets (onboarding, content delivery, fallback) routed by message keyword matching.
- **FR-015**: Webhook delivery MUST use HTTPS only and MUST validate TLS certificates.

**Rate Limiting**

- **FR-016**: The bridge MUST enforce per-contact rate limiting with a configurable window size and max messages per window (default: 10 messages / 60 seconds).
- **FR-017**: The bridge MUST enforce a global rate limit with a configurable window (default: 100 messages / 60 seconds).
- **FR-018**: After 3 rate limit violations within 10 minutes, the contact MUST be temporarily blocked (default: 5 minutes).
- **FR-019**: Rate limit state MUST be in-memory (not persisted); on bridge restart, rate limits reset.

**Logging and Observability**

- **FR-020**: The bridge MUST use structured JSON logging with severity levels (DEBUG, INFO, WARN, ERROR, CRITICAL).
- **FR-021**: Logs MUST include correlation IDs for message tracking across the bridge, webhook, and n8n.
- **FR-022**: Log files MUST be rotated at 10MB size with max 5 rotated files kept.
- **FR-023**: Security events (auth failures, rate limit blocks, allowlist drops, key rotations) MUST be logged at WARN level or above.

**Content and Workflow**

- **FR-024**: The bridge MUST support keyword-to-webhook routing: configure a map of keywords (e.g., `{"start": "https://n8n/webhook/onboarding", "audio": "https://n8n/webhook/content"}`).
- **FR-025**: The bridge MUST include an HTTP healthcheck endpoint at `GET /health` returning 200 with `{"status": "ok", "connected": true/false}` — accessible only from localhost.

**Non-functional Requirements**

- **NFR-001 (Security)**: Secrets MUST NOT appear in logs, error messages, or process listings.
- **NFR-002 (Security)**: The bridge process MUST drop privileges after binding to privileged ports (if any); run as non-root user.
- **NFR-003 (Privacy)**: Message content MUST be ephemeral — forwarded then discarded. Only metadata (from, timestamp, message_id, workflow result) may be stored.
- **NFR-004 (Privacy)**: The bridge MUST NOT log message body text above DEBUG level and the DEBUG log file MUST be rotated hourly and retained max 24h.
- **NFR-005 (Performance)**: Message processing latency (receive → forward to webhook) MUST be <500ms p95 under normal load.
- **NFR-006 (Performance)**: The bridge MUST handle 50 concurrent message deliveries without degradation.
- **NFR-007 (Reliability)**: The bridge MUST achieve 99.5% uptime under normal conditions (excl. WhatsApp service outages).
- **NFR-008 (Reliability)**: Webhook delivery MUST retry with exponential backoff (3 attempts, 10s/30s/60s spacing).
- **NFR-009 (Maintainability)**: Configuration MUST be file-based (YAML or env) and support hot-reload on SIGHUP without process restart.
- **NFR-010 (Auditability)**: Every forwarded message MUST have a traceable path: allowlist check ✓ → auth ✓ → rate limit ✓ → webhook delivery ✓, logged as a structured event.

### Key Entities

- **WhatsAppBridge**: the baileys-based process managing the WhatsApp Web session, connection lifecycle, and message routing.
- **Contact**: a phone number in international format (E.164) with an associated authorized status (allowlisted or not).
- **Message**: an incoming WhatsApp message with `from`, `body`, `timestamp`, `message_id`, `type` (text/image/video/audio/document), and `has_media`.
- **Allowlist**: a deterministic list of E.164 phone numbers authorized to interact with the bridge.
- **ApiKey**: a bearer token used to authenticate webhook requests, with rotation support and constant-time comparison.
- **RateLimitState**: in-memory tracking of per-contact and global message counts within configurable time windows.
- **WebhookTarget**: a configured HTTPS URL with keyword trigger rules; receives forwarded messages as JSON POST bodies.
- **AuthState**: persisted baileys authentication credentials (encrypted multi-device JSON), enabling session reuse.
- **LogEvent**: a structured JSON log entry with severity, correlation_id, component, message, and timestamp.
- **WorkflowResult**: the response from an n8n webhook, including success/failure status, reply message text, and optional media attachment instructions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On startup, the bridge binds to `127.0.0.1` exclusively — verified by `ss -tlnp` showing zero listeners on `0.0.0.0`.
- **SC-002**: 100% of messages from non-allowlisted contacts are silently dropped (logged at DEBUG, never stored or forwarded) — verified by integration test.
- **SC-003**: 100% of webhook requests without valid `X-API-Key` return 401 — verified by integration test with missing, expired, and valid keys.
- **SC-004**: Message processing latency <500ms p95 for the bridge component (receive → forward to webhook) — measured with synthetic load.
- **SC-005**: On allowlist reload, changes take effect within 60 seconds without restart — verified by adding/removing a number and sending a test message.
- **SC-006**: The bridge recovers from connection drops automatically within 60 seconds (p99) — verified by killing the network interface and measuring reconnection time.
- **SC-007**: Rate limits are enforced: per-contact limit violations are queued/blocked deterministically — verified by sending 12 messages in 60 seconds and observing messages 11-12 queued.
- **SC-008**: No message body text appears in any log at INFO, WARN, ERROR, or CRITICAL level — verified by scanning logs after a test session.
- **SC-009**: API key rotation takes effect within 60 seconds — verified by changing the key and observing old key rejection.
- **SC-010**: All security events (auth failures, rate limit blocks, allowlist drops) are logged at WARN or above with correlation IDs — verified by log inspection.

## Assumptions

- **Single WhatsApp number**: the bridge manages one WhatsApp session (one phone number). Multi-number support is out of scope for v1.
- **baileys library**: the bridge uses `@whiskeysockets/baileys` (TypeScript/Node.js). The baileys library is community-maintained and not officially supported by WhatsApp/Meta.
- **Node.js runtime**: the bridge runs as a Node.js process using the Hermes gateway or standalone via PM2/systemd.
- **n8n self-hosted**: n8n runs on the same LAN/127.0.0.1; webhook URLs point to the local n8n instance.
- **No message queuing system**: v1 uses in-memory queuing; Redis/AMQP for persistent queuing is out of scope.
- **No database**: v1 bridge has no database dependency; allowlists and config are file-based. n8n workflows may use their own storage (SQLite/Postgres).
- **E.164 format**: all phone numbers are stored and compared in E.164 format (`+[country][number]`). No fuzzy matching.
- **Content delivery limits**: WhatsApp's 16MB file size limit for documents and 640KB for images is assumed; larger files use link fallback.
- **No end-to-end encryption breaking**: the bridge does not attempt to decrypt WhatsApp's E2EE; it processes messages as they arrive via baileys (already decrypted by the WhatsApp client).
- **Meta Business API not used**: the bridge uses the unofficial baileys library, not the official WhatsApp Business API. See `research.md` for the comparison.
