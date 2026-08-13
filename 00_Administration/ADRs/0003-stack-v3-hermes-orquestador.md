# SPEC — STACK SONORA DIGITAL CORP v3
**Fecha:** 2026-08-12 · **Autor:** Hermes (en representación de Luis Daniel Guerrero Enciso)
**Estado:** APROBADA · **Reemplaza:** especificación implícita multi-OpenClaw (eliminada)

---

## 1. Objetivo

Definir la arquitectura de la plataforma Sonora Digital Corp donde:

- **Hermes es EL ORQUESTADOR** — el cerebro que gestiona agentes, bots, mensajería,
  cron, memoria y ventas.
- **OpenCode es un COMPONENTE** de la estructura (herramienta de desarrollo/escritura
  de código y ejecución de tareas), **NO** el que hace todo ni el que decide la
  arquitectura.
- **Composio es parte del stack** — proveedor de tools de terceros (Google,
  WhatsApp, Telegram, redes sociales) para los agentes de Hermes.

## 2. Decisiones canónicas de arquitectura

| # | Decisión | Detalle |
|---|----------|---------|
| D1 | Hermes orquesta | Gateway Hermes (`hermes-gateway.service`, systemd user) es el único motor 24/7. |
| D2 | Hermes Desktop = puerta | La app de escritorio se conecta al gateway (modo api → 127.0.0.1:8643) y es la interfaz principal. |
| D3 | OpenCode = componente | OpenCode edita/escribe código y ejecuta tareas de desarrollo. Obedece el AGENTS.md y las reglas canónicas. No crea procesos de orquestación paralelos. |
| D4 | Composio en el stack | Composio provee tools (gmail, calendar, whatsapp, telegram, IG, FB) a los agentes vía `COMPOSIO_API_KEY`. |
| D5 | Modelo canónico | `deepseek/deepseek-v4-flash-0731` (OpenRouter). Fallbacks: `deepseek-v4-flash`, `qwen3:4b` VPS. |
| D6 | Todo pesado en VPS | MCP pesado/fastmcp/gateway remoto/npx → VPS OVH `149.56.46.173` o proveedor remoto. Local solo ligero. |
| D7 | Un Hermes por cliente | Cada cliente/persona = un agente en `~/.hermes/agents/<id>/` (nicho + persona + skills + reglas + límites). |
| D8 | Personas | Toda persona se reconoce por nombre/número/chat_id/empresa (people_index). Memoria aislada por tenant. |

## 3. Roles de los componentes

### 3.1 Hermes (ORQUESTADOR)
- **Gateway** `hermes-gateway.service` → puerto API `127.0.0.1:8643` (OpenAI-compatible).
- **Plataformas:** Telegram (bots de clientes), WhatsApp (bridge), api_server.
- **Cron jobs** de orquestación (health, briefing, billing).
- **Memoria:** state.db + memory_store.db + Engram.
- **Agentes:** factory materializa agentes por nicho desde orden natural.

### 3.2 Hermes Desktop (interfaz)
- App Electron `/opt/Hermes One/hermes-desktop`.
- Conexión al gateway: `desktop.json` → `connectionMode=api`, `remoteUrl=http://127.0.0.1:8643`, `remoteApiKey=<API_SERVER_KEY>`.
- Es la puerta de acceso de Luis al sistema.

### 3.3 OpenCode (componente de desarrollo)
- Ejecuta código, edita archivos, despliega cambios.
- **NO** levanta servicios de orquestación propios.
- **NO** decide arquitectura — la decide Hermes y las reglas canónicas.
- Lee `AGENTS.md` (reglas) y `ESTADO.md` (estado vivo).
- Usa Engram para memoria persistente entre sesiones.

### 3.4 Composio (tools externas)
- Provee conectores: Google Calendar, Gmail, WhatsApp, Telegram, Instagram, Facebook, GitHub.
- Key en `~/.composio/agent.json` (cuenta `happy-lantern-hare`).
- Cada agente declara `composio.toolkits` en su `agent.yaml`.
- Automatización de redes: `social_autopilot.py`.

### 3.5 Agentes (un Hermes por cliente/nicho)
- `~/.hermes/agents/<id>/` con `agent.yaml` + `persona.md` + `reglas.md` + `manual.md` + `skills/`.
- Factory: `hermes_agent_factory.py --orden "..." --id <agente>`.
- Exposición MCP: `hermes_agents_mcp.py` (server stdio, tools list_agents/agent_info/agent_shell/...).

## 4. Flujo de alto nivel

```
Luis (Hermes Desktop)  →  Hermes Gateway (8643)  →  ORQUESTADOR
                                 │
        ┌────────────────────────┼─────────────────────────┐
        │                        │                         │
   Telegram bots          WhatsApp bridge              api_server
   (clientes)              (redes/cliente)          (web /chat, sonoradigitalcorp.com)
        │                        │                         │
   agentes/<cliente>        social_autopilot           widget chat
   (persona+skills+reglas)  (Composio IG/FB)          /api/v1/chat
        │                        │
   Composio toolkits        fal.ai (imagen/voz)
```

## 5. Reglas de operación

1. Hermes es el único que arranca gateway/bots/cron.
2. OpenCode no lanza procesos de orquestación; solo edita y ejecuta tareas de desarrollo.
3. Composio se conecta bajo demanda; no hay proceso pesado local.
4. Toda persona se reconoce (people_index) y su memoria es aislada por tenant.
5. Nunca correr modelos pesados en local (RAM 3.3GB).
6. Skills = capacidades reutilizables; persona.md = personalidad única por agente.

## 6. Entregables (ya implementados)

- [x] Hermes v0.20.0 actualizado, gateway activo (8643).
- [x] Hermes Desktop reconectado (modo api).
- [x] Modelos precargados (0731 + fallbacks).
- [x] Multi-tenant: tenants.json + tenant_router.py.
- [x] Personas: people_index.py + people.json + databases.json + skill people-recognition.
- [x] Agentes: esqueleto, plantillas por nicho, factory, agents_registry, MCP server.
- [x] Composio: check de conexiones (IG ACTIVE), social_autopilot.py.
- [x] Web de ventas: paquetes.html, agentes.html, chat.html + /api/v1 en nginx.

## 7. Pendientes

- [ ] Conectar Facebook en Composio (no aparece en la cuenta — sólo IG + github).
- [ ] Regenerar FAL_KEY (vencida, HTTP 401).
- [ ] Re-escanear QR de WhatsApp (sesión caducada).
- [ ] Regenerar token de @Aztro_tech_bot (revocado).
