# Productos — Sonora Digital Corp

## Estructura

```
products/
├── production/       ← Servicios EN PRODUCCIÓN (corriendo 24/7)
│   ├── mystik/          → Asistente de ventas AI (:5200)
│   ├── content-studio/  → Generación de contenido AI (:8765)
│   ├── omnivoice/       → Clonación de voz AI (:3900)
│   └── abe-music-os/    → ABE Music OS (:5180)
│
├── catalog/           ← Lo que VENDEMOS (productos para clientes)
│   ├── mystik-ai/        → Planes: Starter, Pro, Enterprise
│   ├── content-studio/   → API de generación
│   ├── omnivoice/        → API de voz
│   └── open-notebook/    → RAG knowledge base
│
└── concepts/          ← IDEAS / protectos / experimentales
    ├── abe-portfolio/
    ├── booking/
    ├── chatbot/
    ├── yami/
    ├── mystika/
    ├── landing-artista/
    └── telegram-masterclass/
```

## Reglas

1. **production/**: Solo lo que está corriendo 24/7 en el VPS. Tiene Dockerfile + API.md.
2. **catalog/**: Lo que vendemos activamente. Tiene precio, plan, y descripción comercial.
3. **concepts/**: Ideas, experimentos, proyectos del pasado. Sin soporte activo.

## Servicios en producción

| Servicio | Puerto | Docker | API |
|----------|--------|--------|-----|
| Mystik AI | :5200 | ✅ | ✅ |
| Content Studio | :8765 | ✅ | ✅ |
| OmniVoice | :3900 | ✅ | ✅ |
| ABE Music OS | :5180 | ✅ | ✅ |

## Catálogo de ventas

| Producto | Precio mínimo | Plan |
|----------|--------------|------|
| Mystik AI | $0/mes | Starter |
| Content Studio | $49/mes | Pro |
| OmniVoice | $49/mes | Pro |
| Open Notebook | $199/mes | Enterprise |
| ABE Music OS | $199/mes | Enterprise |
