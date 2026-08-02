# ADR-20260802-AZROTECH-MVP-RAG-MEMORIA

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260802-AZROTECH-MVP-RAG-MEMORIA` |
| **Fecha** | 2026-08-02 |
| **Spec** | MVP RAG-First + Memoria Persistente (TICKET-001..010) |
| **Estado** | aceptado |

---

## Context

El bot de Telegram de AstroTech (@AztroTechBot) respondía solo con un prompt estático y sin memoria, contexto, clasificación de leads ni persistencia. Se pidió un MVP con pipeline "RAG-first, luego memoria, luego voz": buscar conocimiento en Qdrant ANTES de llamar al LLM, mantener identidad cross-canal, clasificar leads y medir emoción, con guardrails anti-venta y persistencia dual.

## Decision

Se implementó un `ConversationEngine` que orquesta por cada mensaje:
1. **Identidad cross-canal** → `identity_resolver` (mapea Telegram/WhatsApp/Web a un `internal_id` canónico con lógica de merge).
2. **Memoria emerge** → `emerge_memory` (capas 0-6, promoción L0→L1→L2→L3).
3. **RAG-first** → `rag_retriever` (FastEmbed multilingual-MiniLM-L12-v2, 384 dims, colección `sdc_knowledge`, tenant `aztrotech`, min_score 0.50).
4. **Emoción multi-idioma** → `emotion_analyzer` (heurísticas es/en/pt/fr + LLM opcional en ambiguos, sin cargar modelo grande por RAM).
5. **Lead híbrido** → `lead_classifier` (reglas determinísticas + LLM few-shot con fusión).
6. **Prompt con guardrails** → `prompt_builder` (nunca precios, nunca revelar SDC, educar antes de vender, regla anti-prompt-injection con pregunta de física cuántica).
7. **Persistencia dual** → `persistence` (Postgres + Engram, batch async) + `token_tracker` (costo por modelo, presupuesto diario).

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| Llamar LLM directo con prompt estático | Simple, sin deps | Sin memoria, sin contexto, respuestas genéricas |
| **RAG-first + memoria + guardrails** | Contexto real del catálogo, leads calificados, seguridad | Más componentes, latencia |
| Memoria solo en Postgres | Una fuente de verdad | Sin layers de retención/olvido |
| **Engram dual (Postgres + sqlite engram)** | Capas L0-L6, sync a git | Dos fuentes que sincronizar |

## Consequences

- **Positivas**: eval lead accuracy **94.4%** (18 casos multi-idioma), 0 safety issues, respuestas sin revelar precios ni SDC, costos ~$0.0001/mensaje (deepseek-v4-flash).
- **Positivas**: identidad unificada permite que un cliente hable por WhatsApp y Telegram como el mismo usuario.
- **Deuda**: emoción con LLM solo en ambiguos (48.6% en eval con heurísticas); latencia p50 3.5s por llamadas LLM del clasificador.
- **Migración**: `001_mvp_identity_conversations.sql` aplicada a Postgres local (password `sdc_local_dev`).

## Lessons

- asyncpg NO decodifica JSONB a dict automáticamente: hay que serializar con `json.dumps` al insertar y parsear en lectura (helper `_j`).
- La key de OpenRouter expiró durante el MVP (`sk-or-v1-...261`); la válida quedó en `infra/.env.backup` (`f78...1ab`).
- El `ConversationEngine` se arranca en `post_init` del bot para que asyncpg pool viva en el loop de telegram-python-bot.

## Related

- Spec: TICKET-001..010
- Events: bot reiniciado en tmux `bot-cesar`
