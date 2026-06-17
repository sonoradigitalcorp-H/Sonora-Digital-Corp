# Research: Infraestructura de Tests
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| pytest | Estándar Python, fixtures, plugins, async | Configuración inicial | ✅ Framework principal |
| unittest | Built-in, sin dependencias | Verboso, menos features | ❌ Descartado |
| pytest-cov | Cobertura integrada | Overhead en CI | ✅ Cobertura |
| logrotate | Nativo Linux, configuración simple | Solo Linux | ✅ Log management |
## Decisión Arquitectónica
- **Selección**: pytest + pytest-asyncio + pytest-cov + logrotate + CI/CD GitHub Actions
- **Motivo**: Stack estándar de testing Python con cobertura y rotación de logs
## Limitaciones
1. Sin tests de integración con LLM real (mocked)
2. La cobertura actual no está medida formalmente
