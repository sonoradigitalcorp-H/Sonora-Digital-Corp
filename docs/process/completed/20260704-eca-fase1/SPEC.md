# SPEC-20260704-ECA — Enterprise Cognitive Architecture: Fase 1

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260704-ECA` |
| **Fecha** | 2026-07-04 |
| **Tier** | 3 |
| **Score** | TBD |

## Resumen

Reorganización completa del sistema en 7 niveles cognitivos (Observar → Entender → Decidir → Actuar → Medir → Aprender + Control). Implementación de Execution Kernel (cola de tareas, prioridad, retry, checkpoint, CLI, API) y Evolution Loop (proposer, simulator, auto-implement). Artist Intelligence Network (4 collectors + normalizer + metrics engine). Stack Lock, Control Plane, Scoreboard Dashboard, GitHub Pages, Vercel Secrets.

## Módulos

| Módulo | Descripción | Archivos | Tests |
|--------|-------------|----------|-------|
| Stack Lock | docs/STACK-LOCK.md + PRINCIPLE-010 | 2 nuevos | — |
| Scoreboard Dashboard | SPA interactivo + mejoras to_html() | 2 nuevos, 2 mod | — |
| GitHub Pages | docs/index.html portal | 1 nuevo | — |
| Vercel Secrets | 4 GitHub Secrets configurados | 0 | — |
| Reorganizar apps/ | 7 subdirectorios + backward compat | ~15 movidos, 0 borrados | — |
| Control Plane | dashboard 4 paneles + api endpoints | 2 nuevos | — |
| Artist Intelligence | 4 collectors + base + scheduler | 15 nuevos | 17 |
| Execution Kernel | queue + scheduler + checkpoint + executor + CLI + API + truth | 10 nuevos, 3 mod | 24 |
| Evolution Loop | store + proposer + simulator + loop + policy | 8 nuevos | 19 |
| **Total** | **~40 nuevos, ~15 movidos, 0 borrados** | **~55 total** | **60** |

## Archivos clave creados

| Archivo | Propósito |
|---------|-----------|
| `collectors/base.py` | ABC Collector, Normalizer, MetricsEngine |
| `collectors/registry.yaml` | 4 plataformas + 3 artistas |
| `collectors/scheduler.py` | Auto-descubre y corre collectors |
| `apps/decide/execution/queue.py` | TaskQueue SQLite persistente |
| `apps/decide/execution/scheduler.py` | PriorityScheduler + backoff |
| `apps/decide/execution/checkpoint.py` | Checkpoint/Resume |
| `apps/decide/execution/executor.py` | AgentExecutor con handlers |
| `scripts/execution.py` | CLI con 6 comandos |
| `truth/45-execution.yaml` | 5 reglas de ejecución |
| `apps/learn/evolution/store.py` | Propuestas persistentes |
| `apps/learn/evolution/proposer.py` | Analiza scoreboard + heuristics |
| `apps/learn/evolution/simulator.py` | Estima impacto en score |
| `apps/learn/evolution/loop.py` | Ciclo completo |
| `docs/STACK-LOCK.md` | Stack congelado v1 |
| `apps/measure/guardian/static/control.html` | Control Plane SPA |
| `apps/measure/guardian/static/scoreboard.html` | Scoreboard interactivo |

## Tests

| Suite | Tests |
|-------|-------|
| collectors (test_base.py) | 17 |
| execution (test_execution.py) | 24 |
| evolution (test_evolution.py) | 19 |
| truth (test_truth.py) | 10 (2 actualizados) |
| ABE Service | 9 |
| **Total** | **79** |

## Score estimado: 88/100

| Métrica | Score |
|---------|-------|
| Objetivo | 10 |
| Value Driver | 9 |
| FRs | 9 |
| Success Criteria | 9 |
| Ejecutabilidad | 9 |
| Innovación | 8 |
| **Total** | **88** |
