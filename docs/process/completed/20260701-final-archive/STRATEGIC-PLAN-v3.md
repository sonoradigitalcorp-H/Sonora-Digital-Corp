# Strategic Plan — Native Agent OS: The Next Level

**Based on**: Industry research (GitHub, HuggingFace, MCP Ecosystem)
**Constitution**: OMEGA v10.0 — Value First, Capability First, Founder Elimination
**Current State**: 112 MCP tools, 128 skills, ADK, Workflow Engine, Multi-Provider, Auth, Running 24/7 on VPS

---

## Part 1: Industry Best-in-Class (Julio 2026)

### What the Top Repos Do That We Don't (Yet)

| Repo | Stars | What They Have | SDC Gap |
|------|-------|----------------|---------|
| **ruflo** (ruvnet) | 62k | 100+ agents, swarms, self-learning, federation, web UI, plugin marketplace | Swarm coordination, self-learning loop, plugin marketplace |
| **n8n** | 195k | Visual workflow builder + MCP, 400+ integrations, AI nodes | Visual workflow editor (we have YAML engine) |
| **gemini-cli** | 106k | Multimodal terminal agent, MCP client | - |
| **ChromeDevTools MCP** | 44.8k | Browser debugging via MCP | Browser debug tools |
| **GitHub MCP** (official) | 31.1k | Full GitHub API via MCP | GitHub integration via MCP |
| **UI-TARS** | 37.4k | Multimodal GUI agent, computer use | Computer control agent |
| **gpt-researcher** | 28k | Deep research agent | Research agent depth |
| **Context7** | 58.4k | Code docs for LLMs | Documentation integration |

### Top 3 Things to ADD

1. **GitHub MCP Server (official)** — 31.1k stars, official from GitHub
2. **n8n** — connect our workflow engine to the visual editor
3. **ChromeDevTools MCP** — browser debugging via agents

### Best Local Models for CPU (HuggingFace Data)

| Model | Size | RAM | Task | Download Rank |
|-------|------|-----|------|---------------|
| Qwen2.5-1.5B-Instruct | 1.5B | ~1GB | Routing, classification | #1 most downloaded |
| Qwen2.5-7B-Instruct | 7B | ~4GB | Analysis, code | #3 most downloaded |
| Qwen3-4B | 4B | ~2.5GB | General, instruction | #4 trending |
| Qwen3-30B-A3B | 30B (active 3B) | ~2GB | Best efficiency | Rising |

**Recommendation**: Replace qwen2.5:1.5b with **Qwen3-4B** (better quality, similar RAM) and add **Qwen3-30B-A3B** for research (MoE, only 3B active params = 2GB RAM).

---

## Part 2: Strategic Plan — 6 Initiatives

### Initiative 1: Plugin Marketplace (Inspired by ruflo)

**Value**: Founder Independence — crear y compartir plugins sin tocar código del gateway
**Effort**: 2-3 days

```yaml
# Un plugin es un paquete que añade tools + capabilities
name: sales-force
version: 1.0.0
tools:
  - sales_capture_lead
  - sales_qualify_lead
capabilities:
  - sales-execution
webhook: https://api.cliente.com/sales-webhook
```

```bash
sdc plugin install sales-force          # instala desde registro
sdc plugin create my-plugin             # scaffold
sdc plugin publish                      # publica en marketplace
sdc plugin list                         # plugins instalados
```

---

### Initiative 2: GitHub MCP Server Integration

**Value**: Automation — agents que manejan PRs, issues, repos directamente
**Effort**: 1 day

```bash
sdc provider add github <token>
# Ahora agents pueden:
# - Crear PRs automáticamente
# - Revisar issues
# - Leer código de cualquier repo
```

**Integration**: Añadir `github-mcp-server` como MCP server externo en el gateway. 31.1k stars, oficial de GitHub.

---

### Initiative 3: Visual Workflow Editor (n8n-style)

**Value**: Founder Independence — crear workflows sin YAML
**Effort**: 3-5 days

**Hoy**: `mcp/workflow/engine.js` con YAML manual
**Target**: Editor visual drag-and-drop + YAML export

