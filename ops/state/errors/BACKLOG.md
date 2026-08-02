# ERRORES + PENDIENTES — Backlog Unificado

## 🔴 CRÍTICOS (urgencia inmediata)

| # | Error | Desde | Síntoma |
|---|-------|-------|---------|
| E1 | **Langfuse unhealthy** | Siempre | Container langfuse nunca pasa healthcheck |
| E2 | **14 vulnerabilidades Dependabot** | GitHub | 2 high, 11 moderate, 1 low sin parchar |
| E3 | **No hay revenue real** | SPEC-002 | Pipeline de ventas armado pero 0 leads |
| E4 | **Enterprise Score 23/100** | SPEC-001 | Sin revenue events, sin customer data |
| E5 | **Puertos 3001/4000 se reabren solos** | Security audit | mystika processes reaparecen |

## 🟡 DEUDA TÉCNICA

| # | Error | Desde | Solución propuesta |
|---|-------|-------|-------------------|
| E6 | **26 errores E501 (line-too-long)** | Lint audit | Aceptados como cosméticos |
| E7 | **1 error I001 (unsorted imports)** | Lint audit | `ruff check --fix` lo arregla |
| E8 | **PyAudio no compila en container** | SPEC-003 | Voice module separado |
| E9 | **Healthcheck webui lento (~1min)** | SPEC-003 | Interval 15s ya aplicado |
| E10 | **ENV defaults en Dockerfile** | SPEC-003 | Warnings de seguridad |
| E11 | **Ruff --fix revierte compat py3.10** | SPEC-005 | No usar --unsafe-fixes |
| E12 | **2 tests de ReviewAgent frágiles** | SPEC-003 | Pathes relativos, no absolutos |
| E13 | **score 60/100 con human override** | SPEC-000 | Necesita mejorar para ser autónomo |

## 🟢 PENDIENTES DE PRODUCTO

| # | Pendiente | SPEC relacionado | Prioridad |
|---|-----------|-----------------|-----------|
| P1 | **Pipeline de ventas: 0 leads reales** | SPEC-002 | Alta |
| P2 | **Engram pipeline loop: probar en VPS** | SPEC-007 | Alta |
| P3 | **Dependabot PRs: mergear batch** | — | Alta |
| P4 | **PromptOps & Skills Registry (SPEC-016)** | Planificado | Media |
| P5 | **Multi-tenant engine** | Planificado | Media |
| P6 | **Unified AI Gateway** | Planificado | Baja |
| P7 | **Agent Marketplace** | Planificado | Baja |
| P8 | **Mission Control en producción** | docs/mission-control.html | Media |

## 🔄 PATRONES DETECTADOS (auto-reasoning)

### Patrón 1: Bootstrap Problem recurrente
Cada vez que creamos un sistema de governance, este nos bloquea.
- **SPEC-003**: Branch protection bloqueó push inicial
- **SPEC-005**: Process gate bloqueó su propio PR
- **Solución**: Excepción automática para cambios en `.github/` y `process/`

### Patrón 2: Tres sistemas de skills paralelos
Enterprise OS (10), Telegram (98), OpenCode (9) — sin conexión entre sí.
- **Impacto**: Skills duplicadas, lógica repetida, mantenimiento triple
- **Solución**: SPEC-016 PromptRegistry + SkillRegistry

### Patrón 3: Pruebas sin datos reales
Revenue pipeline, Neo4j, Redis Streams — todo probado en vacío.
- **Impacto**: Cuando llegue el primer cliente real, van a aparecer bugs no detectados
- **Solución**: Test de integración con datos sintéticos

### Patrón 4: Python 3.10 vs 3.12
El host es 3.10, el container es 3.12. Ruff --fix revierte los parches.
- **Impacto**: Cada `ruff check --fix` puede romper compatibilidad
- **Solución**: No usar `ruff check --fix --unsafe-fixes`. Pin ruff version.
