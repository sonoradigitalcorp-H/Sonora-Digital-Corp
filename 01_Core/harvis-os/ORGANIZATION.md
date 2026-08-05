# ORGANIZATION.md — Sonora Digital Corp & Harvis OS

> **Propósito:** Definir WHO hace QUÉ. Eliminar la dependencia del humano como cuello de botella.
> Cada sistema/agente tiene misión, autoridad, responsabilidades y límites claros.

---

## CEO — Luis Daniel (Humano)

**Misión:** Decidir. No ejecutar.
**Autoridad:** Total (principal/única fuente de decisiones).
**Responsabilidades:**
- Definir rumbo y prioridades
- Aprobar specs y releases
- Resolver conflictos entre sistemas
- Revisar reportes de los agentes

---

## Sistema 1 — Harvis OS (Orquestador)

**Rol:** Sistema Operativo para Agentes. Municipio central.
**Misión:** Orquestar, planificar, enrutar y ejecutar tareas a través de agentes.
**Puerto:** 8000 — `GET /health`

### Responsabilidades
- **Dispatcher** — punto único de entrada de tareas → routing automático
- **Planner** — descomposición de tareas en pasos
- **Agent Registry** — catálogo de agentes disponibles
- **Event Bus** — comunicación asíncrona (Redis Streams)
- **Memory** — contexto, vectores (FastEmbed local), grafo
- **Voice Control** — interpretación de comandos por voz (OpenRouter)

### Límites
- NO despliega directamente a clientes
- NO es el VPS de producción
- Depende de infraestructura base (Docker, Redis, PostgreSQL)

---

## Sistema 2 — Cowork / OpenClaw (Operaciones)

**Rol:** Operador de 24/7. Vigilante y trabajador diario.
**Misión:** Monitorear, backup, aprendery mantener el sistema vivo.
**Puerto:** OpenClaw gateway 18789

### Agentes
- **CEO Agent (`main`)** — operaciones diarias, seguridad, monitoreo, deploy
- **RYE Agent (`rye`)** — RAG, auto-evolución, aprendizaje
- **Auto-Save** — memoria persistente cada 60 min (Neo4j + Qdrant)
- **Close-Loop** — cierre de sesión, resúmenes, ADRs

### Responsabilidades
- Health checks de todos los sistemas (incluido Harvis OS)
- Backups de memoria y estado
- Commits automáticos al final del día
- Captura de lecciones aprendidas

### Límites
- NO escribe código de negocio directamente
- NO toma decisiones de arquitectura

---

## Sistema 3 — Hermes (MCP Tools)

**Rol:** Encargado de herramientas. Brazo de ejecución.
**Misión:** Proveer herramientas MCP a los agentes (LLM, RAG, engram, WhatsApp).
**Conexión:** sdc-mcp-local (MCP server)

### Responsabilidades
- `llm_chat` — chat con OpenRouter
- `rag_search` — búsqueda en Qdrant (FastEmbed local)
- `engram_*` — memoria del tenant
- `whatsapp_*` — mensajería
- `sdc_status` — estado del servidor

### Límites
- Ejecuta herramientas, no decide qué hacer
- Depende de Qdrant y OpenRouter

---

## Sistema 4 — OpenCode (Desarrollo)

**Rol:** Ingeniero de software. Escribe y mantiene código.
**Misión:** Implementar specs, refactorizar, testear.
**Acceso:** Este entorno (TUI)

### Responsabilidades
- Escribir código según specs SDD
- Crear y mantener tests
- Ejecutar lint/typecheck
- Documentar (CLAUDE.md, README)

### Límites
- NO decide arquitectura sin spec aprobada
- NO hace deploy a producción sin aprobación

---

## Flujo de Decisiones

```
¿Tarea = escribir código?    → OpenCode
¿Tarea = orquestar agentes?  → Harvis OS (Dispatcher)
¿Tarea = monitorear/backup?  → Cowork (OpenClaw)
¿Tarea = usar una herramienta externa? → Hermes (MCP)
¿Tarea = decidir rumbo?      → CEO (Humano)
```

---

## Split de Modelos (LLM)

| Uso | Proveedor | Modelo | Costo |
|-----|-----------|--------|-------|
| Interpretar comandos (primary) | OpenRouter | `deepseek/deepseek-v4-flash` | $0.00000028/token |
| Interpretar comandos (fallback) | OpenRouter | `nemotron-3-nano:free` | $0 (gratis) |
| Embeddings | **LOCAL** | `FastEmbed (bge-small-en-v1.5)` | $0 (local) |

**Regla de oro:** Embeddings SIEMPRE locales (FastEmbed). LLM puede ser remoto (OpenRouter).

---

## Monitoreo & Auto-Restart

```bash
# Iniciar todo
bash harvis-os/scripts/start-auto.sh

# Health check + auto-restart (cron cada 5 min)
*/5 * * * * /path/to/harvis-os/scripts/health-check.sh
```

Los scripts están en `harvis-os/scripts/`.

---

## Prioridad actual (próximos 30 días)

1. Mantener sistemas vivos (start-auto + health-check ya creados)
2. Agregar créditos a OpenRouter para usar DeepSeek V4 Flash
3. Conectar Cowork CEO para health check de Harvis OS
4. Documentar cada decisión en ADR