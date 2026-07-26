---
title: Mystic OS Architecture
date: 2026-07-25
status: draft
author: SDC Architecture Team
version: 1.0.0
---

# Mystic OS — Arquitectura General

## Visión

Mystic OS es un **sistema operativo multi-tenant para PYMEs**. No es un chatbot ni un asistente conversacional — es una plataforma completa donde cada cliente opera su propio "mundo" digital con dashboard, memoria, agentes y herramientas.

Cada tenant tiene:

- Un **dashboard vivo** con métricas en tiempo real
- Un **sistema de memoria** aislado (short-term + long-term + semántico)
- **Agentes configurables** que ejecutan tareas según políticas del tenant
- **Herramientas registradas** con permisos específicos

## Arquitectura General

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Cliente   │────▶│   Gateway   │────▶│    Core     │
│  (Frontend) │     │  (FastAPI)  │     │  (Session)  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                        ┌──────▼──────┐
                                        │   Planner   │
                                        │  (Router)   │
                                        └──┬──────┬───┘
                                           │      │
                                  ┌────────▼┐  ┌─▼──────────┐
                                  │  Tools   │  │   Memory   │
                                  │ Registry │  │   Engine   │
                                  └──────────┘  └────────────┘
                                               │
                                        ┌──────▼──────┐
                                        │     LLM     │
                                        │  (OpenAI /  │
                                        │   Local)    │
                                        └─────────────┘
```

### Flujo de una solicitud

1. **Gateway** recibe la request, valida tenant y session
2. **Core** asigna session_id, user_id, tenant_id
3. **Planner** decide: ¿tool call? ¿memory recall? ¿chat directo?
4. **Memory Engine** recupera contexto relevante
5. **Tools** se ejecutan si el planner lo decide
6. **LLM** genera respuesta con el contexto completo
7. **Respuesta** se envía al frontend + se persiste en memoria

## Stack Tecnológico

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| Backend | Python 3.11+ / FastAPI | API REST + WebSocket |
| Frontend | Three.js + TypeScript | Cosmic UI 3D |
| Base de datos | PostgreSQL | Datos persistentes por tenant |
| Memoria semántica | Qdrant | Embeddings y búsqueda vectorial |
| Cache / Sesiones | Redis | Session store, rate limiting |
| Cola de tareas | Redis + RQ | Tareas asíncronas |
| Contenedores | Docker + Compose | Despliegue unificado |
| LLM | OpenAI / OpenRouter / Local | Inferencia de lenguaje |

## Principios de Diseño

- **Multi-tenant nativo**: cada tenant tiene datos, memoria y agentes aislados
- **Offline-first**: el frontend funciona con datos cacheados
- **Memory-first**: toda interacción se persiste automáticamente
- **Tool-safe**: las herramientas nunca se ejecutan directamente desde el LLM
- **Mobile-first**: UI responsive con prioridad iPhone/Android
