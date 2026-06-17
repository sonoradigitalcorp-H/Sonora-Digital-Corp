# Implementation Plan: Web UI

**Spec**: [spec.md](./spec.md)

---

## Technical Context

**Language/Version**: Python 3.10+ (backend), JavaScript vanilla (frontend)
**Primary Dependencies**: fastapi, uvicorn, jinja2 (templates)
**Architecture**: FastAPI sirve HTML+JS+CSS, SSE endpoint para streaming
**Frontend**: JavaScript vanilla SPA (~950 líneas), CSS cyberpunk (~600 líneas)

## Constitution Check

| Principio | Cómo lo cumple |
|-----------|---------------|
| Separación de responsabilidades | Backend (FastAPI) separado del frontend (JS vanilla) |
| Privacidad y control | Frontend servido localmente, sin telemetría |
| Calidad y testing | Tests de API con TestClient |

## Implementación

### Archivos existentes

| Archivo | Propósito |
|---------|-----------|
| `webui/fastapp.py` | Backend FastAPI: 25+ endpoints, SSE streaming, file browser, voice API, n8n webhooks |
| `webui/static/app.js` | Frontend SPA: sesiones, chat, workspace, voice, keyboard shortcuts |
| `webui/static/style.css` | Tema cyberpunk: three-panel grid, responsive, animations |
| `webui/templates/index.html` | HTML template: three-panel layout |
| `tests/integration/test_api.py` | Tests de integración (217 lines) |

### Pendiente

| Tarea | Prioridad |
|-------|-----------|
| Responsive breakpoints para móvil (stack vertical) | P2 |
| Slash commands integrados en chat | P2 |
| Drag & drop para reordenar sesiones | P3 |
| Git status indicator en workspace (backend ya existe, frontend parcial) | P2 |

## Archivos del spec

```
specs.new/003-web-ui/
├── spec.md
├── plan.md
└── tasks.md
```
