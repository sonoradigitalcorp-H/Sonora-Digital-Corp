# ADR-20260630-006: Extracción por Dominios
**Status**: Accepted | **Date**: 2026-06-30
**Context**: Código monolítico en apps/. Difícil mantener y escalar.
**Decision**: Extraer por dominios: core, webui, voice, hermes, platforms, clients, products.
**Consequences**: Código más organizado, equipos pueden trabajar en paralelo.
