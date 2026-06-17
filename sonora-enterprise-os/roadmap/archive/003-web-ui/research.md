# Research: Web UI
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| FastAPI + Jinja2 | Sin build step, Python puro, SSE nativo | Menos interactivo que React | ✅ Seleccionado |
| Next.js 16 | SSR, componentes, ecosistema | Build step, Node.js dependency | ❌ Descartado (overhead) |
| Svelte | Ligero, reactivo | Ecosistema pequeño | ❌ Descartado |
## Decisión Arquitectónica
- **Selección**: FastAPI + HTML/CSS/JS vanilla + SSE streaming
- **Motivo**: Cero build step, directo, PWA-ready, mismo lenguaje que el backend
## Limitaciones
1. Sin framework JS, la interactividad es manual
2. La UI legacy (three-panel) está deprecada
