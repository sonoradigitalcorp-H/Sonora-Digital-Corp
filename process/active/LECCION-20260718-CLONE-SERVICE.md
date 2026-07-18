# LECCION-20260718-CLONE-SERVICE — Clone Service Session Learnings

| Campo | Valor |
|-------|-------|
| **ID** | LECCION-20260718-CLONE-SERVICE |
| **SPEC** | SPEC-20260718-CLONE-SERVICE |
| **Fecha** | 2026-07-18 |

---

## ¿Qué pasó?

Se diseñó e implementó el Servicio de Clon Publicitario SDC completo siguiendo la metodología SDD: SPEC → Gherkin → TDD → MCP tools → Agent Harness → Capability → Skill → Registry → Pipeline → Credit System → ADR → SCORE.

## ¿Qué salió bien?

- Se completó en una sola sesión: 15+ archivos, 70 tests, 4 MCP servers
- El stack existente (FAL_KEY, OmniVoice, Supabase, OpenClaw) cubría el 100% de las necesidades sin GPU local
- Se siguió la metodología SDD al pie de la letra (SPEC → Gherkin → TDD → Implementation → Documentation)
- El Agent Harness template de 12 campos ayudó a no saltarse nada

## ¿Qué salió mal?

- Inicialmente se hicieron muchas preguntas al usuario en vez de analizar el stack existente
- Se perdió tiempo preguntando en lugar de investigar lo que ya estaba configurado
- La confusión inicial sobre qué guarda quién (Content Server vs Supabase vs FAL) retrasó el arranque

## ¿Qué se haría diferente?

- Investigar el stack completo antes de preguntar al usuario
- Usar los MCP tools existentes como base en lugar de crear desde cero (lora_mcp ya existía)
- Mover los questions al inicio del plan mode, no después

## Tags

#clone-service #sdd #gherkin #tdd #mcp #fal-ai #omnivoice #supabase

## Engram

- Decision: `architecture/plan-clone-service-sdc`
- Milestone: `bug/clone-service-sdc-implementation-complete`
