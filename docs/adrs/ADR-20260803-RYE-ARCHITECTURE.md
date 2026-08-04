# ADR-20260803-RYE-ARCHITECTURE

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260803-RYE-ARCHITECTURE` |
| **Fecha** | 2026-08-03 |
| **Spec** | SPEC-030: RYE OpenClaw Agents |
| **Estado** | aceptado |

---

## Context

Iván Alejandro Guerrero Enciso (Gerente de Producción RYE, Claremore OK) programa robots FANUC manualmente hoy y quiere un asistente de IA real por Telegram 24/7. Sonora Digital Corp ya tiene un stack maduro: OpenClaw como gateway de bots, engram como memoria persistente, Qdrant + FastEmbed para RAG, OpenRouter/DeepSeek V4 Flash como LLM, y un MCP local (`sdc-mcp-local`) que expone engram + rag_search + llm_chat.

## Decision

Se adopta una arquitectura **bot conductor + 7 agentes especialistas** sobre OpenClaw:

1. **OpenClaw Gateway** (`localhost:18789`) como único canal Telegram (`@RyE_production_bot`), con `dmPolicy: pairing` para permitir solo a Iván.
2. **Conductor `rye`**: enruta cada mensaje al agente especialista según el intento (FANUC, alarma, reporte de turno, mantenimiento, calidad, seguridad, escalamiento).
3. **7 agentes especialistas** ultra-configurados con SOUL.md/AGENTS.md, cada uno con spec ligera, gherkin y eval promptfoo A/B (v1 genérico vs v2 dominio).
4. **Stack LLM/RAG nivel mundial**: OpenRouter `deepseek-v4-flash` (modelo base) + Qdrant colección `kb_rye` + FastEmbed local `paraphrase-multilingual-MiniLM-L12-v2` (384-dim, $0) + engram (memoria persistente) + chunking 512/64 idempotente.
5. **RAG-first pipeline**: buscar en Qdrant ANTES de llamar al LLM; con contexto RAG + memoria, construir el prompt y responder.
6. **RDD gate**: cada commit pasa por review-driven development (freeze → review 4 lentes → fix → validate → receipt → commit).

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| **OpenClaw + 7 agentes especialistas** | Escala a múltiples clientes, skills por agente, gateway central | Curva de config, requiere gateway up |
| 1 bot monolítico con prompts | Simple de empezar | Un solo prompt = respuestas genéricas, sin especialización |
| Polling propio (python-telegram-bot, patrón ABE/Nathy) | Control total | Duplica infra que OpenClaw ya resuelve, sin multi-agente |
| Llamar LLM sin RAG | Cero deps | Alucina en alarmas FANUC, sin contexto de manuales |

## Consequences

- **Positivas**: asistente especializado por dominio robótico, RAG local sin costo, memoria persistente cross-sesión, gate de calidad RDD en cada commit.
- **Positivas**: reutiliza el stack probado de Sonora (sdc-mcp-local, engram, Qdrant, FastEmbed) — no se inventa infra nueva.
- **Riesgos**: el gateway OpenClaw debe estar arriba (hoy down); la calidad RAG depende del corpus que Iván aporte.
- **Mitigación**: Sprint 2 levanta el gateway; Sprint 1 verifica el stack e2e en sandbox antes de producción.

## Related

- `SPEC-030` (spec master RYE)
- `docs/rdd/METHOD.md` (gate RDD)
- `ADR-20260722-ARQUITECTURA-CORE` (capas del monorepo)
