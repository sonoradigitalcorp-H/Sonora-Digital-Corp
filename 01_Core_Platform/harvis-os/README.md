# Harvis OS

**Sistema Operativo para Agentes de IA**

No es un chatbot. No es un workflow. Es un OS para trabajadores digitales.

## Objetivo

Eliminar al humano como cuello de botella, proporcionando un sistema que orqueste agentes automáticamente.

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    ENTRADA ÚNICA                        │
│         Telegram / Web CLI / API REST                   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   HARVIS DISPATCHER                      │
│         Clasifica → Prioriza → Asigna                   │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼───────┐
│   PLANNER    │ │  MEMORY   │ │   QA AGENT   │
│ Divide tareas│ │ Contexto  │ │  Valida      │
└───────┬──────┘ └───────────┘ └──────────────┘
        │
┌───────▼─────────────────────────────────────────────────┐
│                 AGENT POOL                               │
├─────────────┬─────────────┬─────────────┬───────────────┤
│  OpenHands  │  OpenCode   │   Hermes    │    Aider      │
│  (código)   │  (IDE)      │  (MCP)      │   (Git)       │
└─────────────┴─────────────┴─────────────┴───────────────┘
        │
┌───────▼─────────────────────────────────────────────────┐
│              INFRAESTRUCTURA COMPARTIDA                  │
├─────────────┬─────────────┬─────────────┬───────────────┤
│  PostgreSQL │   Qdrant    │    Redis    │    Neo4j      │
│  (estado)   │ (vectores)  │  (cache)    │ (relaciones)  │
└─────────────┴─────────────┴─────────────┴───────────────┘
```

## Componentes

| Componente | Responsabilidad | Estado |
|------------|-----------------|--------|
| Harvis Core | Kernel del sistema | Spec definida |
| Dispatcher | Punto único de entrada | Spec definida |
| Planner | Planificación de tareas | Spec definida |
| Agent Registry | Catálogo de agentes | Spec definida |
| Event Bus | Comunicación asíncrona | Spec definida |

## Metodología

Seguimos **Spec-Driven Development (SDD)** de Joaquín Ruiz.

### Principios

1. **Orquestación Única** — Todo entra por Dispatcher
2. **Separación Determinista vs LLM** — Routing determinista, LLM como fallback
3. **Local-first** — Datos locales, LLM local prioridad
4. **Testing Obligatorio** — Sin tests no hay implementación
5. **Trazabilidad Total** — Cada decisión es auditable

## Stack

- Python 3.11+
- FastAPI
- Redis (Streams)
- PostgreSQL
- Qdrant
- Neo4j
- OpenHands
- OpenCode
- Hermes
- Aider

## Inicio Rápido

```bash
# Clonar repositorio
git clone https://github.com/sonora-digital-corp/harvis-os.git
cd harvis-os

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests
pytest tests/

# Iniciar servicios
docker-compose up -d
```

## Documentación

- [Constitución](.specify/memory/constitution.md)
- [Workflow SDD](.specify/workflows/sdd.md)
- [Specs](specs/)

## Licencia

Por definir

## Autor

- **Luis Daniel Guerrero Enciso** — Sonora Digital Corp
