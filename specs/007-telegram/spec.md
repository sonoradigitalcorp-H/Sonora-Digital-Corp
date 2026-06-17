---
id: 007
title: Telegram Bot Architecture
status: active
type: feature
---

# Spec 007 — Telegram Bot Architecture

## Propósito
Arquitectura de bots de Telegram para Sonora Digital Corp: bots de ventas, comunidad, comunicación entre agentes, mini-apps y automatización.

## Componentes
1. **Hermes Telegram Bot** (puerto 3003) — 3 bots: default, admin, abraham. 97 skills.
2. **AzREC Bot** — Ventas + catálogo de productos. Script listo, token pendiente.
3. **Abe Music Bot** — Showcase de artistas. Script listo, token pendiente.

## Features
- Catálogo interactivo con inline keyboards
- Asistente de ventas con flujo de compra
- Comunicación entre bots via n8n
- Mini-apps: catálogo, trivia musical (próximamente)
- Grupos de comunidad: AzREC, Abe Music

## Archivos
- `/home/mystic/products/azrec/telegram/bot-azrec.py`
- `/home/mystic/products/abe-music/telegram/bot-abe.py`
- `/home/mystic/products/telegram-masterclass/` (9 módulos)

## Dependencias
- Python Telegram Bot library
- Tokens de @BotFather (pendientes para AzREC y Abe Music)
- Servicio Hermes Telegram en puerto 3003

## Verification
- [ ] Hermes bot responde en puerto 3003 (3 bots activos)
- [ ] AzREC bot script funcional (falta token)
- [ ] Abe Music bot script funcional (falta token)
- [ ] Masterclass documentación completa
