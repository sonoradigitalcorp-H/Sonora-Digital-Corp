# Feature Specification: Sistema Unificado JARVIS + Hermes + OpenClaw

**Feature**: 007-sistema-unificado
**Status**: Active
**Input**: Unificar JARVIS, Hermes y OpenClaw en un solo sistema con memoria compartida, canales de comunicación unificados y control humano para decisiones críticas.

---

## Arquitectura del Routing de Agentes

El AgentOrchestrator decide qué agente ejecuta una tarea mediante **matching por palabras clave con límite de palabra** (word-boundary regex). NO usa LLM para decidir — es 100% determinista.

### Flujo de decisión:

```
Tarea del usuario
       │
       ▼
   ┌─────────────────┐
   │  route(task)     │  ← Matching por keywords
   │  Ej: "buscá X"  │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │  Agente elegido  │
   │  → research      │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │  agent.run(task) │  ← Ejecuta con timeout
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │  Resultado       │
   │  + status        │
   │  + execution_time│
   └─────────────────┘
```

### Tabla de routing (9 agentes):

| Agente | Keywords activadoras | Función |
|--------|---------------------|---------|
| **research** | buscar, investigar, search, dónde está, qué es, explícame | Búsqueda en Neo4j + Qdrant + síntesis |
| **code** | escribe, implementa, codifica, arregla, fix, bug, función, analiza | Generación y análisis de código |
| **explore** | explora, navega, listar, find, ls, archivos, carpeta | Exploración de archivos y repo |
| **memory** | recuerda, memoria, contexto, olvida, guardá | Gestión de memoria (Neo4j) |
| **skill** | skill, herramienta, plugin, ejecutá, corré | Ejecución de herramientas MCP |
| **voice** | habla, di, dime, voz, audio | Interfaz de voz (STT/TTS) |
| **review** | revisa, review, valida, testea, probá | Revisión de código y calidad |
| **hermes** | telegram, whatsapp, hermes, n8n, mensaje, notifica, difunde | Comunicación (Telegram, WhatsApp, n8n) |
| **openclaw** | openclaw, gateway, delegá, deriva, agente externo | Gateway a OpenClaw |
| **gbrain** | gbrain, cerebro, sintetiza, think, capturá, grafo | Síntesis con gap analysis |

### Human-in-the-Loop

Ciertas acciones REQUIEREN aprobación humana antes de ejecutarse:

| Acción | Requiere aprobación | ¿Por qué? |
|--------|-------------------|-----------|
| execute_command | ✅ Sí | Puede modificar el sistema |
| docker_deploy | ✅ Sí | Despliega contenedores |
| delete_session | ✅ Sí | Elimina datos |
| purge_memory | ✅ Sí | Destruye recuerdos |
| send_webhook | ✅ Sí | Envía datos a externos |
| modify_system | ✅ Sí | Cambia configuración |
| Búsqueda, chat, código | ❌ No | Rutina, bajo riesgo |

### Capacidades máximas de cada agente

**ResearchAgent**: Busca en Neo4j (grafos) + Qdrant (vectores) simultáneamente. Combina resultados con score de confianza.

**CodeAgent**: 4 modos — analyze (métricas AST), generate (escribe archivos), read (lee contenido), fix_bug (lee → genera fix → escribe → verifica).

**MemoryAgent**: Guarda/recuerda/olvida en Neo4j con fallback a memoria RAM si Neo4j no está disponible.

**ExploreAgent**: Lista archivos, busca código con grep, muestra estructura de árbol.

**ReviewAgent**: Escanea archivos en busca de TODOs, FIXMEs, líneas largas, debug statements. Devuelve issues categorizados con score 1-10.

**SkillAgent**: Ejecuta tools MCP (web_fetch, docker_build, etc.) con catálogo de 10+ skills.

**VoiceAgent**: STT (Whisper) + TTS (edge-tts) + detección de wake word "Hey JARVIS".

**HermesAgent**: Bridge a Hermes API para enviar/recibir mensajes por Telegram y WhatsApp, y disparar workflows en n8n.

