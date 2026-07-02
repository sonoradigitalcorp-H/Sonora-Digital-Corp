# OpenClaw + Hermes MCP — Análisis y Uso en SDC

**Fecha**: 2026-07-01 | **VPS**: sdc-prod (149.56.46.173)

---

## 1. Estado Actual en este VPS

### OpenClaw — ✅ ACTIVO

| Propiedad | Valor |
|-----------|-------|
| **Versión** | 2026.6.10 (aa69b12) |
| **Puerto** | 18789 |
| **Proceso** | `openclaw` PID 602539, corriendo desde Jun 25 |
| **Binario** | `/usr/bin/openclaw` → `openclaw.mjs` (Node) |
| **Health** | `{"ok":true,"status":"live"}` |
| **Plugins** | 80+ (ollama, telegram, browser, webhooks, memory, policy, etc.) |
| **Web UI** | http://127.0.0.1:18789/ (Control UI) |

### Hermes MCP — ✅ ACTIVO (Docker)

| Propiedad | Valor |
|-----------|-------|
| **Versión** | Python 3.11 + MCP SDK 1.28.1 |
| **Puerto** | 8000 |
| **Contenedor** | sdc-mcp-server, Up 25h (healthy) |
| **Protocolo** | SSE (Server-Sent Events) en `/sse` — NO REST |
| **Tools** | gateway_tools(), gateway_call(), jarvis_research(), health_status(), etc. |

### MCP Gateway (Node.js) — ✅ INSTALADO

| Propiedad | Valor |
|-----------|-------|
| **Tipo** | HTTP Server con autenticación JWT RS256 |
| **Skills** | 4 silos unificados (Telegram 98 + Enterprise 10 + opencode 9 + custom) |
| **Total tools** | ~138 |

---

## 2. ¿Qué hace cada uno?

### OpenClaw — Gateway de Canales para Agentes

Es un **multi-channel gateway**. Su propósito principal es:

1. **Recibir mensajes desde canales**: Telegram, WhatsApp, Signal, Discord, iMessage, etc.
2. **Enrutar a un agente AI**: el mensaje llega al Gateway, OpenClaw lo procesa con un LLM local o remoto, y responde.
3. **Extender via plugins**: 80+ plugins para LLMs (ollama, openai, anthropic), memoria, búsqueda web, voz, etc.

**Para qué SIRVE en SDC:**
- Luis Daniel puede chatear con el sistema desde Telegram y recibir respuestas de los agentes
- Los agentes pueden enviar notificaciones a Telegram, WhatsApp o cualquier canal
- El plugin `ollama` conecta directamente a nuestros modelos locales
- El plugin `policy` permite poner reglas de gobernanza

**Para qué NO SIRVE:**
- No es un orquestador de tareas internas (no ejecuta docker restart)
- No es un scheduler (no corre cosas cada 2 minutos)
- Es una interfaz de conversación, no un sistema de automation

### Hermes MCP — Bridge de Tools

Es un **servidor MCP** (Model Context Protocol) que expone herramientas como tools MCP:

1. **gateway_tools()**: lista las 138 tools disponibles en el ecosistema
2. **gateway_call()**: ejecuta cualquier tool del gateway
3. **jarvis_research()**: investigación via JARVIS
4. **health_status()**: health del sistema

**Para qué SIRVE en SDC:**
- Cualquier agente MCP-compatible puede llamar tools de Neo4j, Qdrant, Redis, etc.
- Los agentes JARVIS pueden usar Hermes como puente al MCP Gateway
- Es el "directorio telefónico" de herramientas del sistema

**Para qué NO SIRVE:**
- No ejecuta lógica de decisión (eso es trabajo del agente)
- No mantiene estado entre llamadas

---

## 3. ¿Cómo se relacionan?

