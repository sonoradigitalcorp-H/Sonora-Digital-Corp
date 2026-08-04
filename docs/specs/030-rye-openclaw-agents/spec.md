# SPEC-030: RYE OpenClaw Agents — Asistente 24/7 de Producción Robótica

**Status:** Draft
**Tier:** 1 (Foundation)
**Score:** 78/100
**Created:** 2026-08-03

## 1. Objective

Construir un asistente de IA 24/7 por Telegram para Iván Alejandro Guerrero Enciso, Gerente de Producción en RYE Design (Claremore OK — integrador de robótica automotriz: FANUC, Cognex, Lincoln, Servo-Robot, Yaskawa; líneas para BMW, Rivian, VW, Mercedes). El sistema usa OpenClaw como gateway de bots + un conductor `rye` + 7 agentes especialistas ultra-configurados, con stack LLM+RAG de nivel mundial: OpenRouter (DeepSeek V4 Flash) como modelo base, Qdrant + FastEmbed local para RAG, engram para memoria persistente, chunking e ingestión de bases de datos grandes.

## 2. User Stories

- Como gerente de producción, quiero preguntar por alarma SRVO de FANUC y obtener el diagnóstico con la causa y la solución inmediata.
- Como programador de robots, quiero generar un reporte de turno con tiempos de ciclo, downtime y pendientes en un solo mensaje.
- Como operador, quiero consultar el procedimiento de mantenimiento de una celda sin abrir manuales en PDF.
- Como usuario del bot, quiero que el asistente recuerde conversaciones previas y contexto del cliente RYE.
- Como administrador, quiero que cada cambio de código pase por una revisión RDD (review-driven development) antes de commit.

## 3. Functional Requirements

| ID | Requirement | Priority | Est. Hours |
|----|------------|----------|------------|
| FR1 | Gateway OpenClaw con canal Telegram `@RyE_production_bot` | P0 | 6 |
| FR2 | Conductor `rye` enrutador de mensajes a agentes especialistas | P0 | 8 |
| FR3 | 7 agentes especialistas (fanuc-expert, fault-alarm, shift-report, maintenance-guide, process-quality, robot-safety, escalation) | P0 | 24 |
| FR4 | RAG: Qdrant + FastEmbed local (multilingual 384-dim), colección por tenant | P0 | 8 |
| FR5 | Memoria persistente con engram (capas, búsqueda, tenant `rye`) | P0 | 6 |
| FR6 | Ingestión de BD grandes: chunking 512/64, idempotente por hash | P1 | 6 |
| FR7 | Reporte de turno: captura tiempos de ciclo, downtime y pendientes | P1 | 6 |
| FR8 | Gate RDD: sin recibo no hay commit/push/PR | P0 | 4 |

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR1 | Latencia de respuesta | < 4s p50 |
| NFR2 | Disponibilidad | 99.5% |
| NFR3 | Seguridad de secretos | keys fuera del repo, modo 600 |
| NFR4 | RAG sin API key (embeddings locales) | costo $0 |
| NFR5 | Benchmark RDD | 60+ flujos (45 in-band, out-of-band, dead-end) |

## 5. Technical Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Telegram                              │
│              @RyE_production_bot                          │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│                   OpenClaw Gateway                        │
│                    http://localhost:18789                  │
│         canal telegram (tokenFile, dmPolicy pairing)      │
├──────────────────────────────────────────────────────────┤
│                    Conductor `rye`                         │
│        (enruta mensaje → agente según intento)             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐    │
│  │fanuc-exp │ │fault-alrm│ │shift-rep │ │maintenance │    │
│  │ robot-saf│ │proc-qual │ │escalation│ │            │    │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────────┘    │
└───────┼────────────┼────────────┼──────────────────────────┘
        │            │            │
┌───────▼────────────▼────────────▼──────────────────────────┐
│                   MCP servers (OpenClaw)                    │
│  sdc-mcp-local (engram_* + rag_search + llm_chat)           │
│  qdrant · filesystem · github · playwright · fetch          │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                 LLM + RAG + Memoria stack                    │
│  OpenRouter → deepseek-v4-flash (modelo base)                │
│  Qdrant :6333 → collection kb_rye (FastEmbed 384-dim)        │
│  Engram → ~/.engram/engram.db (SQLite + FTS5, capas)         │
└──────────────────────────────────────────────────────────────┘
```

## 6. RAG Stack (nivel empresa mundial)

| Capa | Tecnología | Config |
|------|-----------|--------|
| LLM base | OpenRouter | `deepseek-v4-flash` (key `~/.config/sonora/env.local`) |
| Embeddings | FastEmbed local | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384-dim, ONNX, sin API key) |
| Vector store | Qdrant | `http://localhost:6333`, colección `kb_<tenant>` (distancia COSINE) |
| Chunking | `ingest_qdrant_openrouter.py` | chunk 512 / overlap 64, idempotente SHA256→UUID |
| Memoria | Engram | SQLite+FTS5, capas L0-L6, CLI `~/.local/bin/engram` v1.19 |
| MCP | sdc-mcp-local | `skills/mcp/servers/sdc_mcp_stdio.py` (engram_save/get/search + rag_search + llm_chat) |

