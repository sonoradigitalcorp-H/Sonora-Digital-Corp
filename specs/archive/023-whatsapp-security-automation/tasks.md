---

description: "Task list for WhatsApp Security and Automation Bridge"
---

# Tasks: WhatsApp Security and Automation Bridge

**Input**: Design documents from `specs/023-whatsapp-security-automation/`

**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅

**Tests**: **MANDATORY**. All security-critical logic (allowlist, API key auth, rate limiting, filters) MUST have unit tests. Integration tests MUST mock baileys and n8n.

**Organization**: Tasks are grouped by phase with clear dependencies. Security tasks (US1-US3) are P1 and must be complete before automation (US4-US5).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story the task belongs to (US1-US7)
- Exact file paths are included in each task

## Path Conventions

Standalone Node.js service: `services/whatsapp-bridge/` under the JARVIS monorepo root.

---

## Phase 1: Project Setup (Shared Infrastructure)

**Purpose**: Initialize the Node.js bridge project and directory structure

- [ ] T001 Create directory structure for `services/whatsapp-bridge/src/`, `tests/unit/`, `tests/integration/`, `config/whatsapp/`
- [ ] T002 Initialize npm project with `package.json`, `tsconfig.json`, `.env.example`, `.gitignore`
- [ ] T003 Install core dependencies: `@whiskeysockets/baileys`, `express`, `pino`, `pino-pretty`, `yaml`, `node:crypto`, `pm2`
- [ ] T004 Install dev dependencies: `jest`, `ts-jest`, `@types/express`, `@types/node`, `typescript`, `supertest`, `nock`
- [ ] T005 [P] Create `config/whatsapp/config.yaml` with all configurable parameters (rate limits, ports, webhook URLs, timeout, log level)
- [ ] T006 [P] Create `config/whatsapp/allowlist.yaml` with example allowlist entries (E.164 format) and a comment about fail-closed behavior
- [ ] T007 [P] Create `.env.example` documenting `WHATSAPP_API_KEY`, `WHATSAPP_CONFIG_PATH`, `NODE_ENV`, `LOG_LEVEL`
- [ ] T008 [P] Add `ecosystem.config.js` for PM2 (service name, script, watch, restart strategy, max memory)

**Checkpoint**: Project structure ready for implementation

---

## Phase 2: Bridge Core — Security Foundation (US1, Priority: P1)

**Purpose**: Implement the core WhatsApp bridge with baileys, ensuring port security, auth state persistence, and loopback binding.

**⚠️ CRITICAL**: These tasks implement FR-001 through FR-004. Security foundation must be solid before any message processing.

- [ ] T009 [US1] Implement `src/types.ts` — all TypeScript types and interfaces (Contact, Message, Config, AllowlistEntry, WebhookTarget, AuthState, RateLimitConfig, LogEvent)
- [ ] T010 [US1] Implement `src/config.ts` — load YAML config from file, merge with env vars, support SIGHUP reload via `process.on('SIGHUP', reload)`
- [ ] T011 [US1] Implement `src/logger.ts` — structured pino logger with correlation IDs (child logger per message), severity levels, log file rotation config
- [ ] T012 [US1] Implement `src/bridge.ts` — baileys socket initialization, multi-device auth state persistence (encrypted JSON), automatic reconnection with exponential backoff (1s-60s), QR code generation, `127.0.0.1` binding enforcement
- [ ] T013 [US1] Implement `src/server.ts` — Express HTTP server bound to `127.0.0.1` only, `GET /health` endpoint returning `{ status, connected, uptime }`, CORS disabled, server header removed

**Validation**: `ss -tlnp | grep node` shows listener on `127.0.0.1:PORT` only. Auth state file is created in `config/whatsapp/auth/`. QR code is logged if no auth state exists.

### Tests for Phase 2

