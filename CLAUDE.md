# CLAUDE.md — Protocolo de Operación

## Regla Absoluta #1: Directorio de Trabajo

Siempre debes ejecutarte DESDE `/home/mystic/sonora-digital-corp/`.

Si no estás en ese directorio, el agente NO tendrá acceso a:
- `opencode.json` (agentes, comandos, constitution)
- `process/` (pipeline de SPECs)
- `sonora-enterprise-os/constitution/` (reglas, TRUTH, OMEGA-PROMPT)
- `.github/hooks/` (gates de git)

## Si detectas que NO estás en el directorio correcto:
1. Informa al usuario inmediatamente
2. No ejecutes ninguna acción hasta que el usuario cambie al directorio correcto
3. Sugiere: `cd /home/mystic/sonora-digital-corp && opencode`

## Archivo de configuración maestro:
`/home/mystic/sonora-digital-corp/opencode.json`

## Referencia rápida:
@AGENTS.md
