# ARQUITECTURA FINAL — Sonora Digital Corp

## Visión 2026-Q3

```
De una plataforma de infraestructura → PRODUCTOS FUNCIONALES
```

## Principios

1. **Un código base** (`~/sdc/`) — cero dispersión
2. **Un pipeline** (SPEC→Score→TDD→ADR→Lección)
3. **Una memoria** (Engram + Redis Streams)
4. **Un governance** (CI invisible, branch protection, gates server-side)
5. **Múltiples productos** (mystika, yami, booking, etc.)

---

## 🏗️ Arquitectura por Capas

```
┌─────────────────────────────────────────────────────────────┐
│                     PRODUCTOS                               │
│  mystika  │  yami  │  booking  │  telegram-masterclass     │
│  (educación musical + NSFW)                                 │
├─────────────────────────────────────────────────────────────┤
│                     CLIENTES                                │
│  abe-music (Abraham)  │  azrec (Zamora)                    │
├─────────────────────────────────────────────────────────────┤
│                     CORE (motor de la empresa)              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  APIs: WebUI (:5174)  │  Agentes (18)  │  JARVIS    │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  Memoria: Engram + Redis Streams + events.jsonl     │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  Pipeline: SPEC→Score→TDD→ADR→Lección               │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  Governance: CI gates + Branch Protection + Hooks   │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     PLATAFORMAS                             │
│  Telegram (98 skills)  │  WhatsApp  │  Web                 │
├─────────────────────────────────────────────────────────────┤
│                     INFRAESTRUCTURA                         │
│  VPS OVH (149.56.46.173)                                    │
│  11 containers Docker (Python 3.12-slim)                    │
│  Nginx + Let's Encrypt SSL                                  │
│  UFW: solo 22/80/443                                        │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Roadmap a Productos Funcionales

### Fase Inmediata (esta semana)

| Tarea | Producto | Tiempo |
|-------|----------|--------|
| Hacer revenue pipeline funcional → 1 lead real | SDC Platform | 1 día |
| Cerrar 14 vulnerabilidades Dependabot | Infra | 2 horas |
| Fix langfuse healthcheck | Infra | 30 min |
| MCP Server monitoreo + alertas | Infra | 1 hora |
| Limpiar 27 errores ruff restantes | Core | 30 min |

### Fase Corto Plazo (2 semanas)

| Tarea | Producto |
|-------|----------|
| SPEC-016 PromptOps & Skills Registry | Core |
| Mission Control dashboard funcional | SDC Platform |
| Mystika: onboarding + planes de suscripción | mystika |
| Yami: módulo de colaboración | yami |
| ABE Music: pipeline de reels automáticos | abe-music |
| Azurec: tienda en línea funcional | azrec |

### Fase Mediano Plazo (1 mes)

| Tarea | Producto |
|-------|----------|
| Multi-tenant engine (organizaciones + roles) | Core |
| Unified AI Gateway (OpenAI + Anthropic + Ollama) | Core |
| Self-healing engine (auto-recovery de containers) | Infra |
| Billing platform (Stripe + suscripciones) | SDC Platform |
| Customer portal (login + dashboard + facturas) | SDC Platform |

---

## 📐 Decisiones de Arquitectura (ADR)

| ADR | Decisión | Status |
|-----|----------|--------|
| ADR-001 | Docker containers sobre systemd | ✅ Implementado |
| ADR-002 | Redis Streams como sistema nervioso | ✅ Implementado |
| ADR-003 | Branch protection + CI gates server-side | ✅ Implementado |
| ADR-004 | Labels sdc.domain para organización | ✅ Implementado |
| ADR-005 | Engram como memoria central (SQLite+FTS5) | ✅ Implementado |
| ADR-006 | Python 3.12 en containers (independiente del host) | ✅ Implementado |
| ADR-007 | Monorepo ~/sdc/ con products/ + clients/ | ✅ Implementado |
| ADR-008 | Todo SPEC tiene score gate ≥60 | ✅ Implementado |
| ADR-009 | PromptRegistry + SkillRegistry unificado | ⬜ Pendiente |

---

## 📊 Métricas Objetivo

| Métrica | Hoy | Meta Q3 |
|---------|-----|---------|
| Enterprise Score | 23/100 | 60/100 |
| Tests | 442 | 500+ |
| Cobertura | 62% | 75%+ |
| Clients activos | 2 (abe-music, azrec) | 5+ |
| Revenue mensual | $0 | $5,000+ MXN |
| Engram memories | 246 | 1,000+ |
| SPECs completados | 9 | 20+ |
| Containers health | 2 unhealthy | 0 unhealthy |
