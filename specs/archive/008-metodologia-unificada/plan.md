# Plan: Metodología Unificada

**Spec**: `specs/008-metodologia-unificada/spec.md`
**Created**: 2026-06-09
**Status**: Implemented

## Summary
Integrar SDD (diseño) + GSD (ejecución) + Self-Improve (mejora continua) como stack metodológico completo de JARVIS.

## Language & Version
- Skills OpenClaw (SKILL.md format)
- Python para gamification engine

## Primary Dependencies
- OpenClaw Gateway (:18789)
- GSD skill, close-loop skill, learning-loop skill, reflect skill, agent-evolver skill

## Storage
- Experience library: SQLite (agent-evolver)
- Reflection state: ~/.reflect/ (YAML)

## Testing
- Tests unitarios en `tests/unit/test_methodology.py`
- Test de comandos /gsd, /wrap-up, /reflect, /learn

## Target Platform
- OpenClaw skills (multi-platform)
- JARVIS Web UI (comandos slash)

## Project Type
- Metodología de desarrollo y operación
- Stack de 3 capas: SDD → GSD → Self-Improve

## Constitution Check
| Principle | Status |
|-----------|--------|
| I. Separación de Responsabilidades | ✅ PASS |
| II. Privacidad y Control | ✅ PASS |
| III. Arquitectura Modular | ✅ PASS |
| IV. Calidad y Testing | ✅ PASS |
| V. Documentación | ✅ PASS |
