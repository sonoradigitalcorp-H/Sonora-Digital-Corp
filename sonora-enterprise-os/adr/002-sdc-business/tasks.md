---
description: "Task list for SDC Business Layer"
---

# Tasks: SDC Business Layer

**Input**: Design documents from `specs/002-sdc-business/`

**Prerequisites**: plan.md ✅, spec.md ✅

**Organization**: Tasks grouped by user story (priority order from spec.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: User story the task belongs to (US1–US4)

---

## Phase 1: Infrastructure & Data Model

- [ ] T001 Create database schema (users, products, orders, payments, gamification, affiliates) in PostgreSQL
- [ ] T002 [P] Create Redis connection for sessions, cart, rate limits
- [ ] T003 [P] Set up FastAPI backend with middleware (CORS, auth, rate limiting)
- [ ] T004 [P] Set up Next.js frontend with Tailwind CSS
- [ ] T005 Create base models and Pydantic schemas for all entities

---

## Phase 2: User Story 1 - Landing Page (Priority: P1) 🎯 MVP

- [ ] T006 Design landing page with 5 niche sections (creators, pymes, educators, artists, entrepreneurs)
- [ ] T007 [P] Implement gamification tier display (Bronze/Silver/Gold/Platinum)
- [ ] T008 [P] Add automated copy check (no technical terms: AI, API, model, GPU, etc.)
- [ ] T009 [P] Make landing page fully responsive (mobile, tablet, desktop)
- [ ] T010 [P] Add animations and transitions for gamification elements

---

## Phase 3: User Story 2 - Ecommerce + Payments (Priority: P1)

- [ ] T011 Implement product catalog with categories (merch, digital, subscriptions)
- [ ] T012 [P] Implement shopping cart with quantity changes and coupon support
- [ ] T013 [P] Implement SPEI payment via Conekta API (CLABE generation, webhook detection)
- [ ] T014 [P] Implement crypto payment (BTC/ETH/SOL wallet generation, confirmation polling)
- [ ] T015 [P] Implement order management (status tracking, history, notifications)
- [ ] T016 [P] Implement payment webhook handling with exponential backoff retry
- [ ] T017 [P] Add inventory locking for concurrent checkout prevention
- [ ] T018 [P] Unit tests for payment flow (mocked APIs)
- [ ] T019 [P] Unit tests for cart operations and coupon logic

---

## Phase 4: User Story 3 - Gamification (Priority: P2)

- [ ] T020 Implement XP tracking (register, create content, refer, purchase)
- [ ] T021 [P] Implement tier progression with configurable thresholds
- [ ] T022 [P] Implement reward unlocking on tier progression
- [ ] T023 [P] Add XP cap per action type (anti-gaming)
- [ ] T024 [P] Unit tests for gamification math and tier thresholds

---

## Phase 5: User Story 4 - Affiliates (Priority: P2)

- [ ] T025 Implement unique referral link and QR code generation per user
- [ ] T026 [P] Implement commission calculation (% of referral purchase)
- [ ] T027 [P] Implement affiliate dashboard (earnings, withdrawals, performance)
- [ ] T028 [P] Implement self-referral detection and rejection
- [ ] T029 [P] Implement payout processing (SPEI or crypto, within 48h)
- [ ] T030 [P] Unit tests for commission calculation and referral validation

---

## Phase 6: Polish & Cross-Cutting

- [ ] T031 [P] Encrypt all payment data at rest and in transit
- [ ] T032 [P] Add payment timeout handling (SPEI > 1h, crypto > 1h)
- [ ] T033 [P] Add gamification XP overflow protection
- [ ] T034 [P] Add webhook retry with exponential backoff
- [ ] T035 [P] Add admin dashboard for order and payment management
- [ ] T036 [P] Full E2E test flow: browse → cart → checkout → payment → confirmation
- [ ] T037 [P] Automated copy scan for banned technical terms

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Infrastructure)**: No dependencies — start immediately
- **Phase 2 (Landing Page)**: Depends on Phase 1
- **Phase 3 (Ecommerce)**: Depends on Phase 1
- **Phase 4 (Gamification)**: Depends on Phase 2 and Phase 3
- **Phase 5 (Affiliates)**: Depends on Phase 3
- **Phase 6 (Polish)**: Depends on all user stories

### Parallel Opportunities

- Phase 2 and Phase 3 can run in parallel after Phase 1
- Phase 4 and Phase 5 can run in parallel after their dependencies
- All [P] tasks within each phase run in parallel

---

## Implementation Strategy

1. Phase 1: Infrastructure → setup DB + Redis + backend + frontend
2. Phase 2: Landing Page → MVP (US1)
3. Phase 3: Ecommerce + Payments → MVP (US2)
4. **Phase 4**: Gamification (US3) ← Current focus
5. **Phase 5**: Affiliates (US4)
6. Phase 6: Polish

---

## Current Status

- [ ] Phase 1: Not started
- [ ] Phase 2: Not started
- [ ] Phase 3: Not started
- [ ] Phase 4: Not started
- [ ] Phase 5: Not started
- [ ] Phase 6: Not started


## Session 2026-06-12: AzREC + Content Pipeline + Telegram

- [X] T043 Crear landing page AzREC con historia, branding y coleccion
- [X] T044 Generar 5 imagenes de producto con fal.ai (gorras, playera, hoodie, tote)
- [X] T045 Configurar nginx para servir AzREC en sonoradigitalcorp.com/azrec/
- [X] T046 Crear catalogo de productos con paginas individuales
- [X] T047 Crear roadmap 1 año con presupuesto casa 20k + estudio
- [X] T048 Crear guia de marca AzREC (logo, colores Sonoran Sunset, tipografia)
- [X] T049 Setup presupuesto equipamiento estudio + renta
