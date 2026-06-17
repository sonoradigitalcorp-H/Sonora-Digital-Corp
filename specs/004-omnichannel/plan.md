# Implementation Plan: Omnichannel Communication

**Branch**: `004-omnichannel` | **Date**: 2026-06-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/004-omnichannel/spec.md`

## Summary

Multi-channel communication system: WhatsApp Business API, Telegram bot, Web UI with voice (Web Speech API), PSTN voice calls, and MCP bridges for external system integration. All channels route through the same orchestrator for consistent responses.

## Technical Context

**Language/Version**: Python 3.11+, JavaScript/TypeScript (web UI)

**Primary Dependencies**: FastAPI, WhatsApp Business API, python-telegram-bot, Twilio (voice calls), Web Speech API, MCP SDK

**Storage**: Redis (session cache, rate limits, queues), PostgreSQL (message history)

**Testing**: pytest with mocked channel APIs, Web Speech API mock in Playwright, MCP client test suite

**Target Platform**: Linux server, web browser (Chrome/Edge/Safari), mobile (WhatsApp/Telegram native apps)

**Project Type**: Multi-channel messaging server with REST + MCP interfaces

**Performance Goals**: WhatsApp response < 5s, Telegram response < 3s, voice E2E < 5s, MCP tool call < 2s

**Constraints**: Meta 15s webhook timeout for WhatsApp, Telegram 30 msg/s rate limit, Web Speech API browser-dependent

**Scale/Scope**: < 1000 conversations/day, < 5 channels, < 50 concurrent MCP connections

## Constitution Check

| Principle | Compliance | Status |
|-----------|-----------|--------|
| **I. Separación de Responsabilidades** | Channel adapters are thin: receive message → normalize → send to orchestrator → format response. All channel logic is deterministic Python. LLM only in orchestrator response generation. | ✅ PASS |
| **II. Privacidad y Control Local** | Message history stored locally. WhatsApp/Telegram messages processed through configured APIs. No data sent to unauthorized third parties. | ✅ PASS |
| **III. Arquitectura Modular** | Each channel is an independent adapter. Add new channel = new adapter file. MCP is the extension mechanism. | ✅ PASS |
| **IV. Calidad y Testing** | Each channel adapter tested independently with mocked external APIs. Integration test with real orchestrator. Webhook validation tests. | ✅ PASS |
| **V. Documentación** | Channel configuration documented. Webhook setup guides. MCP tool documentation auto-generated. | ✅ PASS |

**Result**: PASS. No violations.

## Project Structure

```text
specs/004-omnichannel/
├── plan.md              # This file
├── spec.md              # Feature specification
├── tasks.md             # Implementation tasks
├── checklists/          # Quality checklists
└── contracts/           # API contracts

src/
├── channels/            # Channel adapters
│   ├── whatsapp.py      # WhatsApp Business API adapter
│   ├── telegram.py      # Telegram bot adapter
│   ├── webui.py         # Web UI (SSE + voice)
│   └── voice.py         # PSTN voice call adapter (Twilio)
├── mcp/                 # MCP server
│   ├── server.py        # MCP server (tools/list, tools/call)
│   └── tools.py         # Tool definitions exposed via MCP
├── message/             # Message handling
│   ├── normalizer.py    # Normalize messages to unified format
│   ├── formatter.py     # Channel-specific response formatting
│   └── session.py       # Cross-channel session management
└── api/                 # REST endpoints
```
