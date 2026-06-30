# SPEC — Pipeline System Initial Setup

| Campo | Valor |
|-------|-------|
| **ID** | SPEC-20260630-001 |
| **Fecha** | 2026-06-30 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | completado |
| **Score requerido** | ≥60 |

## 1. Objetivo

Crear el sistema de pipeline de procesos que enforcee spec-first, score gates, ADR documentation, y lecciones aprendidas para toda iniciativa en Sonora Digital Corp.

## 2. Value Driver

automation, governance, knowledge, founder-independence

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Templates para SPEC, SCORE, EVENT, ADR, LECCION, GHERKIN |
| FR2 | Git hooks que enforcean spec-first |
| FR3 | CI gates que verifican spec, score, JR-Lite compliance |
| FR4 | Engram con importance scoring, promotion, decay |
| FR5 | Agent registry con niveles L0-L4 y event bus |
| FR6 | process-pipeline.sh CLI para gestionar ciclo de vida |
| FR7 | CATALOG.md como registro vivo de iniciativas |

## 4. Success Criteria

- [x] process/ directory exists with all templates
- [x] Git hooks installed and enforcing
- [x] CI workflow in .github/workflows/
- [x] Engram upgraded with importance scoring
- [x] agents/MANIFEST.md created
- [x] process-pipeline.sh CLI works

## 5. Gherkin Scenarios

N/A — infrastructure setup

## 6. Edge Cases

- N/A

## 7. Technical Approach

Direct file creation. Engram uses SQLite schema migration (ALTER TABLE not needed because CREATE TABLE IF NOT EXISTS handles new columns). Git hooks use bash. CI uses GitHub Actions.

## 8. Dependencies

- Git (hooks)
- GitHub Actions (CI)
- SQLite (Engram)

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| spec_created | Al crear spec |
| spec_completed | Al completar spec |
| engram_upgraded | Upgrade de Engram |
| agent_manifest_created | Creación de MANIFEST |
| pipeline_initialized | Setup completo |

## 10. Kill Criteria

N/A

## 11. Scale Criteria

A medida que crezcan las iniciativas, agregar más CI gates y automatizar score calculation con datos en vivo.