- [ ] T014 [P] [US1] Unit test: config loading with valid/invalid YAML, env var override, missing file handling in `tests/unit/config.test.ts`
- [ ] T015 [P] [US1] Unit test: baileys socket initialization logic (mock baileys, verify auth state load, verify reconnect backoff) in `tests/unit/bridge.test.ts`
- [ ] T016 [P] [US1] Integration test: server binds to 127.0.0.1 only, healthcheck returns 200 from localhost and fails from external IP in `tests/integration/server.test.ts`

**Checkpoint**: Bridge core running securely with loopback binding. Next: message filtering and allowlist.

---

## Phase 3: Message Filtering and Privacy (US2, Priority: P1)

**Purpose**: Implement contact allowlist and message content filtering. No message from unknown contacts is ever processed.

- [ ] T017 [US2] Implement `src/allowlist.ts` — load allowlist from YAML, E.164 normalization, O(1) lookup via Set, `isAuthorized(contact: string): boolean`, fail-closed (empty allowlist = all blocked)
- [ ] T018 [US2] Implement `src/filters.ts` — message size check (reject >4096 chars text), media type filtering, body content validation (reject binary non-UTF8), `passesFilters(message): { ok: boolean, reason?: string }`
- [ ] T019 [US2] Integrate allowlist + filters into `src/bridge.ts` — on incoming message: check allowlist → check filters → log at DEBUG if rejected → silently drop

**Validation**: Message from unauthorized contact: logged at DEBUG, no webhook call, no storage. Message from authorized contact with oversized body: logged as WARN, not forwarded. Message from authorized contact with normal text: forwarded to webhook.

### Tests for Phase 3

- [ ] T020 [P] [US2] Unit test: allowlist matching (E.164 normalization, case sensitivity, empty allowlist, reload after SIGHUP) in `tests/unit/allowlist.test.ts`
- [ ] T021 [P] [US2] Unit test: content filters (max size, binary rejection, media type) in `tests/unit/filters.test.ts`
- [ ] T022 [P] [US2] Integration test: end-to-end message flow with mocked baileys (authorized→forwarded, unauthorized→dropped, oversized→rejected) in `tests/integration/message-flow.test.ts`

**Checkpoint**: Message privacy guaranteed — only authorized, well-formed messages reach the processing pipeline.

---

## Phase 4: Webhook Authentication and Delivery (US3, Priority: P1)

**Purpose**: All webhook endpoints are authenticated with a rotating API key using constant-time comparison.

- [ ] T023 [US3] Implement `src/auth.ts` — API key loading (env var > file > auto-generate), constant-time comparison via `crypto.timingSafeEqual`, key rotation detection on SIGHUP, `validateApiKey(header: string): boolean`
- [ ] T024 [US3] Implement `src/webhook.ts` — HTTPS POST to n8n webhook URL with JSON body `{ from, body, timestamp, message_id, contact_name }`, timeout (default 30s), retry with exponential backoff (3 attempts: 10s/30s/60s), TLS certificate validation
- [ ] T025 [US3] Add API key middleware to `src/server.ts` — all endpoints except `/health` require `X-API-Key` header, return 401 with `{ error: "unauthorized" }` on failure, log at WARN with source IP

**Validation**: Request with no/missing/expired key → 401 logged as WARN. Request with valid key → forwarded to webhook. Webhook timeout → retried 3 times then logged as ERROR.

### Tests for Phase 4

- [ ] T026 [P] [US3] Unit test: API key validation (valid key, invalid key, empty header, timing attack resistance, rotation detection) in `tests/unit/auth.test.ts`
- [ ] T027 [P] [US3] Unit test: webhook delivery (success, timeout, retry exhaustion, TLS failure) with mocked HTTPS in `tests/unit/webhook.test.ts`
- [ ] T028 [P] [US3] Integration test: full request lifecycle (auth→webhook→response) in `tests/integration/api-auth.test.ts`

**Checkpoint**: All webhook endpoints authenticated. Message delivery secure.

---

## Phase 5: Rate Limiting and Abuse Prevention (US6, Priority: P2)

**Purpose**: Protect against abuse with per-contact and global rate limits.

- [ ] T029 [US6] Implement `src/rate-limiter.ts` — sliding window rate limiter (per-contact and global), configurable window size and max messages, temporary block after N violations, O(1) cleanup strategy for expired windows

