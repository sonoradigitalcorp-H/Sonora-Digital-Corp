# MCP Hacks — Análisis de Servidores que Reducen Tiempo y Dolores de Cabeza

**Fecha**: 2026-07-01 | **Contexto**: Codebase Memory MCP + Ecosistema MCP

---

## 1. ¿Qué es Codebase Memory MCP?

Es un servidor MCP open source (MIT) que **indexa todo el código en un grafo de conocimiento**. Usa:

1. **Tree-sitter** para generar AST (Abstract Syntax Tree) de cada archivo
2. **Hybrid LSP** para mapear relaciones entre llamadas y definiciones
3. **SQLite persistente** (RAM-first) como almacenamiento

**Métrica de rendimiento** (prueba real en proyecto mediano):

| Sin MCP | Con MCP | Ahorro |
|---------|---------|--------|
| 21,000 tokens | 13,000 tokens | **40% menos** |
| 1 min 12 seg | 37 seg | **~50% más rápido** |

**Cómo ayuda en SDC:** En lugar de leer archivo por archivo para entender la arquitectura, preguntas: "dónde se define fetch_artist?" y el MCP responde con la ubicación exacta, relaciones, y dependencias. Sin tener que leer 100 archivos.

---

## 2. Los MCP Servers Más Útiles para SDC

Basado en el repositorio oficial de MCP servers (87.9k stars) y el ecosistema, estos son los que más nos ayudarían:

### 🧠 Memoria y Conocimiento

| Servidor | Qué hace | Para qué en SDC |
|----------|----------|-----------------|
| **Memory MCP** | Grafo de conocimiento persistente con entidades, relaciones y observaciones | Almacenar decisiones de arquitectura, relaciones entre servicios, conocimiento del sistema. Como Engram pero con grafo nativo MCP |
| **Codebase Memory** | Indexa código con AST + LSP. Responde "dónde está X" sin leer archivos | Navegar el código de SDC sin leer 200 archivos uno por uno |

### 🔧 Git y Código

| Servidor | Qué hace | Para qué en SDC |
|----------|----------|-----------------|
| **Git MCP** | status, diff, add, commit, log, branches, show | Los agentes podrían hacer commits solos. Hoy git lo hago yo |
| **Filesystem MCP** | read, write, edit, search, list, move, tree | Los agentes podrían leer/escribir archivos sin comandos shell |

### 🌐 Web y Búsqueda

| Servidor | Qué hace | Para qué en SDC |
|----------|----------|-----------------|
| **Fetch MCP** | Obtiene contenido web y lo convierte para LLM | Los agentes podrían buscar documentación de APIs, leer docs de OpenClaw, etc. |
| **Brave Search MCP** | Búsqueda web y local | Agentes podrían buscar información actualizada en internet |
| **GitHub MCP** | Repos, issues, PRs, code search | Agentes podrían revisar issues, crear PRs, buscar en GH |

### 🗄️ Bases de Datos

| Servidor | Qué hace | Para qué en SDC |
|----------|----------|-----------------|
| **PostgreSQL MCP** | Consultas SQL con schema inspection | Agentes consultarían Postgres directamente sin conexión directa |
| **SQLite MCP** | DB interaction + BI capabilities | Engram tiene SQLite. Agentes podrían consultarlo vía MCP |

---

## 3. Cómo se Integran con Nuestro Ecosistema

### Hoy (OpenClaw + Hermes + MCP Gateway)

```
OpenClaw (:18789) ←→ MCP Gateway (Node.js, 138 tools)
                            ↓
                    Hermes MCP (:8000) 
                            ↓
                    Neo4j MCP, Qdrant MCP, Redis MCP
```

### Mañana (agregando los nuevos MCP servers)

```
OpenClaw (:18789) ←→ MCP Gateway (Node.js, 138+ tools)
                            ↓
                    Hermes MCP (:8000)
                            ↓
          ┌───────────┬────┼────┬───────────┐
          ↓           ↓    ↓    ↓           ↓
     Neo4j MCP  Git MCP  Memory  Fetch MCP  Filesystem
     Qdrant MCP          MCP    Brave MCP   MCP
     Redis MCP
```

