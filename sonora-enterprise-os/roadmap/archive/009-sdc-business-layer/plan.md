# Plan: SDC Business Layer

**Spec**: `specs/009-sdc-business-layer/spec.md`
**Created**: 2026-06-09
**Status**: Implemented

## Summary
Conectar infraestructura JARVIS con modelo de negocio SaaS: 4 planes, Stripe/Mercado Pago, onboarding Mystic, CRM.

## Language & Version
- Python 3.10+
- FastAPI (endpoints REST)
- OpenClaw skills (stripe, supabase)

## Primary Dependencies
- Stripe API / Mercado Pago API
- OpenClaw Gateway
- Neo4j (CRM)

## Storage
- Neo4j: Customer y Subscription nodos
- Stripe: suscripciones y pagos

## Testing
- Tests unitarios: `tests/unit/test_sdc_business.py` (42 tests)
- Tests integración: `test_api.py` (SDC endpoints)
- Multiplicador adulto x2 verificado

## Target Platform
- Web (Vercel)
- API REST

## Project Type
- SaaS Business Layer
- Multi-plan subscription system

## Performance Goals
- Onboarding < 2s
- Plan assignment < 500ms
- Payment creation < 1s

## Constraints
- Stripe/Mercado Pago pueden fallar → error message graceful
- Sin pagos offline (dependencia de red)
- Nicho adulto requiere multiplicador x2

## Constitution Check
| Principle | Status |
|-----------|--------|
| I. Separación de Responsabilidades | ✅ PASS |
| II. Privacidad y Control | ✅ PASS |
| III. Arquitectura Modular | ✅ PASS |
| IV. Calidad y Testing | ✅ PASS |
| V. Documentación | ✅ PASS |