```
                    ┌──────────────────────────────┐
                    │     OPENCLAW (:18789)         │
                    │  Gateway de Conversación      │
                    │  80+ plugins                  │
                    │  Telegram, WhatsApp, Web UI   │
                    └──────────┬───────────────────┘
                               │
                    ┌──────────▼───────────────────┐
                    │     MCP GATEWAY (Node.js)     │
                    │  138 tools, JWT auth          │
                    │  4 skill silos unified        │
                    └──────────┬───────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
  ┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
  │  HERMES MCP   │   │  Neo4j MCP    │   │  Qdrant MCP   │
  │  (:8000)      │   │  (graph)      │   │  (vectors)    │
  │  Tool Bridge  │   │               │   │               │
  └───────────────┘   └───────────────┘   └───────────────┘

  ┌────────────────────────────────────────────────────────┐
  │             MIS 3 AGENTES (NUEVOS)                     │
  │  agent-monitor → Redis Stream → agent-healer → agent-notifier │
  │  (NO usan OpenClaw ni Hermes — son independientes)     │
  └────────────────────────────────────────────────────────┘
```

**Los 3 agentes que construí hoy NO pasan por OpenClaw ni Hermes.** Usan Redis Stream directo. Es más rápido y simple para automation interna. Pero si quisieras que los agentes **hablen contigo por Telegram**, ahí entra OpenClaw — él ya tiene el plugin de Telegram configurado.

---

## 4. Casos de Uso Reales para SDC

### Caso 1: Luis Daniel consulta el sistema desde Telegram → USAR OPENCLAW

```
Luis Daniel: "¿Cómo está Neo4j?"
  → Telegram → OpenClaw (plugin ollama) → consulta health
  → OpenClaw responde: "Neo4j está bien, 33 nodos, 19 relaciones"
```

**Valor**: No necesitas abrir el dashboard. Preguntas desde el celular.

### Caso 2: Agentes existentes usan herramientas del sistema → USAR HERMES

```
AgenteHealer necesita consultar Neo4j:
  → Hermes.gateway_call("neo4j_query", "{cypher:...}")
  → Recibe resultado sin conexión directa a Neo4j
```

**Valor**: Los agentes no necesitan saber dónde está cada base de datos. Hermes es el intermediario.

### Caso 3: OpenClaw como orquestador visual → USAR OPENCLAW CONTROL UI

```
http://127.0.0.1:18789/ → Web UI de OpenClaw
  → Ver sesiones activas
  → Chatear con agentes
  → Configurar plugins
```

**Valor**: Interfaz visual para administrar agentes sin terminal.

### Caso 4: Notificaciones multi-canal → USAR OPENCLAW + WEBHOOKS

```
Container crítico → mi agente notifier → webhook → OpenClaw
  → OpenClaw envía a Telegram + WhatsApp + Slack
```

**Valor**: Una sola notificación llega a todos lados.

---

## 5. Lo que NO se está usando aún

| Recurso | Estado | Por qué no se usa |
|---------|--------|-------------------|
| OpenClaw plugin `ollama` | ✅ Instalado | Los agentes JARVIS ahora llaman a Ollama directo (ask_local). OpenClaw podría ser intermediario pero añade latencia. |
| OpenClaw plugin `telegram` | ✅ Instalado | Mi notifier_agent.py envía Telegram directo via API. OpenClaw podría hacerlo pero es más pesado. |
| Hermes `gateway_call()` | ✅ Disponible | Los agentes nuevos conectan directo a Redis y Neo4j. No necesitan al gateway. |
| MCP Gateway (18989) | ⚠️ Puerto no expuesto | El gateway de 138 tools existe pero no está siendo consultado por nadie. |
| OpenClaw `policy` plugin | ✅ Instalado | Podría gobernar qué agentes pueden hacer qué, pero no hay políticas definidas. |

---

## 6. Conclusión

**OpenClaw y Hermes están instalados y funcionando en este VPS.** No los hemos integrado porque:

1. **Los 3 agentes nuevos (monitor, healer, notifier)** son más eficientes usando Redis Stream directo. OpenClaw añadiría latencia y complejidad innecesaria.
2. **OpenClaw brilla como interfaz conversacional** — para que le preguntes al sistema "cómo está Neo4j?" desde Telegram. Eso no lo hemos configurado aún.
3. **Hermes brilla como intermediario de tools** — para que agentes existentes (los 17 de JARVIS) llamen herramientas sin saber dónde están. Eso tampoco lo hemos activado.

**Lo que sigue:** Decidir si queremos integrarlos o mantener los agentes independientes. Si privilegias velocidad y simplicidad → los 3 agentes actuales son mejores. Si privilegias tener TODO centralizado en un solo ecosistema → hay que migrar los agentes a OpenClaw + Hermes.
