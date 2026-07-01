# ADR-20260630-003: Dockerización Jarvis + WebUI
**Status**: Accepted | **Date**: 2026-06-30
**Context**: JARVIS y WebUI corrían en proceso directo. Necesitaban Docker para portabilidad.
**Decision**: Dockerizar JARVIS Core y WebUI en contenedores separados con multi-stage build.
**Consequences**: Portabilidad, escalabilidad, entornos reproducibles.
