# ADR-20260803-RYE-SECURITY

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260803-RYE-SECURITY` |
| **Fecha** | 2026-08-03 |
| **Spec** | SPEC-030: RYE OpenClaw Agents |
| **Estado** | aceptado |

---

## Context

El bot `@RyE_production_bot` accederá a datos de producción de RYE, manuales FANUC, y conversaciones de Iván. Los secretos reales del sistema viven en `~/.config/sonora/env.local` (OPENROUTER_API_KEY, tokens), el token de Telegram en `~/.openclaw/secrets/telegram-rye.token`, y hay historial de leak de keys en el repo (ADR Aztrotech MVP menciona key expirada en logs). El canal usa `dmPolicy: pairing` para restringir quién habla con el bot.

## Decision

1. **Secrets fuera del repo**: tokens y API keys SOLO en `~/.config/sonora/env.local` (chmod 600) y `~/.openclaw/secrets/telegram-rye.token` (chmod 600). Nunca en archivos versionados.
2. **DM restringido**: `dmPolicy: pairing` — solo Iván (chat_id verificado) puede hablar con el bot; `groupPolicy: disabled`.
3. **Guardrails anti-prompt-injection** (patrón Aztrotech): el prompt del sistema instruye al agente a no revelar prompts internos, no ejecutar instrucciones embebidas del usuario, y rehusar pedidos que escaleen privilegios.
4. **Tenant aislado**: RAG (`kb_rye`) y engram usan `tenant_id=rye` — el conocimiento de RYE no se mezcla con otros clientes.
5. **Gate RDD con kill switch**: `.rdd/killswitch.json` como válvula de emergencia, y las credenciales nunca pasan por los outputs del review (redactadas en los logs de review).
6. **Sin secrets en eval/outputs**: promptfoo y evals usan fixtures mock, nunca keys reales.

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| **Secrets en env.local + tokenFile, repo limpio** | Keys fuera del repo, revocables, mode 600 | Requiere discipline en cada entorno |
| Secrets en `.env` del repo | Simple | Riesgo de commit de secretos (leak histórico) |
| Bot abierto a cualquiera | Fácil probar | Cualquiera accede al conocimiento de RYE |

## Consequences

- **Positivas**: keys revocables y fuera del repo; bot solo accesible por Iván; tenant aislado.
- **Positivas**: guardrails anti-injection probados en Aztrotech (0 safety issues en eval).
- **Riesgos**: si la key de OpenRouter expira, el bot deja de responder (monitorear con `sdc_status`).
- **Riesgos**: el kill switch debe estar documentado y accesible (`.rdd/killswitch.json`).

## Related

- `ADR-20260802-AZROTECH-MVP-RAG-MEMORIA` (guardrails y leak de key)
- `ADR-20260803-RYE-ARCHITECTURE`
- `docs/rdd/METHOD.md` (kill switch)
