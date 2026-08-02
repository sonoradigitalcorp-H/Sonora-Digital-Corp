# ADR-20260802-AZROTECH-WHATSAPP-SANDBOX

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260802-AZROTECH-WHATSAPP-SANDBOX` |
| **Fecha** | 2026-08-02 |
| **Spec** | Sandbox WhatsApp (WACLI) |
| **Estado** | aceptado |

---

## Context

El sistema tiene WhatsApp vía `wacli` v0.12.0 (MCP stdio, 7 tools) autenticado como `5216623538272@s.whatsapp.net`. Se intentó enviar un audio de resumen a 6623538272 y falló con `SessionCipher.go:319 Unable to verify ciphertext mac: mismatching MAC` (sesión de cifrado Signal desincronizada). Además, existe el riesgo de enviar data/how-to a contactos no autorizados.

## Decision

1. **Sandbox estricto**: el único número permitido para WhatsApp es **6623538272** (César). Cualquier envío/lectura a otro número está bloqueado por ahora.
2. **No se implementa el receptor ni el envío en esta fase**: el pipeline de WhatsApp (polling `messages list --from-them` cada 5s → `ConversationEngine`) queda **diferido a una sesión dedicada**, porque primero hay que resolver la sesión Signal.
3. **Fix de sesión pendiente**: re-autenticar escaneando QR (`wacli login`) con volumen bajo, verificar paridad de mensajes y recién entonces habilitar el canal.
4. Documentar en memoria (`proceso:wacli`, `deuda:sesion-wacli`) para no perder contexto entre sesiones.

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| **Diferir WhatsApp a sesión dedicada** | Resolver sesión con calma, sin romper nada | Canal no disponible aún |
| Activar receptor con sandbox parcial | Avanza el canal | Riesgo de envíos accidentales, sesión rota |
| Re-autenticar ahora mismo | Canal listo | Requiere QR interactivo, fuera del flujo actual |

## Consequences

- **Positivas**: cero riesgo de mensajes no autorizados; contexto documentado en engram para la sesión WhatsApp.
- **Positivas**: la identidad cross-canal ya está lista en Postgres para cuando se active.
- **Trade-off**: WhatsApp no entrega hasta resolver `SessionCipher`; el bot sigue por Telegram.
- **Deuda**: re-autenticación QR pendiente (memoria `deuda:sesion-wacli`, prioridad baja).

## Lessons

- `SessionCipher MAC mismatch` indica desync del cifrado de extremo a extremo de la sesión; NO se arregla reintentando, se re-autentica.
- La paridad de mensajes debe verificarse antes de confiar en envíos.
- El patrón de polling `--from-them` cada 5s ya está definido en `ADR-20260719-WHATSAPP-OS-FASE1`.

## Related

- Spec: Sandbox WhatsApp
- Events: engram `proceso:wacli`, `deuda:sesion-wacli`
