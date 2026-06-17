---
description: "Task list for Content Engine & Automation"
---

# Tasks: Content Engine & Automation

**Input**: Design documents from `specs/003-content-engine/`

**Prerequisites**: plan.md ✅, spec.md ✅

**Organization**: Tasks grouped by user story (priority order from spec.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: User story the task belongs to (US1–US5)

---

## Phase 1: Infrastructure

- [ ] T001 Deploy n8n in Docker with persistent workflow storage (SQLite)
- [ ] T002 [P] Set up PostgreSQL for content and schedule storage
- [ ] T002 [P] Set up MinIO/S3-compatible storage for media assets
- [ ] T003 [P] Create FastAPI backend for pipeline orchestration
- [ ] T004 [P] Create Next.js dashboard for content review and scheduling

---

## Phase 2: User Story 1 - n8n Workflows (Priority: P1) 🎯 MVP

- [ ] T005 [P] Create n8n workflow templates: timer trigger, webhook trigger, event trigger
- [ ] T006 [P] Create n8n workflow templates: content generation, social posting, notification
- [ ] T007 [P] Create error handling workflow template (retry with backoff, admin notification)
- [ ] T008 [P] Export all workflows as JSON to config/n8n/ for version control
- [ ] T009 [P] Add n8n healthcheck and auto-restart in Docker Compose

---

## Phase 3: User Story 2 - Content Pipeline (Priority: P1)

- [ ] T010 Implement content generator in src/content/generator.py (text via LLM, images via ComfyUI/API)
- [ ] T011 [P] Implement content review dashboard (edit, approve, reject, regenerate)
- [ ] T012 [P] Implement content scheduler (timestamp, platform, status)
- [ ] T013 [P] Implement content safety filter in src/content/safety.py (toxic/NSFW detection)
- [ ] T014 [P] Unit tests for content generator with mocked LLM
- [ ] T015 [P] Unit tests for safety filter
- [ ] T016 [P] Unit tests for scheduling logic

---

## Phase 4: User Story 3 - Video Pipeline (Priority: P2)

- [ ] T017 Implement video pipeline in src/content/video.py (script → TTS → footage → render)
- [ ] T018 [P] Integrate ElevenLabs API or local TTS for voiceover
- [ ] T019 [P] Implement subtitle overlay (SRT generation, FFmpeg burn-in)
- [ ] T020 [P] Implement platform-optimized export (9:16, 16:9, 1:1)
- [ ] T021 [P] Add footage selection logic (stock library or AI-generated)
- [ ] T022 [P] Unit tests for video pipeline (script → rendered MP4 checksum)
- [ ] T023 [P] Integration test: full video pipeline with real TTS (mocked footage)

---

## Phase 5: User Story 4 - Social Automation (Priority: P2)

- [ ] T024 [P] Implement Instagram publisher in src/social/instagram.py (Graph API, media upload)
- [ ] T025 [P] Implement TikTok publisher in src/social/tiktok.py (TikTok API, video upload)
- [ ] T026 [P] Implement YouTube publisher in src/social/youtube.py (Data API, video upload)
- [ ] T027 [P] Implement X/Twitter publisher in src/social/twitter.py (v2 API, media tweet)
- [ ] T028 [P] Implement LinkedIn publisher in src/social/linkedin.py (Share API, article post)
- [ ] T029 [P] Implement platform-specific formatting (hashtag count, image ratio, video length, char limit)
- [ ] T030 [P] Implement social post scheduler with queue and rate limit handling
- [ ] T031 [P] Unit tests for each publisher with mocked APIs
- [ ] T032 [P] Integration test: schedule post → verify it appears on mock platform

---

## Phase 6: User Story 5 - Agent CFO (Priority: P3)

- [ ] T033 Implement CFO dashboard in src/cfo/dashboard.py (revenue, costs, content performance, growth)
- [ ] T034 [P] Implement trend detection in src/cfo/analyst.py (revenue decline, content optimization)
- [ ] T035 [P] Implement recommendation engine (actionable suggestions from trends)
- [ ] T036 [P] Add CFO data source integration (reads from SDC business DB — spec 002)
- [ ] T037 [P] Unit tests for trend detection and recommendation logic

---

## Phase 7: Polish & Cross-Cutting

- [ ] T038 [P] Add n8n workflow max execution depth guard (prevent infinite loops)
- [ ] T039 [P] Add TTS language mismatch detection and warning
- [ ] T040 [P] Add social platform rate limit queuing with retry-after
- [ ] T041 [P] Add CFO no-data state (onboarding message, not error)
- [ ] T042 [P] Handle DST time change for scheduled posts gracefully
- [ ] T043 [P] Encrypt all social platform credentials
- [ ] T044 [P] Full E2E test: content gen → approve → schedule → publish

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Infrastructure)**: No dependencies — start immediately
- **Phase 2 (n8n)**: Depends on Phase 1
- **Phase 3 (Content)**: Depends on Phase 1
- **Phase 4 (Video)**: Depends on Phase 3
- **Phase 5 (Social)**: Depends on Phase 3 and Phase 4
- **Phase 6 (CFO)**: Depends on spec 002 (payment data source)
- **Phase 7 (Polish)**: Depends on all user stories

### Parallel Opportunities

- Phase 2 and Phase 3 can run in parallel
- Phase 4 and Phase 5 are sequential (video → social)
- All [P] tasks within each phase run in parallel

---

## Implementation Strategy

1. Phase 1: Infrastructure → n8n + DB + storage
2. Phase 2: n8n Workflows → automation MVP (US1)
3. Phase 3: Content Pipeline → content MVP (US2)
4. Phase 4: Video Pipeline (US3)
5. Phase 5: Social Automation (US4)
6. Phase 6: Agent CFO (US5)
7. Phase 7: Polish

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

- [X] T053 Crear thumbnail generator service (FastAPI, puerto 8765)
- [X] T054 Crear multi-platform publisher service (FastAPI, puerto 8766)
- [X] T055 Crear YouTube news scraper + script generator (HN integration)
- [X] T056 Crear content pipeline con fal.ai (productos, thumbnails, social)
- [X] T057 Crear n8n workflow JSON para newsjacking automation
- [X] T058 Generar 5 imagenes de producto para catalogo AzREC
- [X] T059 Crear media library inventory + workflow docs
