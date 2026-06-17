---
description: "Task list for Hermes One — Potencial Máximo"
---

# Tasks: Hermes One — Potencial Máximo

**Input**: Design documents from `specs/005-hermes-potencial-maximo/`

**Prerequisites**: plan.md ✅, spec.md ✅

**Organization**: Tasks grouped by phase (priority order from plan.md)

## Format: `[ID] [P?] [Phase] Description`
- **[P]**: Can run in parallel
- **[Phase]**: Phase the task belongs to

---

## Phase 1: Foundation — Config Migration + Gateway (US1, US6)

- [ ] T001 Run `hermes config migrate` to update v28 → v29
- [ ] T001a [P] Run `hermes config check` to identify missing settings
- [ ] T002 Configure `approvals.mode: smart` for balanced UX
- [ ] T003 Set `streaming.enabled: true` for real-time token streaming
- [ ] T004 [P] Backup current config.yaml to specs/005-hermes-potencial-maximo/contracts/
- [ ] T005 Install gateway as systemd service: `hermes gateway install --system`
- [ ] T006 Verify gateway auto-starts: `systemctl --user status hermes-gateway`
- [ ] T007 Verify Telegram + WhatsApp reconnect after gateway restart

---

## Phase 2: Web Search + Browser (US1)

- [ ] T008 Install DuckDuckGo search: `pip install ddgs`
- [ ] T009 Enable web-ddgs plugin: `hermes plugins enable web-ddgs`
- [ ] T010 Install Chromium browser: `sudo apt install -y chromium-browser`
- [ ] T011 Configure browser engine: `hermes config set browser.engine auto`
- [ ] T012 Test web search: ask Hermes to search for something
- [ ] T013 Test browser: ask Hermes to open a URL

---

## Phase 3: Voice STT/TTS (US1)

- [ ] T014 Install faster-whisper: `pip install faster-whisper`
- [ ] T015 Configure STT: `hermes config set stt.enabled true`
- [ ] T016 Set STT provider: `hermes config set stt.provider local`
- [ ] T017 Set STT model: `hermes config set stt.local.model base`
- [ ] T018 Test voice: send voice message in Telegram, verify transcription

---

## Phase 4: Multi-Profile + Kanban (US3)

- [ ] T019 List existing profiles: `hermes profile list`
- [ ] T020 Create worker profile: `hermes profile create worker --clone default`
- [ ] T021 Create cron profile: `hermes profile create cron --clone default`
- [ ] T022 Create research profile: `hermes profile create research --clone default`
- [ ] T023 Initialize kanban board: `hermes kanban init`
- [ ] T024 Configure kanban dispatcher settings in config.yaml
- [ ] T025 Test kanban: create a task assigned to worker profile
- [ ] T026 Test cross-profile: complete task from worker, verify on orchestrator

---

## Phase 5: Memory + Cron (US4, US5)

- [ ] T027 Verify memory is enabled: `hermes config set memory.memory_enabled true`
- [ ] T028 Enable user profile: `hermes config set memory.user_profile_enabled true`
- [ ] T029 Test memory: save a fact, start new session, verify recall
- [ ] T030 Create health-monitor cron: every 30min checks service status
- [ ] T031 Create system-resources cron: every 1h reports disk/mem usage
- [ ] T032 Create jarvish-heartbeat cron: every 15min checks JARVIS status
- [ ] T033 List cron jobs: `hermes cron list` — verify all 3 active

---

## Phase 6: Models & Providers — Fallback (US2)

- [ ] T034 Configure fallback model with OpenRouter (or another free provider)
- [ ] T035 Configure auxiliary vision model: `hermes config set auxiliary.vision.provider auto`
- [ ] T036 Configure auxiliary compression settings (already configured, verify)
- [ ] T037 Test fallback: temporarily block primary, verify automatic failover
- [ ] T038 Configure model catalog: verify `model_catalog.enabled: true`

---

## Phase 7: Final Polish (US1-US6)

- [ ] T039 Verify `security.redact_secrets: true`
- [ ] T040 Configure streaming settings (buffer_threshold, edit_interval)
- [ ] T041 Run full health check: `hermes doctor`
- [ ] T042 Verify JARVIS MCP bridge reconnects after gateway restart
- [ ] T043 Run all US acceptance tests from spec.md
- [ ] T044 Update checklists/phase*.md with completion notes
- [ ] T045 Commit spec to git: `cd ~/jarvis && git add specs/005-hermes-potencial-maximo/ && git commit -m "feat: spec 005 — Hermes Potencial Máximo"`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Foundation)**: No dependencies — start immediately
- **Phase 2 (Web Search)**: Depends on Phase 1 (config migration first)
- **Phase 3 (Voice)**: Depends on Phase 1
- **Phase 4 (Kanban)**: Depends on Phase 1
- **Phase 5 (Memory/Cron)**: Depends on Phase 1
- **Phase 6 (Fallback)**: Depends on Phase 1
- **Phase 7 (Polish)**: Depends on Phase 1-6

### Parallel Opportunities
- Phases 2, 3, 4, 5, 6 can all run in parallel after Phase 1
- All [P] tasks within each phase run in parallel

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

- [X] T056 Crear sistema de comunicacion entre agentes (AgentOrchestrator)
- [X] T057 Voice assistant pipeline completo (edge-tts, interactive mode)
