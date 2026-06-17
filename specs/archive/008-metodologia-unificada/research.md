# Research: Metodología Unificada
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| SDD + GSD + Close-Loop + Learning-Loop | Stack completo, trazabilidad | Overhead de documentación | ✅ Seleccionado |
| Solo SDD | Spec-driven, simple | Sin ciclo de mejora | ❌ Descartado |
## Decisión Arquitectónica
- **Selección**: Stack de 4 capas: SDD → GSD → Close-Loop → Learning-Loop
- **Motivo**: Ciclo completo de diseño-ejecución-mejora continua
## Limitaciones
1. Overhead de documentación para features pequeños
2. Learning-Loop requiere GBrain disponible