### 6.1 RAG-first pipeline (por mensaje)

1. Recibir mensaje en el agente → normalizar texto.
2. `rag_search(tenant_id="rye", query)` → top-K chunks con `min_score >= 0.65`.
3. Si hay contexto, `engram_search(rye, query)` para memoria previa relevante.
4. Construir prompt con contexto RAG + memoria + system prompt del agente.
5. `llm_chat` → DeepSeek V4 Flash vía OpenRouter.
6. Guardar interacción en engram (`engram_save`) para aprendizaje.

### 6.2 Carga de bases de datos grandes

- Script `ingest_bulk.py`: lee `tenants/rye/knowledge/**/*.{md,txt,pdf}` → chunk 512/64 → FastEmbed → upsert idempotente en `kb_rye`.
- Idempotencia: `point_id = UUID(sha256(chunk_text + metadata))` → re-ejecutable sin duplicados.
- Verificación: `verify_rag_stack.py` (engram_save→search + rag_index→rag_search end-to-end).

## 7. RDD Gate (Review-Driven Development)

Cada cambio de código pasa por el pipeline RDD antes de commit:

1. `freeze.sh` — snapshot con huella dactilar.
2. `review.sh` — 4 lentes paralelos (sdd-engineer/test-engineer/frontend/backend).
3. `fix.sh` — arreglo acotado (1 intento, máx 120 líneas).
4. `validate.sh` — validación read-only.
5. `receipt.sh` — autorización de commit (recibo con hash RDD).
6. `commit.sh` — commit con hash RDD en mensaje.

**Kill switch**: `.rdd/killswitch.json` — desactiva el gate en emergencia.

## 8. Repository Structure (nuevos artefactos)

```
docs/specs/030-rye-openclaw-agents/spec.md       <- esta espec
docs/specs/030-r-a-rye-fanuc-expert/spec.md       <- spec agente 1
docs/specs/030-r-a-rye-fault-alarm/spec.md        <- spec agente 2
docs/specs/030-r-a-rye-shift-report/spec.md       <- spec agente 3
docs/specs/030-r-a-rye-maintenance-guide/spec.md  <- spec agente 4
docs/specs/030-r-a-rye-process-quality/spec.md    <- spec agente 5
docs/specs/030-r-a-rye-robot-safety/spec.md       <- spec agente 6
docs/specs/030-r-a-rye-escalation/spec.md         <- spec agente 7
docs/adrs/ADR-20260803-RYE-*.md                   <- 6 ADRs
docs/rdd/METHOD.md                                <- espec RDD
tests/gherkin/rye-rdd-gate.feature                <- gherkin 1
tests/gherkin/rye-shift-report.feature            <- gherkin 2
tests/gherkin/rye-fanuc-expert.feature            <- gherkin 3
tests/steps/rye_rdd_gate_steps.py                 <- steps 1
tests/steps/rye_shift_report_steps.py             <- steps 2
tests/steps/rye_fanuc_expert_steps.py             <- steps 3
tests/evals/promptfoo/rye-*.yaml                  <- evals LLM por agente
tests/rye/test_rye_specs.py                       <- eval estructural
sandbox/rye/                                      <- sandbox local
scripts/verify_rag_stack.py                       <- verificación e2e stack
scripts/ingest_bulk.py                            <- ingestión BD grandes
```

## 9. Data Model (nuevos objetos)

| Objeto | Campos clave |
|--------|--------------|
| RAG chunk | `{id: uuid, text, source, chunk_index, payload: {tenant_id, doc_id, source, tags}}` |
| Engram memory | `{tenant_id, key, value, user_id, layer, importance, tags, created_at}` |
| Shift report | `{shift, date, cell, cycle_time_s, downtime_min, parts_ok, parts_ng, pending[]}` |
| Agent routing | `{intent → agent_id, confidence, fallback}` |

## 10. Open Questions

- Q1: ¿Iván usa el bot desde el celular en planta (WiFi industrial)? ¿Red OK para Telegram?
- Q2: ¿Qué manuales FANUC (SRVO, alarmas de programa) aporta Iván como corpus inicial?
- Q3: ¿Reporte de turno manual (Iván escribe) o integrado con el ERP/PLC de RYE?

## 11. Acceptance Criteria

- AC1: `@RyE_production_bot` responde en Telegram con diagnóstico FANUC correcto.
- AC2: `rag_search("rye", ...)` y `engram_search("rye", ...)` devuelven contexto.
- AC3: Gate RDD: `commit.sh` falla sin recibo; pasa con recibo.
- AC4: `make doctor` pasa preflight (Qdrant :6333 healthy, engram bin ok).
- AC5: Benchmark RDD 60+ flujos con `make sdd-eval` + promptfoo.
