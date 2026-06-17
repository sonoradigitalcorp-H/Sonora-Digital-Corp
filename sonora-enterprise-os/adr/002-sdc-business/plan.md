# Implementation Plan: SDC Business Layer

**Branch**: `002-sdc-business` | **Date**: 2026-06-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-sdc-business/spec.md`

## Summary

Business layer for Sonora Digital Corp: gamified landing page, ecommerce (merch + digital), dual payments (SPEI + Crypto), gamification tiers (Play-Work-Learn-Earn), and affiliate system. Customer-facing copy avoids all technical language.

## Technical Context

**Language/Version**: Python 3.11+, Next.js 16 (landing page + storefront)

**Primary Dependencies**: FastAPI, Stripe/Conekta (SPEI), web3.py (crypto), Next.js, Tailwind CSS

**Storage**: PostgreSQL (primary), Redis (sessions, cart, rate limits)

**Testing**: pytest for backend logic, Playwright for frontend E2E, coverage >= 80%

**Target Platform**: Linux server (cloud or local), responsive web (mobile-first)

**Project Type**: Web application (Next.js frontend + FastAPI backend + payment workers)

**Performance Goals**: Page load < 3s (4G Mexico), checkout < 1s, payment detection < 5min (SPEI) / < 1hr (crypto)

**Constraints**: No technical language in customer-facing copy, encrypted payment data, webhook reliability

**Scale/Scope**: < 1000 products, < 10K users, < 100 orders/day

## Constitution Check

*GATE: Must pass before implementation.*

| Principle | Compliance | Status |
|-----------|-----------|--------|
| **I. Separación de Responsabilidades** | Business logic in Python/FastAPI (deterministic). LLM only for content generation (spec 003), not business decisions. | ✅ PASS |
| **II. Privacidad y Control Local** | Customer PII encrypted at rest. Payment data handled by third-party APIs (Conekta, blockchain RPC). No unnecessary data storage. | ✅ PASS |
| **III. Arquitectura Modular** | Payments, gamification, affiliates, ecommerce are independent modules. Can be deployed separately. | ✅ PASS |
| **IV. Calidad y Testing** | Payment flow tests with mocked APIs. Gamification XP math tests. Affiliate commission calculation tests. | ✅ PASS |
| **V. Sin Jerga Técnica** | Copy reviewed and tested via automated scan for banned terms. Customer never sees AI/API/model/GPU. | ✅ PASS |

**Result**: PASS. No violations.

## Project Structure

```text
specs/002-sdc-business/
├── plan.md              # This file
├── spec.md              # Feature specification
├── tasks.md             # Implementation tasks
├── checklists/          # Quality checklists
└── contracts/           # API contracts

src/
├── business/            # Business logic
│   ├── landing.py       # Landing page data + gamification
│   ├── ecommerce.py     # Product catalog, cart, orders
│   ├── payments.py      # SPEI + crypto payment processing
│   ├── gamification.py  # XP tracking, tier progression
│   └── affiliates.py    # Referral tracking, commissions
├── api/                 # FastAPI endpoints
└── ui/                  # Next.js pages and components
```

**Structure Decision**: Flat business/ module with one file per domain. Each file is independent. Payment processing uses background workers for webhook handling.
