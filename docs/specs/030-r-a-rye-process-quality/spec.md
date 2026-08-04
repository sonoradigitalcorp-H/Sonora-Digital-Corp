# SPEC-030-R-A: Process Quality (IATF) (agente process-quality)

**Status:** Draft
**Tier:** 1 (Foundation)
**Score:** 78/100
**Created:** 2026-08-03
**Parent:** SPEC-030 (RYE OpenClaw Agents)

## 1. Objective

Calidad según IATF 074: FMEA, plan de control, trazabilidad, no conformidades de celdas robóticas.

## 2. User Stories

- Como auditor, quiero consultar requisitos IATF
- Como Iván, quiero registrar alarmas como no conformidad menor

## 3. Functional Requirements

| ID | Requirement | Priority | Est. Hours |
|----|------------|----------|------------|
| FR1 | Consultar estándares IATF desde RAG | P0 | 4 |
| FR2 | Registrar no conformidad | P0 | 4 |
| FR3 | Trazabilidad de piezas | P0 | 4 |

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR1 | Latencia de respuesta | < 4s p50 |
| NFR2 | RAG en kb_rye | min_score >= 0.65 |
| NFR3 | Seguridad de secrets | keys fuera del repo |

## 5. Stack

- LLM: OpenRouter `deepseek-v4-flash`
- RAG: Qdrant `kb_rye` (embeddings local all-minilm 384-dim)
- Memoria: engram (tenant `rye`)
- Entrada: Telegram `@RyE_production_bot` → conductor `rye`

## 6. Gherkin

- tests/gherkin/rye-fanuc-expert.feature

## 7. Acceptance Criteria

- AC1: el agente responde con contexto de kb_rye cuando existe.
- AC2: sin contexto, admite desconocer y sugiere manual FANUC.
- AC3: guarda interacciones clave en engram.
