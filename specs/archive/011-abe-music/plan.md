# Plan: ABE MUSIC

**Spec**: `specs/011-abe-music/spec.md`
**Created**: 2026-06-09
**Status**: Implemented

## Summary
White label de SDC para sello discográfico: CRM artistas en grafos, dashboard CEO, revenue split, distribución.

## Language & Version
- Python 3.10+
- Neo4j (grafos)
- n8n (workflows distribución)

## Primary Dependencies
- Neo4j (CRM grafos)
- Stripe Connect (payout artistas)
- Fal.ai (contenido artistas)
- n8n (workflows)

## Storage
- Neo4j: Artist, Label, Release, Collaboration nodos
- Revenue split: 70/20/10 (artista/sello/distribución)

## Testing
- Tests unitarios: `tests/unit/test_abe_music.py` (21 tests)
- Dashboard CEO: KPIs, top artists, revenue breakdown

## Target Platform
- Web (dashboard CEO)
- API REST
- n8n workflows

## Project Type
- Music label management platform
- White label SDC product

## Performance Goals
- Dashboard carga < 2s
- Revenue calculation < 500ms
- Artist KPI < 200ms
- Stream recording < 100ms

## Constraints
- Revenue split configurable por contrato
- Stripe Connect necesario para payout
- n8n para distribución automática

## Constitution Check
| Principle | Status |
|-----------|--------|
| I. Separación de Responsabilidades | ✅ PASS |
| II. Privacidad y Control | ✅ PASS |
| III. Arquitectura Modular | ✅ PASS |
| IV. Calidad y Testing | ✅ PASS |
| V. Documentación | ✅ PASS |
