# Implementation Plan: WhatsApp Security and Automation Bridge

**Branch**: `023-whatsapp-security-automation` | **Date**: 2026-06-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/023-whatsapp-security-automation/spec.md`

## Summary

WhatsApp bridge for JARVIS using `@whiskeysockets/baileys` (WhatsApp Web JS) with strict security: loopback-only binding, contact allowlist (fail-closed), rotating API key webhook auth, rate limiting, structured logging, and n8n workflow integration for client onboarding and content delivery. Message content is ephemeral — forwarded to n8n then discarded. JARVIS memory stores only metadata.

Enfoque técnico: bridge Node.js independiente, configuración YAML + env vars, webhooks hacia n8n local, persistencia de sesión cifrada, PM2 para gestión de procesos.

## Technical Context

**Language/Version**: Node.js 20 LTS (TypeScript 5.x)

**Primary Dependencies**: `@whiskeysockets/baileys` (WhatsApp Web JS), `express` (webhook HTTP server), `pino` (structured logging), `node:fs` + `node:crypto` (API key rotation, constant-time comparison), `node:http` (healthcheck), `yaml` (config parsing), `pm2` (process management).

**Storage**: File-based only. Encrypted baileys auth state on disk (`config/whatsapp/auth/`). YAML config files (`config/whatsapp/config.yaml`, `config/whatsapp/allowlist.yaml`). API key in `config/whatsapp/api_key.txt` (auto-generated if missing). No database dependency in the bridge itself (n8n may use its own DB).

**Testing**: Jest + ts-jest. Unit tests for rate limiter, allowlist, API key validation. Integration tests with mocked baileys socket. E2E tests against a test WhatsApp number (manual).

**Target Platform**: Linux server (Ubuntu 22.04+). Runs alongside JARVIS Hermes gateway and n8n. Systemd unit or PM2 process.

**Project Type**: Standalone Node.js service (npm package) within the JARVIS monorepo, in `services/whatsapp-bridge/`.

**Performance Goals**: Message processing <500ms p95 (bridge only, excluding n8n workflow time). 50 concurrent deliveries. 99.5% bridge uptime.

**Constraints**: Bind to `127.0.0.1` exclusively. Fail-closed on allowlist. No message content in persistent storage. No group chat processing unless explicitly configured. HTTPS webhooks only. Constant-time API key comparison.

**Scale/Scope**: Single WhatsApp number, single JARVIS instance. Client onboarding + content delivery as primary n8n workflows. ~5 webhook endpoints, ~200 lines of n8n workflow config per workflow type.

## Architecture Decisions

### Decision 1: Bridge as standalone Node.js process (not embedded in Hermes)

The WhatsApp bridge runs as a separate Node.js process from the JARVIS Python backend. Communication happens via n8n webhooks (not direct IPC).

**Rationale**: baileys is Node.js/TypeScript native. Embedding it in the Python Hermes gateway would require a subprocess or sidecar anyway. A standalone process with clear webhook contracts keeps the boundary clean, allows independent restart/reconnect without affecting JARVIS core, and follows the existing pattern of isolated services.

### Decision 2: File-based config with SIGHUP reload (no database)

Allowlist, API keys, and routing rules live in YAML/text files. On SIGHUP, the bridge re-reads all config files. No DB dependency in the bridge itself.

**Rationale**: Simpler than adding SQLite/Redis for config storage. n8n workflows have their own storage for client data. The bridge is stateless (except in-memory rate limiter state). Config changes are auditable via git for the allowlist and routing YAML.

### Decision 3: Message content is ephemeral — bridge stores nothing

The bridge forwards message data to n8n via POST, then discards it. Only metadata (from, timestamp, message_id) is available for logging. n8n workflows are responsible for any persistent storage of message content.

**Rationale**: Privacy by design. The bridge should not be a vector for message data leaks. If the n8n webhook is down, the message is retried and then discarded — there is no replay from bridge storage.

### Decision 4: Rate limiting in-memory (no Redis)

Rate limit state is in-memory only. On bridge restart, all rate counters reset.

**Rationale**: Rate limits are not critical state — a restart resets them naturally. Adding Redis adds operational complexity for this single concern. For v1, in-memory is adequate.

### Decision 5: PM2 for process management (not systemd directly)

PM2 manages the Node.js bridge process with automatic restart, log management, and cluster mode (if needed).

**Rationale**: PM2 provides log rotation, auto-restart on crash, graceful shutdown, and monitoring out of the box for Node.js apps. Systemd calls PM2, or PM2 runs as a systemd unit.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluación frente a la Constitución de JARVIS v1.0:

| Principio | Cómo lo cumple el diseño | Estado |
|-----------|--------------------------|--------|
| **1. Separación de Responsabilidades** | Bridge Node.js independiente del backend Python. Comunicación vía webhooks HTTP (no acoplamiento directo). n8n es el orquestador de workflows; el bridge solo rutea mensajes. | ✅ PASS |
| **2. Privacidad y Control** | Todo local (baileys local, n8n local, webhooks localhost). Message content ephemeral — no se almacena en JARVIS. Fail-closed allowlist. Sin telemetría. | ✅ PASS |
| **3. Arquitectura Modular** | Bridge como servicio independiente PM2. Config file-based. Contrato webhook claro. n8n workflows desacoplados. | ✅ PASS |
| **4. Calidad y Testing** | Jest tests para allowlist, rate limiter, API key auth. Integration tests con baileys mockeado. Gate de cobertura >80%. | ✅ PASS |
| **5. Documentación** | Spec SDD completo en `specs/023-whatsapp-security-automation/`. Contratos webhook documentados. Config YAML con comentarios. | ✅ PASS |

**Resultado**: PASS. No se requieren entradas en Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/023-whatsapp-security-automation/
├── plan.md              # This file
├── spec.md              # Full specification
├── research.md          # WhatsApp Business API vs baileys + security
├── data-model.md         # Key entities
├── checklist.md          # Quality checklist
└── tasks.md             # Implementation tasks
```

