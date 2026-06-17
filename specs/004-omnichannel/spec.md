# Feature Specification: Omnichannel Communication

**Feature Branch**: `004-omnichannel`

**Created**: 2026-06-10

**Status**: Draft

**Input**: Multi-channel communication system: WhatsApp integration, Telegram bot, Web UI with voice (Web Speech API), voice call interface, and MCP bridges for external systems.

## User Scenarios & Testing

### User Story 1 - WhatsApp messaging (Priority: P1)

The user sends and receives messages via WhatsApp, with full conversational context, rich media support (images, audio, documents), and session management.

**Why this priority**: WhatsApp is the highest-engagement channel in LatAm. Without it, reach is limited.

**Independent Test**: Send a WhatsApp message to the business number, verify the response comes within 5 seconds with correct context.

**Acceptance Scenarios**:

1. **Given** a user sends a WhatsApp message, **When** the webhook receives it, **Then** JARVIS processes and responds via WhatsApp API within 5 seconds.
2. **Given** a multi-turn conversation, **When** the user sends follow-up messages, **Then** JARVIS maintains session context across messages.
3. **Given** an image sent via WhatsApp, **When** received, **Then** JARVIS processes it (OCR if needed) and responds appropriately.
4. **Given** a document sent, **When** processed, **Then** JARVIS extracts text and responds with the content summary.

---

### User Story 2 - Telegram bot (Priority: P1)

The user interacts via Telegram bot with full command support, inline queries, rich media, and group chat capabilities.

**Why this priority**: Telegram offers superior API capabilities for rich interactions. Equal priority to WhatsApp for reach.

**Independent Test**: Start the Telegram bot, send "/start", verify the welcome message. Send a question, verify the response.

**Acceptance Scenarios**:

1. **Given** a user starts the Telegram bot, **When** they send /start, **Then** the bot responds with a welcome message and available commands.
2. **Given** a user sends a text message, **When** the bot receives it, **Then** it processes and responds via Telegram API.
3. **Given** a group chat with the bot, **When** mentioned with @botname or command, **Then** it responds in the group.
4. **Given** an inline query, **When** a user types @botname query, **Then** inline results appear without leaving the chat.

---

### User Story 3 - Web UI with voice (Priority: P2)

The user interacts via web browser with a three-panel interface and voice input/output via Web Speech API (Speech-to-Text + Text-to-Speech).

**Why this priority**: Voice is the most natural interface. Depends on Web UI existing. Differentiator vs. text-only bots.

**Independent Test**: Open the web UI in Chrome, click the microphone button, speak a question, verify STT captures it and JARVIS responds with TTS audio.

**Acceptance Scenarios**:

1. **Given** the web UI loaded, **When** the user clicks the microphone button, **Then** STT captures their speech with real-time transcription.
2. **Given** a voice input captured, **When** JARVIS generates a response, **Then** TTS reads it aloud while text appears in chat.
3. **Given** the three-panel layout, **When** the user resizes the browser, **Then** panels adapt (workspace, chat, tools).
4. **Given** voice input in a noisy environment, **When** background noise is high, **Then** STT still achieves >= 80% accuracy.

---

### User Story 4 - Voice calls (Priority: P3)

The user calls a phone number and speaks with JARVIS via voice call, with STT/TTS pipeline, session context, and call management.

**Why this priority**: Phone calls are the highest-effort but highest-trust channel. Depends on US3 voice components.

**Independent Test**: Call the configured phone number, speak "what can you help me with", verify JARVIS responds via voice with context.

**Acceptance Scenarios**:

1. **Given** an incoming call, **When** answered, **Then** JARVIS greets the caller and prompts them to speak.
2. **Given** a voice conversation, **When** the caller speaks, **Then** STT transcribes, orchestrator responds, TTS speaks the reply.
3. **Given** a caller interrupts, **When** they speak over JARVIS, **Then** JARVIS stops speaking and listens.
4. **Given** call quality issues, **When** audio is unclear, **Then** JARVIS asks for repetition gracefully.

---

### User Story 5 - MCP bridges to external systems (Priority: P2)

External systems (CRMs, ERPs, custom apps) connect to JARVIS via MCP protocol, accessing tools and agents programmatically.

**Why this priority**: MCP bridges make JARVIS extensible beyond the built-in channels. Depends on core MCP infrastructure (001).

