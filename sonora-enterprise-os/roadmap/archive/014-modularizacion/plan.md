# Implementation Plan: Modularización del Core

**Spec**: spec.md

---

## Constitution Check

| Principio | Cómo lo cumple |
|-----------|---------------|
| Separación de responsabilidades | Cada módulo hace una cosa |
| Arquitectura modular | Agentes, tools y routes en paquetes separados |
| Calidad y testing | Tests después de cada migración |
| Documentación | Spec 014 documenta el plan |

## Archivos

| Archivo | Propósito |
|---------|-----------|
| `src/core/agents/` | 10 agentes separados (~60 ln c/u) |
| `src/core/tools/` | 4 módulos: definitions, executors, router |
| `webui/routes/` | 14 routers por dominio |
| `src/core/orchestrator.py` | Routing + ejecución (161 ln) |

---

*Plan generated from spec*
