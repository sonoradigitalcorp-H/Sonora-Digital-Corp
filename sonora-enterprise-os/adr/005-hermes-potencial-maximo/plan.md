# Implementation Plan: Hermes One — Potencial Máximo

**Branch**: `005-hermes-potencial-maximo` | **Date**: 2026-06-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/005-hermes-potencial-maximo/spec.md`

## Summary

Full optimization of the Hermes One ecosystem across 7 domains: Desktop/Office, Models/Providers, Kanban, Memory, Cron, Gateway, and Security. The implementation follows a phased approach where higher-priority items (Desktop, Gateway, Models) are completed first, followed by automation features (Kanban, Cron, Memory).

## Technical Context

**Language/Version**: Python 3.11+, Hermes Agent v0.16.0
**Primary Dependencies**: Hermes CLI tools, systemd, Electron app, DuckDuckGo (ddgs), faster-whisper, Linear MCP OAuth
**Storage**: SQLite (sessions, kanban, memory), filesystem (skills, config)
**Testing**: hermes doctor, manual verification per acceptance scenario
**Target Platform**: Ubuntu 24.04 (Wayland), external monitor 1920x1080
**Performance Goals**: Gateway response < 10s, cron precision ±30s, kanban dispatch < 60s
**Constraints**: opencode-go as primary provider (no-cost), deepseek-v4-flash as primary model

## Constitution Check

| Principle | Compliance | Status |
|-----------|-----------|--------|
| **I. Separación de Responsabilidades** | All configuration is deterministic (config.yaml, .env). LLM used only for response generation. Kanban routing is tool-based, not LLM-decided. | ✅ PASS |
| **II. Privacidad y Control Local** | All data local (SQLite, Obsidian vault, memory). Only LLM API calls go external (opencode-go). | ✅ PASS |
| **III. Arquitectura Modular** | Each component (gateway, kanban, cron, memory) is independently configurable. Profiles isolate concerns. | ✅ PASS |
| **IV. Calidad y Testing** | Each US has independent tests. hermes doctor validates config. Manual acceptance scenarios defined. | ✅ PASS |
| **V. Spec-Driven Development** | This spec + plan + tasks + checklist follow SDD. | ✅ PASS |

**Result**: PASS. No violations.

## Project Structure

```text
specs/005-hermes-potencial-maximo/
├── spec.md              # This feature specification
├── plan.md              # This implementation plan
├── tasks.md             # Implementation tasks
├── checklist.md         # Quality checklist
├── contracts/           # API contracts (if applicable)
└── checklists/          # Per-phase checklists

Implementation touches:
├── ~/.hermes/config.yaml         # Main config
├── ~/.hermes/.env                # Secrets
├── ~/.hermes/hermes-agent/       # Source (read-only)
├── ~/jarvis/                     # JARVIS integration
└── /etc/systemd/user/            # Systemd services
```

## Implementation Strategy

### Phase 1: Foundation — Config Migration + Gateway Systemd (US1, US6)
1. `hermes config migrate` to v29
2. Optimize config.yaml: approvals smart mode, delegation config, streaming
3. Install gateway as systemd service (`hermes gateway install --system`)
4. Verify gateway auto-starts and Telegram/WhatsApp reconnect

### Phase 2: Web Search + Browser (US1)
1. Install ddgs (`pip install ddgs`)
2. Enable web-ddgs plugin
3. Install Chromium for local browser backend
4. Configure browser engine

### Phase 3: Voice STT/TTS (US1)
1. Install faster-whisper (`pip install faster-whisper`)
2. Configure STT with local provider
3. Test voice pipeline end-to-end

### Phase 4: Kanban + Multi-Profile (US3)
1. Create additional profiles (worker, research, cron)
2. Initialize kanban board
3. Configure dispatcher settings
4. Test cross-profile task lifecycle

### Phase 5: Memory + Cron (US4, US5)
1. Configure memory provider and user profile
2. Create health-monitor cron job
3. Create system-resource cron job
4. Validate persistence across sessions

### Phase 6: Models & Providers — Fallback (US2)
1. Configure fallback model/provider
2. Configure auxiliary models (vision, compression)
3. Test failover scenario

### Phase 7: Final Polish (All US)
1. Security settings (redact secrets, approvals)
2. Streaming configuration
3. Full system health check
4. JARVIS bridge sync

## Success Criteria

- [ ] `hermes doctor` passes with no warnings
- [ ] All 6 US acceptance scenarios verified
- [ ] Gateway runs as systemd, survives reboot
- [ ] Web search works (DuckDuckGo)
- [ ] Voice input/output works (faster-whisper + Edge TTS)
- [ ] Kanban board operational with 2+ profiles
- [ ] Memory persists across sessions
- [ ] Cron jobs fire on schedule
- [ ] Fallback provider engages on primary failure
- [ ] All edge cases handled gracefully