**OpenClawAgent**: Bridge a OpenClaw gateway para delegar tareas a agentes especializados.

---

## Alineación con SDD

Esta spec sigue los 5 principios de la Constitución (spec 000):

| Principio | Cumplimiento |
|-----------|-------------|
| I. Separación (determinista vs LLM) | ✅ Routing 100% determinista por keywords. LLM solo genera respuestas. |
| II. Privacidad y Control Local | ✅ Todo corre en localhost. Solo el LLM va a deepseek vía opencode-go. |
| III. Arquitectura Modular | ✅ Cada agente es independiente, reemplazable, con interfaz clara. |
| IV. Calidad y Testing | ✅ 134 tests pasando. Cada agente tiene tests unitarios. |
| V. SDD | ✅ Esta spec documenta el sistema completo. |

---

## User Stories

### US1 — Routing determinista
**Given** un usuario escribe "buscá información sobre Python"
**When** el orquestador ejecuta `route()`
**Then** la tarea se enruta al agente `research`

### US2 — Human-in-the-Loop
**Given** un usuario pide ejecutar `docker compose up`
**When** el orquestador detecta que requiere aprobación
**Then** se crea un ticket de aprobación y se pausa la ejecución

### US3 — Bridge Hermes
**Given** un usuario dice "mandá un mensaje por Telegram"
**When** el orquestador enruta a HermesAgent
**Then** HermesAgent envía el mensaje vía Hermes Gateway

### US4 — Bridge OpenClaw
**Given** un usuario dice "usá OpenClaw para generar una imagen"
**When** el orquestador enruta a OpenClawAgent
**Then** OpenClawAgent delega al gateway en :18789

### US5 — Fallback a research
**Given** un usuario escribe una tarea sin keywords reconocibles
**When** el orquestador ejecuta `route()`
**Then** la tarea se enruta a `research` como fallback default

---

## Functional Requirements

| ID | Descripción | Prioridad |
|----|-------------|-----------|
| FR-001 | El orquestador debe rutear tareas por keywords sin usar LLM | P0 |
| FR-002 | Cada agente debe tener timeout configurable | P0 |
| FR-003 | Acciones críticas deben requerir aprobación humana | P0 |
| FR-004 | El bridge Hermes debe enviar/recibir mensajes multi-canal | P1 |
| FR-005 | El bridge OpenClaw debe delegar tareas al gateway | P1 |
| FR-006 | El sistema debe soportar ejecución paralela de tareas | P2 |
| FR-007 | El contexto de ejecución debe persistirse entre tareas | P2 |

---

## Success Criteria

| ID | Criterio | Medición |
|----|----------|----------|
| SC-001 | Routing 100% determinista — sin LLM en decisión | Verificar que `route()` no llama a `chat_completion()` |
| SC-002 | Timeout de agente detiene ejecución > N segundos | Test con `asyncio.wait_for` timeout |
| SC-003 | Acción bloqueada sin aprobación no se ejecuta | Test de approve/reject |
| SC-004 | Bridge Hermes responde en < 3s | Health check endpoint |
| SC-005 | 9+ agentes registrados en orquestador | `list_agents()` count >= 9 |

---

## Edge Cases

| # | Caso | Respuesta esperada |
|---|------|-------------------|
| EC-01 | Tarea vacía | Retorna error con mensaje "Tarea vacía" |
| EC-02 | Todos los agentes timeout | Retorna error con timeout aggregation |
| EC-03 | Hermes Gateway offline | HermesAgent retorna health: offline, no crash |
| EC-04 | OpenClaw Gateway offline | OpenClawAgent retorna health: offline, no crash |
| EC-05 | Routing ambiguo (match múltiple) | Primer match en orden de definición |
| EC-06 | Tarea extremadamente larga (>10KB) | Truncar a 200 chars para routing |

---

## Commits y versionado

Cada cambio significativo se commiteará con mensaje descriptivo siguiendo conventional commits.
Los PDFs de commit se generan automáticamente desde `git log`.
