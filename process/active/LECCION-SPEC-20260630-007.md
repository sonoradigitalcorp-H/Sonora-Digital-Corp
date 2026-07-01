# Lección — SPEC-20260630-007: Native Agent OS

| Campo | Valor |
|-------|-------|
| **Spec** | `SPEC-20260630-007` |
| **Tier** | 2 |
| **Fecha** | 2026-07-01 |

---

## ¿Qué pasó?

Se reemplazaron las 4 capas de routing (nginx → FastAPI → AgentOrchestrator → MCP) por un MCP Gateway único con auth JWT RS256, CapabilityRegistry runtime, ADK declarativo, Multi-Provider routing (7 modelos), Skill Marketplace unificado (128 skills), y Dashboard visual. En total 2,077 líneas de JS en 15 archivos, 44 tools MCP, 6 archivos nginx simplificados.

---

## ¿Qué salió bien?

- ✅ CapabilityRegistry funciona mejor que el keyword matching — resuelve capabilities con semántica en vez de if/elif
- ✅ ADK YAML mucho más fácil de leer que clases Python hardcodeadas — se creó sales-agent y research-agent en minutos
- ✅ Multi-Provider routing por capability permite elegir modelo óptimo (Gemini para research, GPT-4 para sales, DeepSeek para código)
- ✅ Skill Marketplace unificó 128 skills de 4 silos en 1 CLI command (`sdc skill list`)
- ✅ El dashboard en HTML plano (sin frameworks) carga en <200ms y muestra todo en vivo
- ✅ nginx se simplificó de 15 location blocks a 1 solo proxy_pass

---

## ¿Qué salió mal?

- ❌ El CapabilityRegistry no tiene embeddings reales — usa keyword matching básico en vez de Qdrant. Funciona pero no es semántico real
- ❌ Provider Router no está conectado al FinOps existente — los costs se trackean pero no se asignan por capability
- ❌ El Docker sandbox (docker-runner.js) no se pudo testear completamente — necesita Docker runtime
- ❌ SkillRegistry usa filesystem, no DB — no persiste cambios entre sesiones

---

## ¿Qué haríamos diferente?

- Conectar CapabilityRegistry a Qdrant para embeddings reales (ya hay Qdrant en Docker)
- Integrar Provider Router con el FinOps existente (`finops.jsonl`)
- Persistir SkillRegistry en SQLite en vez de JSON filesystem
- Agregar tests unitarios para los módulos JS (solo tenemos integration tests)
- Hacer el dashboard en tiempo real con SSE en vez de refresh manual

---

## Engram Tags

native-agent-os, mcp-gateway, auth, jwt, capability-registry, adk, multi-provider, skill-marketplace, dashboard, migration, infra, architecture
