# ADR-20260701-007 — Self-Healing Loop

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260701-007` |
| **Fecha** | 2026-07-01 |
| **Spec** | `SPEC-20260701-007` |
| **Estado** | aceptado |

---

## Context

El monitor detecta contenedores caídos y escribe a events.jsonl, pero nadie reacciona. Un container puede estar horas muerto hasta que alguien revisa el dashboard. Necesitábamos un loop automático de reparación.

## Decision

### 1. Healer como timer independiente

No modificar el monitor. Crear un segundo timer `healer.timer` que corre 30s después del monitor. Esto mantiene separación de concerns: monitor solo detecta, healer solo repara.

### 2. Telegram directo (sin n8n)

Enviar notificaciones críticas directamente a Telegram API en vez de pasar por n8n. Razón: n8n puede estar caído (si el container que falla es justamente n8n). La llamada directa a `api.telegram.org` es más confiable.

### 3. Dedup con cooldown

El healer no reintenta contenedores que ya fueron sanados exitosamente en los últimos 120 segundos. Esto evita loops infinitos de restart.

### 4. Fallback a .env

Las credenciales de Telegram se leen de variables de entorno primero, con fallback al archivo `.env` del proyecto. Esto permite que el healer funcione incluso sin systemd env vars.

## Consequences

**Positivo:**
- Container caído → reinicio en <60s automático
- Si no revive tras 3 intentos → Telegram a Luis Daniel
- Sin dependencia de n8n (más confiable)
- Healer no interfiere con monitor

**Trade-offs:**
- Healer reinicia contenedores sin consultar dependencias (puede causar cascada)
- No hay "rollback" — si el container tiene config corrupta, reiniciar no ayuda
- Telegram token en .env (aceptable para VPS aislado)

## Related

- Monitor: `scripts/monitor.py` + `monitor.timer`
- Healer: `scripts/healer.py` + `healer.timer`
- Events: `healing_attempt`, `healing_success`, `healing_failure`, `container_critical`
