# Research: Constitución
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| CLAUDE.md inline | Simple, visible | Solo visible en Claude Code | ✅ Usado + archivo separado |
| SPECS formales | Trazabilidad completa | Más overhead | ✅ usados como complemento |
## Decisión Arquitectónica
- **Selección**: CLAUDE.md + constitution.md dual
- **Motivo**: CLAUDE.md expuesto al LLM automáticamente; constitution.md como fuente de verdad vinculante
## Limitaciones
1. CLAUDE.md no es vinculante para herramientas externas (OpenClaw, Hermes)
2. La constitución necesita ratificación periódica