### Source Code (repository root)

```text
services/whatsapp-bridge/
├── src/
│   ├── index.ts                  # Entry point: start bridge, load config
│   ├── bridge.ts                 # Baileys socket management, reconnection, auth
│   ├── config.ts                 # YAML + env config loader with SIGHUP reload
│   ├── allowlist.ts              # Contact allowlist (fail-closed, E.164)
│   ├── auth.ts                   # API key management (rotation, constant-time compare)
│   ├── rate-limiter.ts           # Per-contact + global rate limiter (in-memory)
│   ├── webhook.ts                # Webhook delivery (HTTPS POST, retry, timeout)
│   ├── router.ts                 # Keyword → webhook target routing
│   ├── server.ts                 # Express HTTP server (healthcheck, admin, webhook receiver)
│   ├── logger.ts                 # Structured pino logger with correlation IDs
│   ├── filters.ts                # Message content filtering (size, type)
│   └── types.ts                  # TypeScript types for all entities
├── config/
│   └── whatsapp/
│       ├── config.yaml           # Main config (rate limits, ports, webhooks)
│       ├── allowlist.yaml        # Authorized contacts (E.164)
│       └── api_key.txt           # Auto-generated API key (gitignored)
├── tests/
│   ├── unit/
│   │   ├── allowlist.test.ts
│   │   ├── auth.test.ts
│   │   ├── rate-limiter.test.ts
│   │   └── filters.test.ts
│   ├── integration/
│   │   ├── bridge.test.ts        # Mocked baileys socket
│   │   └── webhook.test.ts       # Mocked n8n endpoints
│   └── e2e/
│       └── manual.md             # Manual E2E test instructions
├── package.json
├── tsconfig.json
├── .env.example
└── .gitignore
```

**Structure Decision**: Standalone Node.js service under `services/whatsapp-bridge/`. The bridge is independent of the Python backend but follows the same monorepo conventions. PM2 `ecosystem.config.js` at the monorepo root manages this and other services.

## Complexity Tracking

> No hay violaciones de la Constitución que justificar. Sección intencionadamente vacía.
