# Research: Ecosistema Completo
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| OpenClaw ClawHub | 5,000+ skills, SKILL.md estándar | Gateway local | ✅ Skills externas |
| Hermes Platforms | 10 adapters multi-canal | Dependencia de token | ✅ Mensajería |
| n8n Workflows | 400+ integraciones, self-hosted | Recursos | ✅ Automatización |
## Decisión Arquitectónica
- **Selección**: OpenClaw (skills) + Hermes (canales) + n8n (workflows) + SDD (metodología)
- **Motivo**: Stack completo que cubre skills, comunicación, automatización y calidad
## Limitaciones
1. Sin monitoreo centralizado de todos los componentes
2. Dependencia de servicios externos (GitHub, Vercel) para CI/CD
