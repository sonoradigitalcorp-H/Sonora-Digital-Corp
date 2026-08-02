# SPEC-20260704-EXECUTION — Execution Kernel

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260704-EXECUTION` |
| **Fecha** | 2026-07-04 |
| **Tier** | 2 |
| **Score target** | 85/100 |

## Objetivo

Scheduler unificado para operaciones de agentes con cola persistente, prioridad, retry con backoff, checkpoint/resume, y API en Guardian. Orquesta ejecución de agentes, no timers del sistema (cron/systemd/n8n siguen existiendo para scheduling de infraestructura).

## Arquitectura

```
CLI (scripts/execution.py)  ←  Guardian API (/api/v1/execution/)
            │
            ▼
      Task Queue (SQLite)
    ┌───────┼───────┐
    ▼       ▼       ▼
 queued  running  completed/failed/cancelled
            │
            ▼
     Priority Scheduler
            │
            ▼
      Agent Executor
    ┌───┬───┬───┬───┐
    ▼   ▼   ▼   ▼   ▼
 mystic builder hermes devops auditor
```

## FRs

| FR | Descripción | Criterio |
|----|-------------|----------|
| FR1 | Task queue con SQLite persistente | Estados: queued, running, completed, failed, cancelled |
| FR2 | Priority scheduler (L1 > L2 > L3) | Máx 2 concurrentes por agente |
| FR3 | Retry engine con backoff exponencial | 1s → 5s → 30s → 5min, max 3 retrys |
| FR4 | Checkpoint/resume para tareas largas | Estado parcial guardable |
| FR5 | CLI: submit, status, cancel, retry, list | 5 comandos |
| FR6 | Guardian API: queue, tasks, stats | 3 endpoints |
| FR7 | Execution Agent en registry | Nuevo agente |

## NO reemplaza

- **cron** — para tareas de sistema (backups, healthchecks)
- **systemd timers** — para servicios
- **n8n** — para flujos visuales multi-paso

El Execution Kernel orquesta **operaciones de agentes**: tareas de análisis, generación, revisión, deploy, que lógicamente pertenecen al Cognitive Kernel.

## Archivos a crear

| Archivo | Propósito |
|---------|-----------|
| `apps/decide/execution/queue.py` | Core task queue (SQLite) |
| `apps/decide/execution/scheduler.py` | Priority + retry + concurrency |
| `apps/decide/execution/checkpoint.py` | Checkpoint/resume |
| `apps/decide/execution/__init__.py` | Package init |
| `scripts/execution.py` | CLI interface |
| `agents/capabilities/execution.yaml` | Capability |
| `truth/45-execution.yaml` | Reglas de ejecución |
| `state/execution/` | DB + checkpoints |
| `tests/test_execution.py` | Tests |

## Criterios de éxito

- [ ] Queue persiste entre reinicios (SQLite)
- [ ] Prioridad L1 corre antes que L2
- [ ] Retry backoff respeta tiempos
- [ ] Checkpoint guarda y resume estado
- [ ] CLI funciona: submit, status, cancel, retry, list
- [ ] Guardian endpoints responden
- [ ] Agent registry actualizado

## Riesgos

- Confusión con scheduler.js existente en mcp/ (mitigación: execution kernel es para agentes, mcp/scheduler es para MCP tools)
- Duplicación con planner/decision_engine.py (mitigación: execution kernel es cola, decision_engine es selección de proveedor)