```bash
sdc workflow edit lead-to-cash          # abre editor web
sdc workflow export lead-to-cash        # exporta YAML
sdc workflow import file.yaml           # importa YAML
```

**Strategy**: No construir desde cero. Conectar n8n (195k stars, 400+ integrations) como frontend visual de nuestro Workflow Engine.

---

### Initiative 4: Swarm Coordination (ruflo-style)

**Value**: Automation — múltiples agents coordinados automáticamente
**Effort**: 3-4 days

**Hoy**: Workflow Engine secuencial (steps lineales)
**Target**: Swarm con topologías (jerárquica, mesh, broadcast)

```yaml
# workflow-swarm.yaml
name: research-swarm
topology: mesh
agents:
  - web-researcher    # busca en web
  - code-analyzer     # analiza código encontrado
  - summarizer        # sintetiza todo
```

```bash
sdc swarm run research-swarm "investigar agentic AI frameworks"
# Los 3 agents trabajan en paralelo, se pasan resultados
```

---

### Initiative 5: Self-Learning Loop

**Value**: Founder Elimination — el sistema mejora solo con uso
**Effort**: 2-3 days

**Hoy**: Lecciones se guardan en archivos markdown
**Target**: El CapabilityRegistry aprende de qué tasks resuelve bien cada capability

**Mecanismo**:
1. Cada tool call registra: task, capability resuelta, éxito/fallo, duración
2. El registry ajusta confianza basado en histórico
3. Si una capability falla seguido → se degrada, otra toma su lugar

---

### Initiative 6: ADK Agent Marketplace

**Value**: Revenue — vender agentes ADK a clientes de SDC
**Effort**: 2-3 days

**Hoy**: 2 agentes ADK (sales-agent, research-agent)
**Target**: 20+ agentes en marketplace, instalables con 1 comando

```bash
sdc adk search content-generator        # busca en marketplace
sdc adk install content-generator       # instala agente
sdc adk publish my-agent                # publica agente propio
```

---

## Part 3: Roadmap by Value

```
FASE 1 (Semana 1): GitHub MCP + Plugin Marketplace
  ├── GitHub MCP server integration (1 día)
  ├── Plugin system scaffold (2 días)
  └── Tools: sdc plugin install|create|publish|list

FASE 2 (Semana 1-2): Swarm + Self-Learning
  ├── Swarm coordination engine (3 días)
  ├── Self-learning capability registry (2 días)
  └── Tools: sdc swarm run

FASE 3 (Semana 2-3): Visual Editor + Marketplace
  ├── Conectar n8n como visual editor (3 días)
  ├── ADK Agent Marketplace (2 días)
  └── Tools: sdc workflow edit

SEMANA 4: Integración + Testing
  ├── QA de todas las iniciativas
  ├── Documentación
  └── Deploy a VPS
```

---

## Part 4: Score Estimate

| Métrica | Score | Justificación |
|---------|-------|---------------|
| Revenue Impact | 8 | Agent marketplace = producto vendible |
| Scalability | 8 | Swarm escala mejor que workflows lineales |
| Reusability | 9 | Plugins y agents reusables entre clients |
| Automation Impact | 10 | Self-learning + swarm = automation total |
| Knowledge Impact | 7 | Self-learning preserva conocimiento de uso |
| Reliability | 7 | Swarm con failover entre agents |
| Founder Independence | 9 | Plugins sin tocar código del gateway |
| Operational Simplicity | 7 | Visual editor reduce fricción |
| Customer Value | 9 | Clients pueden instalar agents específicos |
| FinOps Efficiency | 6 | Cost tracking por plugin/agent |

**Total estimado: 80/100** → PASA

---

## Part 5: Constitution Alignment

| OMEGA Principle | How This Plan Delivers |
|-----------------|----------------------|
| **Value First** | Cada iniciativa tiene métrica de negocio |
| **Founder Elimination** | Plugins, marketplace, self-learning reducen dependencia |
| **Capability First** | Plugin system = capabilities reusables |
| **Enterprise Nervous System** | Events tracking en cada tool call |
| **FinOps Law** | Cost tracking por capability/plugin |
| **Observability Law** | Dashboard con métricas de uso real |
| **Self Healing** | Self-learning corrige capacidades fallidas |
