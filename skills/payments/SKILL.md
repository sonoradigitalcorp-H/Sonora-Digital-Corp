# skills/payments — Multi-Provider Payment Processing

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-PAY-001

---

## 1. Business Objective

Process payments through Stripe and MercadoPago in under 5 seconds — handling checkout creation, payment confirmation, refunds, and daily reconciliation — with full transaction audit trail.

## 2. Inputs (Gherkin)

```gherkin
Given a payment provider is configured (Stripe, MercadoPago, or both)
And the user has an active session with payment intent data
When a payment request is submitted (checkout, subscription, or refund)
```

## 3. Outputs (Gherkin)

```gherkin
Then a payment preference/checkout session is created
And the payment is processed and confirmed by the provider
And the transaction status is recorded in Hasura
And a receipt notification is sent to the user
And daily reconciliation matches provider records to internal records
```

## 4. Events

```
Events:
- payment:processed: a payment was completed successfully
- payment:failed: a payment was declined or errored
- payment:refunded: a payment was refunded partially or fully
- payment:reconciled: daily reconciliation matched all records
```

## 5. Dependencies

```
Dependencies:
- Stripe API: service — payment processing (US/international)
- MercadoPago API: service — payment processing (LatAm)
- Hasura: service — transaction and status storage
- Engram: service — reconciliation records
- Webhook handler: service — IPN processing for async updates
```

## 6. Tools

```
Tools:
- stripe_create_checkout: create Stripe checkout session
- stripe_create_payment: create direct payment intent
- mp_create_preference: create MercadoPago preference
```

## 7. Policies

```
Policies:
- All payments must be idempotent (same request never charges twice)
- Failed payments must be logged with provider error code
- Refunds must require explicit authorization (no auto-refund)
- PII (card details) must never be stored locally
- Daily reconciliation must complete by 12:00
- Webhook signatures must be verified before processing
```

## 8. Success Metrics

```gherkin
Success Metrics:
- process_time: Given payment request When completed Then total milliseconds
  Target: < 5000 ms
- success_rate: Given all payment attempts When processed Then success percentage
  Target: > 95%
- reconciliation_match: Given daily records When compared to provider Then match rate
  Target: 100%
```

## 9. Failure Conditions

```
Failure Conditions:
- Provider API down: Stripe or MercadoPago returns 5xx (detect via HTTP status)
- Webhook timeout: IPN not received within 60s (detect via timeout timer)
- Reconciliation mismatch: internal vs provider totals differ (detect via comparison)
- Duplicate charge: same IDEMPOTENCY_KEY results in double charge (detect via audit)
- Currency mismatch: payment currency unsupported by provider (detect via validation)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If provider API down → queue payment, retry every 30s for 5 min, then fail
2. If webhook missing → poll provider status API for pending transactions
3. If reconciliation mismatch → flag transactions, investigate manually
4. If duplicate charge → initiate immediate refund, log incident
5. If currency error → reject payment, suggest supported currency
6. Log all attempts to state/logs/skills/payments.log
```

## 11. Business Value

```
Business Value: Payment processing in under 5 seconds. Supports Stripe + MercadoPago.
```

## 12. Parent OS

```
Parent OS: Finance
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: ADR-2026-PAY-001
- Events: payment:processed, payment:failed, payment:refunded, payment:reconciled
- Logs: state/logs/skills/payments.log
```
