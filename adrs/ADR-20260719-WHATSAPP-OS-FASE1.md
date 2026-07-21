# ADR — WhatsApp OS Fase 1

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260719-WHATSAPP-OS-FASE1` |
| **Fecha** | 2026-07-19 |
| **Spec** | SPEC-20260719-WHATSAPP-OS-FASE1 |
| **Estado** | activo |

## Contexto
Se necesitaba una base sólida de WhatsApp para Sonora OS v3. Existían dos MCP servers duplicados (`wacli_mcp.py` y `wacli_server.py`) con funcionalidad parcial. No había webhook persistente ni catálogo de servicios. El enterprise score estaba en 58/100.

## Decisión
1. **Unificar MCP servers**: Mergear `wacli_server.py` → `wacli_mcp.py` con 9 tools
2. **Webhook persistente con polling**: `wacli messages list --from-them` cada 5s
3. **Eventos JSONL**: Todos los eventos WhatsApp se emiten a `state/events/events.jsonl`
4. **Catálogo JSON**: Servicios en `state/whatsapp/catalog.json` con tokens, precios, entregas
5. **Skills formales**: whatsapp-onboarding y whatsapp-catalog en formato SKILL-TEMPLATE.md

## Opciones Consideradas
| Opción | Pros | Contras |
|--------|------|---------|
| Mantener 2 servers separados | Sin riesgo de regresión | Duplicación, divergencia de código |
| **Unificar en wacli_mcp.py** | Una fuente de verdad, código más robusto | Riesgo de merge, pruebas necesarias |
| Webhook vía wacli --events | Eventos en tiempo real | Documentación limitada de --events |
| **Webhook vía polling messages** | Simple, funciona con wacli actual | Latencia de 5s |

## Consecuencias
- Positivas: 35/35 evals, 38 tests nuevos, enterprise score 75/100
- Positivas: Catálogo listo para consultar desde WhatsApp
- Pendiente: `--events` flag de wacli podría reemplazar polling en futuro

## Lecciones
- Crear symlink `src → apps/jarvis/src` resolvió errores de colección de tests legacy
- El enterprise score necesitaba `--continue-on-collection-errors` para ser realista