**Independent Test**: Connect an MCP client to the JARVIS MCP server, list available tools, invoke a tool, verify the response.

**Acceptance Scenarios**:

1. **Given** an MCP client connecting, **When** it sends initialize, **Then** JARVIS responds with available tools and capabilities.
2. **Given** a tool invocation via MCP, **When** the tool executes, **Then** the result is returned via MCP response.
3. **Given** concurrent MCP connections, **When** multiple clients connect, **Then** each session is isolated.
4. **Given** an MCP connection drop, **When** the client reconnects, **Then** the session resumes from last checkpoint.

---

### Edge Cases

- **WhatsApp webhook timeout (>15s Meta limit)**: respond with "processing" placeholder, then follow up
- **Telegram rate limit (30 msg/s)**: queue outgoing messages, batch when possible
- **Web Speech API not supported (Firefox)**: graceful fallback to text-only chat
- **Voice call dropped mid-conversation**: save transcript, resume on next call
- **MCP client sends invalid tool params**: return validation error, not crash
- **Multi-channel conflict**: same user asks via WhatsApp and Telegram simultaneously — must detect duplicate and avoid double-response

## Requirements

### Functional Requirements

**WhatsApp**

- **FR-001**: The system MUST integrate with WhatsApp Business API via webhooks.
- **FR-002**: Incoming messages MUST be processed within 15 seconds (Meta timeout).
- **FR-003**: The system MUST support text, image, audio, and document messages.
- **FR-004**: Session context MUST persist across messages.

**Telegram**

- **FR-005**: The system MUST implement a Telegram Bot with command handling.
- **FR-006**: The bot MUST support inline queries and group chat mentions.
- **FR-007**: Rich media (photos, documents, voice) MUST be supported.

**Web UI voice**

- **FR-008**: The web UI MUST support Speech-to-Text via Web Speech API.
- **FR-009**: The web UI MUST support Text-to-Speech via Web Speech API.
- **FR-010**: Voice MUST gracefully degrade to text-only when API unavailable.

**Voice calls**

- **FR-011**: The system MUST answer incoming calls and process voice via STT/TTS pipeline.
- **FR-012**: Interrupt handling MUST allow user to speak over JARVIS.
- **FR-013**: Call sessions MUST save transcripts and auto-resume on callback.

**MCP bridges**

- **FR-014**: The system MUST expose an MCP server with tool listing and invocation.
- **FR-015**: Concurrent MCP connections MUST be supported with session isolation.
- **FR-016**: Invalid tool parameters MUST return structured validation errors.

**General**

- **FR-017**: All channels MUST route through the same orchestrator for consistent responses.
- **FR-018**: Channel-specific formatting MUST be applied (markdown for Telegram, plain text for voice).

### Key Entities

- **Channel**: communication medium (WhatsApp, Telegram, Web, Voice, MCP) with adapter
- **Message**: unified message format with channel metadata, content, media, and session ID
- **Session**: cross-channel conversation state with history and context
- **Webhook**: incoming message endpoint per channel with validation and rate limiting
- **VoiceCall**: call session with transcript, status, and resume token

## Success Criteria

### Measurable Outcomes

- **SC-001**: WhatsApp response within 5 seconds in >= 95% of cases (< 15s Meta limit).
- **SC-002**: Telegram bot response within 3 seconds in >= 95% of cases.
- **SC-003**: Web UI voice STT accuracy >= 85% in quiet environment.
- **SC-004**: Voice call end-to-end latency (speak → hear response) < 5 seconds.
- **SC-005**: MCP server handles 10 concurrent connections without degradation.
- **SC-006**: Zero channel outages due to unhandled adapter errors.

## Assumptions

- **WhatsApp Business API**: requires Meta-approved business account; assumes existing approval
- **Telegram Bot API**: no approval needed; create via @BotFather
- **Web Speech API**: works in Chrome, Edge, Safari; Firefox has limited STT support
- **Voice calls**: uses Twilio or similar for PSTN termination; assumes configured number
- **MCP**: follows MCP specification (initialize, tools/list, tools/call); JSON-RPC 2.0
- **Rate limits**: platforms enforce their own; we queue and respect retry-after headers
- **Single orchestrator**: all channels share the same orchestrator instance; horizontal scaling for high volume
