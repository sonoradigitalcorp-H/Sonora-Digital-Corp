# Plan: Open Tools Integration

## Objetivo
Dejar de construir UI manualmente. Open Design genera, Aider edita, JARVIS orquesta, Bitso cobra. 100% pipeline automatizado.

## Fase 1 — Instalación (Día 1)
- [ ] Descargar Open Design desktop + CLI
- [ ] `od mcp install hermes` — conectar a JARVIS
- [ ] Instalar Aider (`pip install aider-chat`)
- [ ] Crear design system Sonoran Sunset en OD
- [ ] Crear design system Zamora en OD
- [ ] Probar: generar landing Zamora con skill `landing-artist`

## Fase 2 — Integración con JARVIS (Día 2-3)
- [ ] Script `bin/od-generate.sh` — wrapper: brief → OD → deploy
- [ ] Script `bin/aider-session.sh` — wrapper: tarea → Aider → commit
- [ ] Service systemd para OD daemon (puerto 7456)
- [ ] nginx proxy `/design/` → localhost:7456
- [ ] Probar: "genera landing Zamora" desde Telegram

## Fase 3 — Payment Pipeline (Día 3-5)
- [ ] Registro Bitso Business (usuario)
- [ ] API key → `.env`
- [ ] Webhook service: `services/payments/webhook.py`
- [ ] CLABE virtual por producto
- [ ] Notificación Telegram al recibir pago
- [ ] Liberación automática de contenido digital

## Fase 4 — Automatización Total (Día 5-7)
- [ ] GitHub Action: PR → Aider review → auto-merge
- [ ] Open Design automation: brief semanal → deck automático
- [ ] Pipeline: brief → OD genera → Aider pule → deploy → cobro
- [ ] Dashboard de métricas: cuánto se generó, cuánto se cobró

## Riesgos
- OD requiere Node.js ≥22 (instalar si no está)
- OD desktop no tiene Linux build oficial (usar Docker o CLI-only)
- Aider con modelo local (Ollama) puede ser lento en 3.2GB RAM
- Bitso KYC toma 2-6 semanas

## Mitigaciones
- OD CLI-only + MCP = no necesita GUI
- Aider con Claude API (no local) para tareas complejas
- Mercado Pago como respaldo mientras llega Bitso
- OD skills custom: crear skill `landing-zamora` con imágenes fal.ai

## Archivos a modificar
- Crear: `services/open-design/`, `bin/od-generate.sh`, `bin/aider-session.sh`
- Crear: `services/payments/webhook.py`, `services/payments/requirements.txt`
- Crear: `design-systems/azrec/`, `design-systems/zamora/`
- Modificar: nginx config (proxy /design/)
- Modificar: `.env` (BITSO_API_KEY, etc.)
