# Research: Modularización del Core
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| Package por módulo | Separación clara, imports explícitos | Múltiples archivos | ✅ agents/, tools/, routes/ |
| Monolito | Simple, un archivo | Difícil de mantener, 1,000+ líneas | ❌ Reemplazado |
## Decisión Arquitectónica
- **Selección**: Paquetes Python por dominio (agents/, tools/, routes/)
- **Motivo**: Cada módulo < 200 líneas, responsabilidad única, testeable independientemente
## Limitaciones
1. Mayor número de imports y archivos
2. Posibles imports circulares si no se diseñan bien las dependencias