**Validation**: 12 messages in 60s from one contact → messages 11-12 queued. Contact blocked after 3 violations in 10 minutes → all messages dropped for 5 minutes. Rate limit events logged.

### Tests for Phase 6 — actually Phase 5

- [ ] T030 [P] [US6] Unit test: rate limiter (single contact under/over limit, global limit, violation tracking, block/unblock, window expiry) in `tests/unit/rate-limiter.test.ts`
- [ ] T031 [P] [US6] Integration test: rate-limited message flow (contact blocked, message queued, block expiry) in `tests/integration/rate-limiter.test.ts`

**Checkpoint**: Rate limiting active and verified.

---

## Phase 6: Keyword Routing and n8n Integration (US4 + US5, Priority: P2)

**Purpose**: Route authorized messages to n8n webhooks based on keyword matching. Support onboarding and content delivery workflows.

- [ ] T032 [US4/US5] Implement `src/router.ts` — keyword → webhook URL mapping loaded from config, longest-prefix keyword matching, fallback webhook for unmatched keywords, `route(message): WebhookTarget | null`
- [ ] T033 [US4/US5] Integrate router into message processing pipeline in `src/bridge.ts`: allowlist ✓ → filters ✓ → rate limit ✓ → route → webhook → log result
- [ ] T034 [US4/US5] Implement n8n workflow webhook receiver: POST endpoint at `/webhook/whatsapp` that accepts n8n callbacks (workflow results), translates them to WhatsApp message sends via baileys `sendMessage`
- [ ] T035 [US4/US5] Add n8n workflow templates in `config/n8n/`: `onboarding.json` (profile collection, storage, confirmation) and `content-delivery.json` (content lookup, permission check, send)
- [ ] T036 [US4/US5] Implement outbound message queue in `src/bridge.ts`: queue messages when baileys is disconnected, flush on reconnect, max queue size 1000

**Validation**: Send "start" from authorized contact → n8n onboarding workflow fires → confirmation received. Send "audio" → content workflow fires → audio file or link received. Unmatched keyword → fallback response.

### Tests for Phase 6

- [ ] T037 [P] [US4/US5] Unit test: keyword routing (exact match, prefix match, case insensitive, fallback, no match) in `tests/unit/router.test.ts`
- [ ] T038 [P] [US4/US5] Integration test: full pipeline (message→router→webhook→response) with mocked n8n endpoints in `tests/integration/pipeline.test.ts`

**Checkpoint**: Onboarding and content delivery workflows functional.

---

## Phase 7: Error Handling and Logging (US7, Priority: P3)

**Purpose**: Comprehensive error handling and structured logging for all bridge operations.

- [ ] T039 [US7] Add centralized error handling to `src/server.ts` — catch-all error middleware, structured error response, correlation ID propagation
- [ ] T040 [US7] Add logging throughout all bridge components: config load events (INFO), connection state changes (INFO/WARN), message flow tracing (DEBUG), security events (WARN+), errors (ERROR/CRITICAL)
- [ ] T041 [US7] Implement log rotation in `src/logger.ts` — 10MB max file size, 5 rotated files, compression for archived logs, hourly DEBUG rotation with 24h retention
- [ ] T042 [US7] Add startup validations in `src/index.ts`: verify config file exists, verify allowlist is non-empty (WARN if empty), verify API key is set, verify webhook URLs are HTTPS, verify port is available

**Validation**: Each error condition produces a structured log with correlation_id, severity, component, message. Log rotation creates new files at size threshold. Startup validations emit clear error messages.

### Tests for Phase 7

- [ ] T043 [P] [US7] Unit test: log output format (structured JSON, severity, correlation ID, component name) in `tests/unit/logger.test.ts`
- [ ] T044 [P] [US7] Integration test: log file rotation (force rotation by size, verify file count, verify compression) in `tests/integration/logger-rotation.test.ts`

**Checkpoint**: Comprehensive logging operational.

---

