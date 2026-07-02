# ADR-20260701-006 — CI Completo + Mock Tests

## Context

SPEC-006 pedía 90+ tests y mocks para cada collector. Se superó el target (138 tests) con mocks para todos los collectors.

## Decision

Cubrir 8 collectors con mocks:
- Deezer: 9 tests ✅
- Apple Music: 3 tests ✅  
- YouTube: 4 tests ✅
- TikTok: 2 tests ✅
- Spotify: 2 tests ✅
- Wikipedia: 3 tests ✅
- Sync/Health: 8 tests ✅
- Hermes Client: 7 tests ✅

Total: 138 tests (68 nuevos).

## Consequences

CI ahora cubre planner (70) + ABE Service (9) + collectors (31) + agents (28).
