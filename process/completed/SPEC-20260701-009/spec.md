# SPEC — OpenClaw como Interfaz Conversacional

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260701-009` |
| **Fecha** | 2026-07-01 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Que Luis Daniel pueda preguntarle al sistema desde Telegram y recibir respuesta de los agentes usando modelos locales. OpenClaw hoy está instalado pero sin providers ni canales configurados.

---

## 2. Value Driver

founder-independence, automation, knowledge

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Provider Ollama configurado con deepseek-r1:7b-64k |
| FR2 | Channel Telegram configurado con bot token y allowlist para Luis Daniel |
| FR3 | Agent instructions con contexto del sistema (servicios, Neo4j, arquitectura) |
| FR4 | OpenClaw responde mensajes de Telegram usando Ollama local |
| FR5 | No se rompe nada existente (mismos puertos, mismos servicios) |

---

## 4. Success Criteria

- [ ] `openclaw health` muestra ollama provider listado
- [ ] Telegram bot responde a Luis Daniel
- [ ] Agente usa deepseek-r1:7b local
- [ ] No se rompen servicios existentes
- [ ] CI verde

---

## 5. Technical Approach

Agregar a `~/.openclaw/openclaw.json`:
1. `providers.ollama` apuntando a localhost:11434
2. `channels.telegram` con bot token y allowlist
3. `agents.defaults.instructions` con system prompt
4. Habilitar skills útiles (web_search, memory)
5. Verificar con `openclaw doctor` y prueba en Telegram

---

## 6. Dependencies

- OpenClaw v2026.6.10 corriendo ✅
- Ollama con deepseek-r1:7b-64k ✅
- Telegram bot @ABEfenix_bot ✅
- Telegram chat ID: 5738935134 ✅

---

## 7. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `openclaw_configured` | Config de OpenClaw actualizada |
| `telegram_channel_connected` | Bot responde en Telegram |

---

## 8. Kill Criteria

Si OpenClaw no acepta la configuración después de 3 intentos (`openclaw doctor --fix`), abortar y reportar error de schema.

---

## 9. Scale Criteria

- Múltiples agentes en OpenClaw (uno para producción, uno para desarrollo)
- Skills avanzados: consulta a Neo4j, Qdrant, Redis vía MCP
- Heartbeat: que el agente haga check-in cada 30min por Telegram
