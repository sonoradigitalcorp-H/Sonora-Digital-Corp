# Feature Specification: SDC Business Layer

**Feature Branch**: `002-sdc-business`

**Created**: 2026-06-10

**Status**: Draft

**Input**: Business layer for Sonora Digital Corp: landing page, ecommerce (merch, digital products), payments (SPEI/Crypto), gamification system, and affiliate program.

## User Scenarios & Testing

### User Story 1 - Customer landing page with brand experience (Priority: P1)

A visitor arrives at the SDC landing page and experiences a branded, gamified journey that explains what SDC offers without technical jargon — only benefits.

**Why this priority**: The landing page is the front door. No customers enter without it.

**Independent Test**: Load the landing page in a browser, verify all sections render, the gamification elements animate, and no technical terminology appears in customer-facing copy.

**Acceptance Scenarios**:

1. **Given** a first-time visitor, **When** they load the landing page, **Then** they see five niche-specific value propositions (creators, pymes, educators, artists, entrepreneurs) without mentioning AI or technology.
2. **Given** any page with marketing copy, **When** the page renders, **Then** no technical terms (API, model, GPU, AI, etc.) appear.
3. **Given** the gamification section, **When** the user scrolls to it, **Then** they see the Play-Work-Learn-Earn progression with clear rewards per tier.
4. **Given** a mobile device, **When** the page loads, **Then** it is fully responsive and touch-friendly.

---

### User Story 2 - Ecommerce: merch and digital products (Priority: P1)

The customer browses products (merch, digital assets, subscriptions), adds to cart, and completes purchase via SPEI (Mexican bank transfer) or cryptocurrency.

**Why this priority**: Revenue depends on transactions. Payment integration is critical.

**Independent Test**: Browse product catalog, add items to cart, initiate checkout with both SPEI and crypto, verify the payment flow works end-to-end with test credentials.

**Acceptance Scenarios**:

1. **Given** a product catalog, **When** the user browses, **Then** products display with price (MXN + USD/Crypto toggle), description, and media.
2. **Given** items in cart, **When** the user proceeds to checkout, **Then** they choose between SPEI and cryptocurrency payment.
3. **Given** SPEI payment selected, **When** the user confirms, **Then** a CLABE reference is generated and payment is detected within 5 minutes.
4. **Given** crypto payment selected, **When** the user confirms, **Then** a wallet address/QR is shown and the system waits for blockchain confirmation.

---

### User Story 3 - Gamification: Play-Work-Learn-Earn (Priority: P2)

The user engages with the platform and progresses through gamification tiers (Bronze → Silver → Gold → Platinum), unlocking rewards and benefits.

**Why this priority**: Drives engagement and retention. Depends on US1 and US2 existing.

**Independent Test**: Create a test user, perform actions that earn XP, verify tier progression and reward unlocking.

**Acceptance Scenarios**:

1. **Given** a registered user, **When** they complete actions (register, create content, refer friends), **Then** they earn XP and see their progress.
2. **Given** enough XP for tier up, **When** the threshold is reached, **Then** the user unlocks the next tier and its rewards automatically.
3. **Given** a Bronze user, **When** they refer 5 friends, **Then** they unlock Silver and get 20% lifetime commission.

---

### User Story 4 - Affiliate system (Priority: P2)

Users refer others via unique affiliate links and earn commissions on purchases. Affiliates track earnings, withdrawals, and performance.

**Why this priority**: Viral growth. Depends on payments (US2) existing.

**Independent Test**: Generate an affiliate link, make a purchase through it, verify commission is tracked and credited.

**Acceptance Scenarios**:

1. **Given** a registered user, **When** they access the affiliate dashboard, **Then** they see their unique referral link, QR code, and current earnings.
2. **Given** a referral purchase completed, **When** the payment settles, **Then** the affiliate's commission is credited automatically.
3. **Given** sufficient earnings, **When** the user requests withdrawal, **Then** the payout is processed via SPEI or crypto within 48 hours.

---

### Edge Cases

- **SPEI payment timeout (> 1 hour)**: cancel order, notify user, release inventory
- **Crypto payment stuck (unconfirmed > 1 hour)**: show pending status, allow cancellation
- **Gamification XP cap exceeded**: handle gracefully, no overflow
- **Affiliate self-referral**: detect and reject with clear message
- **Concurrent checkout same product**: inventory lock to prevent overselling
- **Payment webhook failure**: retry with exponential backoff, alert admin

## Requirements

### Functional Requirements

**Landing page**

- **FR-001**: The landing page MUST display 5 niche-specific value propositions without technical language.
- **FR-002**: The landing page MUST include gamification section showing Play-Work-Learn-Earn tiers.
- **FR-003**: All customer-facing copy MUST avoid technical terms (AI, API, model, GPU, etc.).
- **FR-004**: The landing page MUST be fully responsive (mobile, tablet, desktop).

**Ecommerce**

- **FR-005**: The system MUST support product categories: merch, digital assets, subscriptions.
- **FR-006**: The cart MUST support multiple items, quantity changes, and coupon codes.
- **FR-007**: Checkout MUST support SPEI (CLABE reference) and cryptocurrency (BTC/ETH/SOL) payments.
- **FR-008**: Payment detection MUST use webhook polling for SPEI and blockchain confirmation for crypto.

**Gamification**

- **FR-009**: The system MUST track XP per user across actions: register, create content, refer, purchase.
- **FR-010**: Tiers MUST be: Bronze, Silver, Gold, Platinum with configurable thresholds.
- **FR-011**: Rewards MUST unlock automatically on tier progression.
- **FR-012**: XP MUST be capped per action type to prevent gaming.

**Affiliates**

- **FR-013**: Each user MUST have a unique referral link and QR code.
- **FR-014**: Commissions MUST be calculated as configurable % of referral purchase amount.
- **FR-015**: Affiliates MUST see earnings dashboard with withdrawal history.
- **FR-016**: Self-referrals MUST be detected and rejected.

**General**

- **FR-017**: All payment data MUST be encrypted at rest and in transit.
- **FR-018**: No customer data MUST leave the system without explicit consent.

### Key Entities

- **Product**: merch, digital asset, or subscription with price, media, inventory
- **Order**: cart snapshot with payment status, items, total
- **Payment**: SPEI reference or crypto transaction with confirmation status
- **User**: registered customer with gamification tier, XP, affiliate data
- **Tier**: Bronze/Silver/Gold/Platinum with thresholds and rewards
- **Affiliate**: referral link, commission rate, earnings, withdrawals

## Success Criteria

### Measurable Outcomes

- **SC-001**: Landing page loads in < 3s on 4G in Mexico.
- **SC-002**: SPEI payment detected within 5 minutes of transfer in >= 95% of cases.
- **SC-003**: Crypto payment confirmed within 1 hour in >= 90% of cases.
- **SC-004**: Gamification tier progression works for 100% of users earning required XP.
- **SC-005**: Affiliate commission credited within 5 minutes of payment settlement.
- **SC-006**: Zero technical terms appear in customer-facing copy (checked via automated scan).

## Assumptions

- **SPEI**: assumes Conekta or similar API for CLABE generation and webhook detection
- **Crypto**: assumes blockchain RPC nodes for BTC/ETH/SOL; self-hosted or Infura/Alchemy
- **Local payment running**: payment services run on local/private cloud, not end-user device
- **Single commission model**: flat % per sale; tiered or multi-level commissions are v2
- **Gamification data**: stored in application DB (SQLite/Postgres), not in Neo4j (separate concerns)
- **No regulatory compliance**: SPEI and crypto handled via third-party APIs that handle compliance
