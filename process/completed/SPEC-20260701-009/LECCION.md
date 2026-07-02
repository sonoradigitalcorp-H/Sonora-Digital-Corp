# Lecciones — SPEC-20260701-009

## Lo que funciono bien
1. OpenClaw auto-detecta el modelo ollama sin configurar baseUrl
2. `openclaw config set` maneja la validacion de schema automaticamente
3. Telegram bot responde inmediatamente despues de configurar el canal

## Lo que no funciono
1. `agents.defaults.instructions` no existe en el schema de OpenClaw
2. El system prompt debe ir en AGENTS.md en el workspace del agente, no en la config
3. `openclaw doctor` no tiene un comando `restart` — solo `openclaw` reinicia via systemd

## Proxima vez
1. No buscar `instructions` en el schema de OpenClaw — usar AGENTS.md
2. Verificar con `openclaw health` despues de cada cambio de config
