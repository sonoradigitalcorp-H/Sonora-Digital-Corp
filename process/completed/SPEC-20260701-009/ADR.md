# ADR-20260701-009 — OpenClaw como Interfaz Conversacional

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260701-009` |
| **Fecha** | 2026-07-01 |
| **Spec** | `SPEC-20260701-009` |
| **Estado** | aceptado |

---

## Context

OpenClaw v2026.6.10 estaba instalado en el VPS pero sin configurar: sin proveedor LLM, sin canales, sin instrucciones de agente. El Telegram bot @ABEfenix_bot existía pero no estaba conectado a ningún agente. Luis Daniel no tenía forma de consultar el sistema desde el celular.

## Decision

### 1. Provider Ollama local como modelo principal

Se configuró `agents.defaults.model.primary = "ollama/deepseek-r1:7b-64k"`. OpenClaw auto-detecta el modelo a través de su plugin ollama. No se necesita configurar baseUrl porque el plugin usa `http://127.0.0.1:11434` por defecto.

### 2. Telegram channel con allowlist

Se configuró `channels.telegram` con el bot token de @ABEfenix_bot y `dmPolicy: allowlist` limitado al chat ID de Luis Daniel (5738935134). Esto asegura que solo él pueda hablar con el agente.

### 3. System prompt via AGENTS.md

OpenClaw no tiene un campo `instructions` en el schema. Las instrucciones del sistema se configuran a través de un archivo `AGENTS.md` en el workspace del agente. Se creó en `~/.openclaw/agents/main/workspace/AGENTS.md` con toda la arquitectura del sistema.

## Consequences

**Positivo:**
- Luis Daniel puede consultar el sistema desde Telegram
- El modelo local deepseek-r1:7b-64k se usa sin costo de API
- OpenClaw auto-detectó y habilitó el modelo automáticamente
- Sin cambios en servicios existentes

**Trade-offs:**
- El system prompt via AGENTS.md es menos flexible que un campo directo en config
- La primera respuesta puede tardar ~45s mientras deepseek carga en memoria
- OpenClaw no tiene acceso directo a Neo4j todavía (requiere SPEC-010)

## Related

- Config: `~/.openclaw/openclaw.json`
- Workspace: `~/.openclaw/agents/main/workspace/AGENTS.md`
- Telegram: @ABEfenix_bot
- Modelo: deepseek-r1:7b-64k via Ollama
