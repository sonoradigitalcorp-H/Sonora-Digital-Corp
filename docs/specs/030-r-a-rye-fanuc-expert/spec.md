# SPEC-030-R-A: FANUC Robot Expert (agente fanuc-expert)

**Status:** Draft
**Tier:** 1 (Foundation)
**Score:** 78/100
**Created:** 2026-08-03
**Parent:** SPEC-030 (RYE OpenClaw Agents)

## 1. Objective

Diagnóstico experto de robots FANUC: alarmas SRVO, programación KAREL, R-2000iC, integración con líneas automotrices BMW/Rivian.

## 2. User Stories

- Como Iván, quiero diagnosticar alarmas SRVO sin abrir el manual
- Como programador, quiero ayuda con KAREL y posiciones R-2000iC
- Como operador, quiero que el bot recupere config de la celda desde RAG

## 3. Functional Requirements

| ID | Requirement | Priority | Est. Hours |
|----|------------|----------|------------|
| FR1 | Diagnóstico SRVO: causa + acción correctiva citando fuente | P0 | 4 |
| FR2 | Conocimiento KAREL: $SN, $PR[], $DLM, $ER | P0 | 4 |
| FR3 | RAG por celda: recuperar config R-2000iC de kb_rye | P0 | 4 |

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
