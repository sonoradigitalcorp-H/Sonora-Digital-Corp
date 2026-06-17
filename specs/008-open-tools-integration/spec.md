---
id: 008
title: Open Tools Integration (Aider + Open Design)
status: draft
type: infrastructure
---

# Spec 008 — Open Tools Integration

## Propósito
Eliminar la construcción manual de landings, dashboards, slides y prototipos. En su lugar, usar **Open Design** (259 skills, 142 design systems) y **Aider** (42k ⭐, multi-model) como motor de generación visual y de código. El agente JARVIS orquesta, las herramientas ejecutan. No más HTML a mano.

## Stack Objetivo

| Herramienta | Rol | Licencia | Estrellas |
|---|---|---|---|
| **Open Design** | Generación de UI: landings, dashboards, slides, imágenes, video | Apache-2.0 | 64k ⭐ |
| **Aider** | Edición de código: features, fixes, refactors multi-file | MIT | 42k ⭐ |
| **JARVIS (Hermes)** | Orquestador: recibe orden, delega en OD/Aider, verifica | Propietario | — |
| **fal.ai** | Imágenes únicas (flux-schnell) para productos AzREC/Zamora | API | — |
| **Bitso Business** | Cobros SPEI automatizados con CLABE virtual | API | — |

## Por qué esto cambia todo

**Antes:** Cada landing = horas/mono escribiendo HTML + CSS + JS a mano. Cada error de CI = debug manual. Cada deploy = copy-paste.

**Después:** 
1. Dices "landing para Zamora, estilo Abe Music Hub"
2. Open Design la genera con 1 click (skill + design system)
3. Aider retoca si necesitas cambios
4. JARVIS deploya a nginx
5. Cliente ve y paga por Bitso SPEI

## Components

### 1. Open Design Daemon (puerto 7456)
- Servicio systemd: `sonora-open-design`
- Skills instalados: landing-artist, catalog, dashboard, deck, social-post
- Design systems: Sonoran Sunset (AzREC), Abe Music, Zamora (a crear)

### 2. Aider CLI wrapper
- Script: `bin/aider-session.sh`
- Usa modelo local (Ollama) para tareas simples, Claude API para complejas
- Integrado con git: commits automáticos con formato SDD

### 3. Payment Pipeline (Bitso)
- CLABE virtual por producto/cliente
- Webhook → notificación Telegram + email
- Liberación automática de acceso tras pago

## Archivos
- `services/open-design/` — config + systemd
- `bin/aider-session.sh` — wrapper Aider
- `products/*/landing/` — generado por OD, no manual
- `services/payments/` — webhook Bitso + liberación

## Dependencias
- Node.js ≥22 (Open Design)
- Python ≥3.10 (Aider)
- Docker (si OD corre en contenedor)
- Bitso Business API key (pendiente)
- Tokens Telegram (pendientes)

## Verification
- [ ] `od mcp install hermes` funciona
- [ ] Aider puede leer y modificar `src/` con cualquier modelo
- [ ] Open Design genera landing AzREC en <60s
- [ ] Bitso webhook recibe pago y libera acceso en <5s
- [ ] Pipeline completo: brief → OD → Aider → deploy → cobro