## Phase 8: Security Hardening and Polish

**Purpose**: Final security review, documentation, and quality gates.

- [ ] T045 [P] Security review: verify no secrets in logs (scan test logs for API key leaks), verify `helmet` middleware applied, verify no CORS headers leak, verify `X-Powered-By` removed
- [ ] T046 [P] Add rate limit and allowlist metrics to healthcheck endpoint (`GET /health`) — return `{ status: "ok", connected: true, uptime: 3600, allowlist_count: 5, blocked_contacts: 1 }`
- [ ] T047 [P] Create PM2 startup script: `pm2 start services/whatsapp-bridge/ecosystem.config.js --env production`, add to JARVIS startup sequence
- [ ] T048 [P] Create n8n workflow documentation in `config/n8n/README.md` — webhook URLs, expected payload format, authentication, error responses
- [ ] T049 [P] Final code cleanup: remove unused imports, verify all TypeScript strict mode checks pass, run linter
- [ ] T050 [P] Create manual E2E test script `tests/e2e/manual.md` — QR scan, send test messages, verify logging, rotate API key, verify rate limiting, simulate disconnect

**Checkpoint**: Production-ready WhatsApp bridge with all security and automation features.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Bridge Core (Phase 2)**: Depends on Setup — BLOCKS everything else
- **Message Filtering (Phase 3)**: Depends on Phase 2 (needs running bridge)
- **Webhook Auth (Phase 4)**: Depends on Phase 2 (needs server); can run in parallel with Phase 3
- **Rate Limiting (Phase 5)**: Depends on Phase 2; can run in parallel with Phases 3-4
- **Keyword Routing (Phase 6)**: Depends on Phases 3-4-5 (needs filtering + auth + rate limiting working)
- **Error Handling (Phase 7)**: Depends on Phases 2-3-4-5-6 (needs all components to add logging); can start in parallel with Phase 6
- **Polish (Phase 8)**: Depends on all phases complete

### User Story Dependencies

- **US1 (P1)**: Bridge core — no dependencies beyond Phase 1
- **US2 (P1)**: Message filtering — depends on US1 (needs running bridge)
- **US3 (P1)**: Webhook auth — depends on US1 (needs server); independent of US2
- **US6 (P2)**: Rate limiting — depends on US1; independent of US2/US3
- **US4 (P2)**: Client onboarding — depends on US2 + US3 + US6 (needs filtering, auth, rate limiting)
- **US5 (P2)**: Content delivery — depends on US2 + US3 + US6; can be parallel with US4
- **US7 (P3)**: Error handling — depends on all other stories

### Parallel Opportunities

- Phase 3, 4, 5 can run in parallel after Phase 2
- Phase 6 and 7 can run in parallel
- All [P] tasks within a phase can run in parallel
- n8n workflow templates (T035) can be developed independently of the bridge code

---

## Implementation Strategy

### MVP First (US1 + US2 + US3 = Secure Bridge)

1. Phase 1: Setup
2. Phase 2: Bridge Core (baileys, server, loopback, auth state)
3. Phase 3: Message Filtering (allowlist, content filters)
4. Phase 4: Webhook Auth (API key, webhook delivery)
5. **STOP & VALIDATE**: Full security perimeter tested

### Incremental Delivery

1. Setup + Core + Filtering + Auth → secure bridge running (MVP!)
2. Add Rate Limiting → abuse protection active
3. Add Keyword Routing + n8n workflows → automation live
4. Add Error Handling + logging polish → production-ready
5. Security review + E2E tests → ship

---

## Notes

- **Security-first**: every feature passes through allowlist → auth → rate limit before reaching n8n
- **Fail-closed**: empty allowlist = all messages blocked, not all allowed
- **Ephemeral content**: bridge stores nothing; n8n is responsible for any data persistence
- **[P] tasks**: different files, no dependencies
- **[Story] label**: maps task to user story for traceability
- n8n webhook payload format is documented in `config/n8n/README.md` (T048)
- PM2 manages the bridge as `whatsapp-bridge` service; part of JARVIS service group
