# AGENCY OS v4.0 — Manifesto del Sistema de Prompts
## JARVIS → AI Agency · 14 Jun 2026 (v4.0: Turbo)

```
  AGENCY OS v4.0
  ├── _META/       ★ Prompts que crean prompts (núcleo evolutivo)
  ├── IDENTITY/    ★ Quién eres, principios, constitution
  ├── AGENTS/      ★ Prompts por tipo de agente
  ├── STRATEGY/    ★ El negocio: pricing, clientes, pipeline, escalamiento
  ├── OPERATIONS/  ★ El día a día: schedules, rutinas, daemon, gateway
  ├── CONTENT/     ★ Producción: landings, dashboards, reportes, marketing, diseño
  ├── CODE/        ★ Cómo escribes código: TDD, harness, tests
  ├── CLIENTS/     ★ Clientes específicos: ABE, multi-cliente
  └── TOOLS/       ★ Herramientas externas: GitHub, MCP, OpenDesign
```

### Filosofía
1. **Entregar > Construir**. Cada hora sin entregable visible al cliente es una hora perdida.
2. **Auto-mejora cada 10 min**. Turbo-loop corrige errores y mejora prompts continuamente.
3. **Daemon 24/7**. El sistema nunca duerme. Monitorea, repara, reporta, entrega.
4. **Sin VPS**. Tu laptop es el servidor. 3.2GB RAM alcanza para 5 clientes.
5. **Sin frameworks**. HTML plano + CSS puro + fetch() a API viva.

### El Ciclo (v4.0)
```
CADA 10 MIN: Turbo-loop → healthcheck → auto-fix → log
CADA 6 HORAS: Push reporte ABE → Telegram
CADA 24 HORAS: Tests → commit → push → GitHub
CADA SEMANA: Meta-evolve (domingo) → mejora prompts
```

### Chain de Decisión
```
TÚ (hablas/escribes)
  → IDENTITY/core.md filtra por principios y voz
    → TOOLS/ selecciona herramienta (GitHub, MCP, OpenDesign)
      → STRATEGY/ define el plan (cliente, delivery, scaling)
        → CONTENT/ produce el entregable (dashboard, reporte, landing)
          → OPERATIONS/ ejecuta (daemon, gateway, push)
            → CLIENTS/ verifica entrega (delivery-gate)
              → _META/ auto-optimize (cada 10 min mejora)
```

### Mapa de Herramientas v4.0
| Herramienta | Quién | Cuándo | Por qué |
|-------------|-------|--------|---------|
| Daemon Python | OPERATIONS/abe-daemon.md | 24/7 | Monitorea + repara + reporta |
| Turbo-Loop | _META/auto-optimize-10min.md | Cada 10 min | Auto-mejora continua |
| Gitingest | TOOLS/gitingest.md | Investigar repos | Leer código sin clonar |
| GitHub CLI | TOOLS/github-search.md | Buscar + gestionar | Encontrar soluciones existentes |
| OpenDesign | TOOLS/open-design.md | Diseños visuales | 129 design systems listos |
| Telegram Bot | OPERATIONS/gateway-config.md | Push clientes | Canal de entrega principal |
| pytest | AGENTS/executor.md | Cada cambio | 24+ tests ABE pasando |
| Neo4j | AGENTS/memory.md | CRM | Grafos de artistas |
| Fal.ai | AGENTS/creator.md | Imágenes | Generación multimedia |
| OpenRouter | AGENTS/executor.md | LLM API | deepseek-v4-flash |
| systemd | OPERATIONS/abe-daemon.md | Servicios | Daemon + timer 24/7 |
