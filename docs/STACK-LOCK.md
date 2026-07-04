# Stack Lock v1

**Política**: PRINCIPLE-010 (`truth/10-principles.yaml`)
**Vigencia**: 2026-07-04 hasta nuevo aviso
**Regla fundamental**: Ninguna herramienta nueva entra al stack sin razón objetiva post-MVP.

## Stack aprobado

### Frontend
- **Vercel** — hosting y deploy
- **Next.js** — framework React
- **React** — UI library
- **TypeScript** — lenguaje
- **Tailwind CSS** — estilos
- **shadcn/ui** — componentes

### Backend
- **FastAPI** — API framework (Python)
- **PostgreSQL** — base de datos relacional
- **Redis** — caché y colas
- **Qdrant** — búsqueda vectorial
- **Neo4j** — grafo de conocimiento

### AI
- **Mystic Engine** — Cognitive Kernel (truth, memory, agents, planning, economics, learning, evolution)
- **Ollama** — inferencia local 100% (PRINCIPLE-009)
- Modelos: qwen3:4b-64k (principal), deepseek-r1:7b-64k (complejo), llama3.2:3b-64k (tasks)

### Automatización
- **n8n** — workflows visuales
- **GitHub Actions** — CI/CD

### Observabilidad
- **Sentry** — errores
- **OpenTelemetry** — trazas

### Infraestructura
- **Docker** — contenedores
- **Nginx** — reverse proxy
- **GitHub** — código + issues + PRs + Actions

## Stack explícitamente excluido (sin usar)
- Cursor, Lovable, Codex, Gemini — herramientas de desarrollo, no parte del stack productivo
- Apify — no necesario hasta que collectors escalen solos

## Proceso para agregar herramienta
1. Issue en GitHub describiendo: qué necesidad resuelve, alternativas evaluadas, por qué gana
2. Aprobación del dueño del sistema
3. Actualizar este archivo
4. Agregar a PRINCIPLE-011 en adelante
