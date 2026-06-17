---
description: "Task list for Omnichannel Communication"
---

# Tasks: Omnichannel Communication

**Input**: Design documents from `specs/004-omnichannel/`

**Prerequisites**: plan.md ✅, spec.md ✅

**Organization**: Tasks grouped by user story (priority order from spec.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: User story the task belongs to (US1–US5)

---

## Phase 1: Infrastructure

- [ ] T001 Set up Redis for session cache, rate limits, and message queues
- [ ] T002 [P] Set up PostgreSQL for message history
- [ ] T003 [P] Create unified message schema (channel, content, media, session, metadata)
- [ ] T004 [P] Create FastAPI backend with webhook endpoints per channel
- [ ] T005 [P] Create channel adapter interface (send/receive, normalize, format)

---

## Phase 2: User Story 1 - WhatsApp (Priority: P1) 🎯 MVP

- [ ] T006 Implement WhatsApp Business API webhook receiver in src/channels/whatsapp.py
- [ ] T007 [P] Implement message normalization (text, image, audio, document → unified format)
- [ ] T008 [P] Implement session management (persist context across messages)
- [ ] T009 [P] Implement response formatting (rich text, quick replies, list messages)
- [ ] T010 [P] Implement 15-second processing timeout (send "processing" placeholder)
- [ ] T011 [P] Unit tests for WhatsApp adapter with mocked API
- [ ] T012 [P] Integration test: receive webhook → process → send response

---

## Phase 3: User Story 2 - Telegram (Priority: P1)

- [ ] T013 Implement Telegram bot in src/channels/telegram.py (polling or webhook)
- [ ] T014 [P] Implement command handling (/start, /help, custom commands)
- [ ] T015 [P] Implement inline query support
- [ ] T016 [P] Implement group chat mention handling (@botname)
- [ ] T017 [P] Implement rich media support (photos, documents, voice)
- [ ] T018 [P] Implement rate limit queuing (30 msg/s limit)
- [ ] T019 [P] Unit tests for Telegram adapter with mocked API
- [ ] T020 [P] Integration test: send message → process → receive response

---

## Phase 4: User Story 3 - Web UI Voice (Priority: P2)

- [ ] T021 Implement Speech-to-Text via Web Speech API in web UI
- [ ] T022 [P] Implement Text-to-Speech via Web Speech API in web UI
- [ ] T023 [P] Implement real-time transcription display during STT
- [ ] T024 [P] Implement three-panel responsive layout (workspace, chat, tools)
- [ ] T025 [P] Implement graceful degradation to text-only when Web Speech API unavailable
- [ ] T026 [P] Unit tests for voice components with mocked Speech API
- [ ] T027 [P] Integration test: voice input → STT → orchestrator → TTS → audio output

---

## Phase 5: User Story 4 - Voice Calls (Priority: P3)

- [ ] T028 Implement Twilio webhook receiver for incoming calls in src/channels/voice.py
- [ ] T029 [P] Implement STT/TTS pipeline for call audio
- [ ] T030 [P] Implement interruption handling (user speaks over JARVIS → stop + listen)
- [ ] T031 [P] Implement call session management (transcript, resume on callback)
- [ ] T032 [P] Unit tests for voice call adapter with mocked Twilio

---

## Phase 6: User Story 5 - MCP Bridges (Priority: P2)

- [ ] T033 Implement MCP server in src/mcp/server.py (initialize, tools/list, tools/call)
- [ ] T034 [P] Implement tool definitions for all exposed capabilities
- [ ] T035 [P] Implement concurrent connection handling with session isolation
- [ ] T036 [P] Implement structured error responses for invalid parameters
- [ ] T037 [P] Implement session resume on reconnection
- [ ] T038 [P] Unit tests for MCP server with real MCP client

---

## Phase 7: Cross-Channel Integration

- [ ] T039 Implement cross-channel session deduplication (same user on WhatsApp + Telegram)
- [ ] T040 [P] Implement unified message formatter (channel-specific markdown, plain text for voice)
- [ ] T041 [P] Implement channel health monitoring (webhook liveness, API status)
- [ ] T042 [P] Full E2E test: message enters via all channels → orchestrator → formatted response per channel

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Infrastructure)**: No dependencies — start immediately
- **Phase 2 (WhatsApp)**: Depends on Phase 1
- **Phase 3 (Telegram)**: Depends on Phase 1
- **Phase 4 (Web Voice)**: Depends on spec 001 core orchestrator
- **Phase 5 (Voice Calls)**: Depends on Phase 4 (STT/TTS)
- **Phase 6 (MCP)**: Depends on Phase 1
- **Phase 7 (Integration)**: Depends on all channels functional

### Parallel Opportunities

- Phase 2, Phase 3, Phase 4, Phase 6 can all run in parallel after Phase 1
- Phase 5 depends on Phase 4
- All [P] tasks within each phase run in parallel

---

## Implementation Strategy

1. Phase 1: Infrastructure → Redis + Postgres + message schema + adapter interface
2. Phase 2: WhatsApp → highest-engagement channel MVP (US1)
3. Phase 3: Telegram → second channel MVP (US2)
4. Phase 4: Web Voice → voice interface (US3)
5. Phase 5: Voice Calls → phone channel (US4)
6. Phase 6: MCP Bridges → extensibility (US5)
7. Phase 7: Cross-channel Integration → unification

---

## Current Status

- [ ] Phase 1: Not started
- [ ] Phase 2: Not started
- [ ] Phase 3: Not started
- [ ] Phase 4: Not started
- [ ] Phase 5: Not started
- [ ] Phase 6: Not started
- [ ] Phase 7: Not started


## Session 2026-06-12: AzREC + Content Pipeline + Telegram

- [X] T050 Crear Telegram bot AzREC con asistente de ventas y catalogo
- [X] T051 Crear Telegram bot Abe Music con showcase de artistas
- [X] T052 Crear Telegram masterclass (9 modulos: fundamentos a PRO)
