# SPEC-030-R-A: Fault & Alarm Router (agente fault-alarm)

**Status:** Draft
**Tier:** 1 (Foundation)
**Score:** 78/100
**Created:** 2026-08-03
**Parent:** SPEC-030 (RYE OpenClaw Agents)

## 1. Objective

Diagnóstico rápido de cualquier código de alarma (SRVO, SRVO-1xx, alarmas de programa) con causa + acción.

## 2. User Stories

- Como operador, quiero saber qué significa un código corto
- Como técnico, quiero la secuencia de reset correcta

## 3. Functional Requirements

| ID | Requirement | Priority | Est. Hours |
|----|------------|----------|------------|
| FR1 | Resolver código de alarma contra RAG | P0 | 4 |
| FR2 | Ruta a fanuc-expert si es SRVO complejo | P0 | 4 |
| FR3 | Admitir desconocido y sugerir manual | P0 | 4 |

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
