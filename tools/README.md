# Tools — Catálogo

Este directorio organiza las tools por dominio de negocio. Los archivos `.js` reales permanecen en `mcp/tools/` para compatibilidad. Este directorio contiene referencias (`.md`) que describen cada tool y su ubicación real.

## Estructura

```
tools/
├── mcp/       → Tools del gateway MCP (hermes, openclaw, brain, skills, agent-converse)
├── system/    → Tools del sistema (files, commands, voice, memory, mcp, healthcheck, search, tests, docker, user)
├── business/  → Tools de negocio (payments, sales, content, media, music, viral, mystikverse, zamora, approvals, billing, store, design-tools, generator, intake, webhooks, score, music-providers)
└── abe/       → Tools de ABE Music (abe, abe-connect, abe-hub, abe-store)
```

## Referencia cruzada

Cada tool en `tools/X/Y.md` referencia su archivo `.js` en `mcp/tools/` o su implementación Python en `apps/`.
