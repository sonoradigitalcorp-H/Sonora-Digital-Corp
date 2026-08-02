# SPEC-20260704-EVOLUTION — Self-Evolution Loop

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260704-EVOLUTION` |
| **Fecha** | 2026-07-04 |
| **Tier** | 2 |
| **Score target** | 85/100 |

## Objetivo

Ciclo cerrado donde el sistema mide su propio desempeño, propone mejoras basado en métricas y heurísticas aprendidas, simula el impacto, implementa si es viable, y vuelve a medir. Sin intervención humana.

## Arquitectura

```
Measure (Scoreboard + Economics + Learning)
    ↓
Analyze (Evolution Proposer)
    ↓
Propose (candidate improvement)
    ↓
Simulate (dry-run en sandbox, estima impacto)
    ↓
Approve (si score mejora ≥5% y costo < umbral)
    ↓
Implement (auto-PR o config change)
    ↓
Measure (verificar que score mejora)
    ↓
Record (en truth/90-learned.yaml como heurística)
```

## FRs

| FR | Descripción | Criterio |
|----|-------------|----------|
| FR1 | Proposer analiza scoreboard + heurísticas + economics | Propuesta generada semanalmente |
| FR2 | Simulation engine ejecuta en sandbox | Impacto estimado con score antes/después |
| FR3 | Auto-implement si score mejora ≥5% y costo < $0 | PR creado automáticamente |
| FR4 | Eventos evolution.* emitidos en cada etapa | 4 eventos: proposed, simulated, implemented, measured |
| FR5 | Evolution Agent en registry | Nuevo agente con capabilities específicas |

## Archivos a crear

| Archivo | Propósito |
|---------|-----------|
| `apps/learn/evolution/proposer.py` | Analiza métricas → propuestas |
| `apps/learn/evolution/simulator.py` | Dry-run de propuestas, estima impacto |
| `apps/learn/evolution/loop.py` | Orquestador del ciclo |
| `apps/learn/evolution/__init__.py` | Package init |
| `agents/capabilities/evolution.yaml` | Capability definition |
| `agents/policies/70-evolution.yaml` | Policy restrictiva |
| `tests/test_evolution.py` | Tests |

## Criterios de éxito

- [ ] Proposer genera al menos 1 propuesta por semana basada en datos reales
- [ ] Simulation ejecuta sin efectos secundarios
- [ ] Auto-implement solo si score mejora ≥5%
- [ ] Todos los eventos evolution.* emitidos correctamente
- [ ] Truth Guardian reporta evolution metrics

## Riesgos

- Propuestas irrelevantes si los datos son pobres (mitigación: umbral mínimo de data quality)
- Auto-implement puede romper algo (mitigación: solo cambios en truth/ y config/, no en código productivo)
