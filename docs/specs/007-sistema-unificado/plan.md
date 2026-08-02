# Plan: Sistema Unificado

**Spec**: `specs/007-sistema-unificado/spec.md`
**Created**: 2026-06-09
**Status**: Implemented

## Summary

Unificar JARVIS, Hermes y OpenClaw en un solo sistema con bridge unificado, memoria compartida y human-in-the-loop.

## Language & Version
- Python 3.10+
- FastAPI para REST
- OpenClaw Gateway para skills externas

## Primary Dependencies
- Hermes API (HTTP bridge)
- OpenClaw Gateway (HTTP bridge)
- GBrain CLI (subprocess)

## Storage
- Neo4j: memoria persistente
- Qdrant: búsqueda vectorial
- Cache in-memory: UnifiedMemory

## Testing
- Tests unitarios en `tests/unit/test_unified_bridge.py`
- Tests de integración en `tests/integration/test_api.py`
- Mock de Hermes, OpenClaw, GBrain para tests offline

## Target Platform
- Linux local
- Docker (Neo4j + Qdrant + MCP)

## Project Type
- Multi-service integration layer
- Bridge pattern

## Performance Goals
- Health checks < 1s
- Approval flow < 500ms
- Memory operations < 200ms

## Constraints
- Hermes puede estar offline → fallback graceful
- OpenClaw puede estar offline → mensaje informativo
- Sin dependencias de red para operaciones core

## Scale/Scope
- Mono-usuario (fase actual)
- Extensible a multi-usuario vía Neo4j

## Constitution Check
| Principle | Status |
|-----------|--------|
| I. Separación de Responsabilidades | ✅ PASS |
| II. Privacidad y Control | ✅ PASS |
| III. Arquitectura Modular | ✅ PASS |
| IV. Calidad y Testing | ✅ PASS |
| V. Documentación | ✅ PASS |