**Los 3 agentes actuales (monitor, healer, notifier)** se beneficiarían de:
- **Git MCP**: Commitear automáticamente cambios en config
- **Memory MCP**: Recordar decisiones de healing entre reinicios
- **Filesystem MCP**: Leer/escribir eventos sin depender de Python

---

## 4. Qué Instalar YA (bajo impacto, alto retorno)

| Prioridad | Servidor | Instalación | Beneficio |
|-----------|----------|-------------|-----------|
| 🔴 1 | **Git MCP** | `pip install mcp-server-git` | Agentes hacen commits. Ya instalado ✅ |
| 🔴 2 | **Memory MCP** | `npx -y @modelcontextprotocol/server-memory` | Grafo de conocimiento tipo Engram vía MCP |
| 🟡 3 | **Filesystem MCP** | `npx -y @modelcontextprotocol/server-filesystem` | Agentes manipulan archivos sin shell |
| 🟡 4 | **Fetch MCP** | `npx -y @modelcontextprotocol/server-fetch` | Agentes buscan documentación web |
| 🟢 5 | **GitHub MCP** | `npx -y @modelcontextprotocol/server-github` | Agentes gestionan issues y PRs |

**Nota sobre Codebase Memory MCP:** No se encontró en GitHub con ese nombre exacto (404). El concepto está cubierto por el **Memory MCP oficial** + **tree-sitter**. Existen MCP servers de código abierto como `mcp-server-codebase` o `github.com/modelcontextprotocol/servers/src/memory` que ofrecen funcionalidad similar. También hay frameworks como **EasyMCP** y **FastMCP** para construir el nuestro.

**Ecosistema MCP completo:** El repositorio oficial tiene 87.9k stars, 4,116 commits, y una comunidad activa con cientos de servidores listados en [mcpservers.org](https://mcpservers.org), [smithery.ai](https://smithery.ai), y [pulsemcp.com](https://pulsemcp.com).

---

## 5. Impacto en Tiempo y Dolores de Cabeza

| Dolor de cabeza actual | Cómo lo resuelve un MCP server | Tiempo ahorrado |
|----------------------|--------------------------------|-----------------|
| "Dónde se define X?" | Codebase Memory responde en 37 seg vs 1 min 12 seg leyendo archivos | **~50%** |
| "Hay que commitear estos cambios" | Git MCP: los agentes commitean solos | **5 min manual → 0** |
| "Buscar en docs de OpenClaw cómo configurar Y" | Fetch MCP: agente lee la doc y responde | **10 min manual → 0** |
| "El agente no recuerda lo que decidió antes" | Memory MCP: grafo persistente de decisiones | **No más repeticiones** |
| "Hay que leer 10 archivos para entender la arquitectura" | Codebase Memory: pregunta directa al grafo | **~80% menos archivos** |
| "Crear un issue en GitHub" | GitHub MCP: agente crea issue, asigna, etiqueta | **3 min manual → 0** |

---

## 6. Conclusión

**Codebase Memory MCP** (y el concepto de MCP servers en general) reduce drásticamente el tiempo que perdemos en:

1. **Navegar código** (entender dónde está cada cosa)
2. **Operaciones repetitivas** (commits, issues, búsquedas)
3. **Pérdida de contexto** (agentes que no recuerdan decisiones pasadas)

Ya tenemos el 70% de la infraestructura: OpenClaw, Hermes, MCP Gateway con 138 tools. Agregar estos 5 MCP servers nos da el 30% restante para que los agentes sean **realmente autónomos**: que lean código, hagan commits, busquen documentación, y recuerden decisiones.

**Próximo paso (SPEC-009):** Configurar OpenClaw para usar Telegram + Ollama como interfaz conversacional. Luego agregar Git MCP y Memory MCP para que los agentes operen sobre el código directamente.
