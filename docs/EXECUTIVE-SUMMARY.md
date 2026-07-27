# Sonora Digital Corp — Executive Summary

**Versión:** 3.1.0 · **Último commit:** `0548123` · **Branch:** `main`
**Fecha:** 2026-07-26 · **Reestructuración mayor completada**

---

## 📊 Métricas Clave

| Métrica | Valor |
|---------|-------|
| Directorios raíz | **18** (bajó de 43) |
| Archivos raíz | **7** (bajó de 28) |
| Apps core | **37** en `apps/` |
| Skills | **51** en `skills/` |
| Scripts | **65** en `scripts/` |
| Productos | **~20** en `products/` |
| Clientes | **5** en `clients/` |
| ADRs | **13** documentados |
| Commits | **402** en main |
| Tests | **916 checks** en preflight |

---

## 🏗️ Arquitectura — 6 Capas Concéntricas

```
kernel/   ← Capa 0: Identidad, reglas, constitución (30 archivos)
infra/    ← Capa 1: Infraestructura (Docker, nginx, fleet.yml)
apps/     ← Capa 2: Servicios core (37 apps, motor principal)
products/ ← Capa 3: Lo que SDC vende (mystika, clon-digital, etc.)
clients/  ← Capa 4: Clientes externos (ABE Music, Aztrotech, etc.)
portal/   ← Capa visual: Grimoire 3D (Three.js galaxy)
```

**Transversales:** `ops/` (playbooks), `state/` (estado vivo), `reference/` (arqueología)

---

## 📁 Estructura Raíz (18 directorios)

| Directorio | Contenido |
|-----------|-----------|
| `apps/` | Core: engine, evolution, hermes, voice, webui, frontends, etc. |
| `backups/` | Backups diarios + archive histórico |
| `clients/` | 5 clientes: ABE Music, Aztrotech, Cesar, Hermosillo CC, Joyería |
| `config/` | Config, tenants, secrets |
| `docs/` | Documentación, mapas, presentaciones |
| `infra/` | Docker compose, fleet.yml, FreeSWITCH, nginx |
| `kernel/` | Constitución: OMEGA-PROMPT, SOUL, TRUTH, 10-RULES |
| `mcp/` | MCP SDK + servers (legacy coexistente) |
| `ops/` | Playbooks, runbooks de operaciones |
| `portal/` | Grimoire 3D (Three.js) |
| `process/` | Pipeline SDD: specs activos, completados, templates |
| `products/` | ~20 productos: mystika, clon-digital, notifier, affiliates, etc. |
| `reference/` | Especs cerradas, arqueología |
| `scripts/` | 65 herramientas de automatización y DevOps |
| `skills/` | 51 skills canónicas + SDD pipeline |
| `state/` | Estado vivo: events, media, quality, engram |
| `tests/` | Tests unitarios, BDD, integración, evals, promptfoo |
| `adrs/` | 13 Architecture Decision Records |

**Archivos raíz (7):** `AGENTS.md` · `CLAUDE.md` · `Makefile` · `opencode.json` · `pyproject.toml` · `README.md` · `requirements.txt`

---

## 🧠 Core Apps (apps/)

| App | Propósito |
|-----|-----------|
| `core/` | Motor principal: engine, planner, agents, executors |
| `evolution/` | Auto-evolución, scorecard, aprendizaje continuo |
| `hermes/` | Gateway multi-canal (Telegram, WhatsApp, Desktop) |
| `webui/` | Frontend FastAPI (puerto 5174) |
| `voice/` | STT/TTS (speech-to-text, text-to-speech) |
| `frontends/` | HTML/CSS/JS landings y dashboards |
| `whatsapp/` | Webhook WhatsApp |
| `abe-service/` | ABE Music OS |
| `sonora_engine/` | Motor alternativo (FastAPI + WebSocket) |

---

## 🛠️ Comandos Rápidos

```bash
make               # Lista todos los comandos
make doctor-quick  # Preflight check rápido
make test          # Tests unitarios
make eval          # Evaluaciones estructurales
make score         # Enterprise Score
make lint          # Ruff linting (local)
```

---

## 🔗 Enlaces Rápidos

| Recurso | Ruta |
|---------|------|
| Constitución | `kernel/OMEGA-PROMPT.md` |
| Reglas | `kernel/10-RULES.md` |
| Verdad | `kernel/TRUTH.md` |
| Mapa | `docs/MAPA-SDC.md` |
| Blueprint completo | `docs/BLUEPRINT.md` |
| ADR arquitectura | `adrs/ADR-20260722-ARQUITECTURA-CORE.md` |

---

*Generado por Mystic (SDC Orchestrator) — 2026-07-26*
