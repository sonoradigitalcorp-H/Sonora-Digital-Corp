# Harvis OS — Instrucciones para Agentes de IA

## Contexto

Harvis OS es un **sistema operativo para agentes de IA**. No es un chatbot. No es un workflow. Es un OS para trabajadores digitales.

El objetivo es eliminar al humano como cuello de botella, proporcionando un sistema que orqueste agentes automáticamente.

## Metodología

Seguimos **Spec-Driven Development (SDD)** de Joaquín Ruiz.

Referencia: Del Vibe Coding al Spec-Driven Development

## Reglas

### 1. NO implementar sin spec aprobada

Cada componente debe tener una especificación antes de escribir código.

Ubicación de specs: `specs/XXX-nombre/spec.md`

### 2. NO crear componentes duplicados

Antes de crear un componente, verificar que no exista uno que haga lo mismo.

Componentes existentes:
- `001-harvis-core` — Kernel del sistema
- `002-dispatcher` — Punto único de entrada
- `003-planner` — Planificación de tareas
- `004-agent-registry` — Catálogo de agentes
- `005-event-bus` — Comunicación asíncrona

### 3. SIEMPRE pasar Constitution Check

Antes de CADA implementación, verificar los 5 principios:

```markdown
## Constitution Check

### Principio I: Orquestación Única
- [ ] ¿Entra por Dispatcher?
- [ ] ¿No hay comunicación directa entre agentes?

### Principio II: Separación Determinista vs LLM
- [ ] ¿La lógica crítica es determinista?
- [ ] ¿El LLM solo se usa cuando es necesario?

### Principio III: Local-first
- [ ] ¿Los datos permanecen locales?
- [ ] ¿Se prioriza LLM local?

### Principio IV: Testing
- [ ] ¿Hay tests para esta funcionalidad?
- [ ] ¿Los tests cubren casos límite?

### Principio V: Trazabilidad
- [ ] ¿Cada decisión se registra?
- [ ] ¿Se puede auditar el flujo?
```

### 4. SIEMPRE escribir tests antes de código

Seguir TDD: test → implement → refactor.

### 5. SIEMPRE documentar decisiones técnicas

Cada decisión debe documentarse con razón y alternativas consideradas.

## Estructura del Proyecto

```
harvis-os/
├── .specify/
│   ├── memory/
│   │   └── constitution.md      # Constitución del proyecto
│   ├── templates/
│   │   ├── spec.md              # Plantilla para specs
│   │   ├── plan.md              # Plantilla para planes
│   │   └── tasks.md             # Plantilla para tareas
│   └── workflows/
│       └── sdd.md               # Flujo de trabajo SDD
├── specs/
│   ├── 001-harvis-core/
│   │   ├── spec.md
│   │   ├── plan.md
│   │   └── tasks.md
│   ├── 002-dispatcher/
│   ├── 003-planner/
│   ├── 004-agent-registry/
│   └── 005-event-bus/
├── src/
│   ├── core/                    # Harvis Core
│   ├── dispatcher/              # Dispatcher
│   ├── planner/                 # Planner
│   ├── registry/                # Agent Registry
│   ├── events/                  # Event Bus
│   ├── agents/                  # Wrappers de agentes
│   │   ├── openhands.py
│   │   ├── opencode.py
│   │   ├── hermes.py
│   │   └── aider.py
│   ├── adapters/                # Adapters de entrada
│   │   ├── telegram.py
│   │   ├── web.py
│   │   └── cli.py
│   └── memory/                  # Sistema de memoria
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── config/
│   ├── settings.py
│   ├── routing_rules.yaml
│   └── agents.yaml
├── CLAUDE.md                    # Este archivo
└── README.md
```

## Flujo de Trabajo

```
1. Discovery
   ├─ Entender el problema
   ├─ Identificar servicios existentes
   └─ Definir alcance

2. Constitution Check
   ├─ Verificar Principio I
   ├─ Verificar Principio II
   ├─ Verificar Principio III
   ├─ Verificar Principio IV
   └─ Verificar Principio V

3. Spec
   ├─ Definir inputs/outputs
   ├─ Definir contrato
   ├─ Definir testing
   └─ Documentar decisión

4. Plan
   ├─ Dividir en fases
   ├─ Estimar tareas
   ├─ Identificar dependencias
   └─ Definir criterios de éxito

5. Tasks
   ├─ Desglosar tareas
   ├─ Priorizar (P0, P1, P2)
   ├─ Asignar estimaciones
   └─ Definir subtareas

6. Implement
   ├─ Escribir tests primero (TDD)
   ├─ Implementar código
   ├─ Verificar tests
   └─ Documentar cambios

7. Validate
   ├─ Constitution Check final
   ├─ Revisión de código
   ├─ Verificar métricas
   └─ Actualizar documentación

8. Release
   ├─ Tag de versión
   ├─ Changelog
   ├─ Deploy
   └─ Monitoreo
```

## Stack Tecnológico

### Core
- Python 3.11+
- FastAPI
- Pydantic
- structlog

### Almacenamiento
- PostgreSQL (estado)
- Redis (cache, colas, eventos)
- Qdrant (vectores)
- Neo4j (relaciones)

### Agentes
- OpenHands (código, deploy)
- OpenCode (IDE)
- Hermes (MCP)
- Aider (Git)

### Comunicación
- Redis Streams (Event Bus)
- HTTP (APIs internas)

### Observabilidad
- OpenTelemetry
- Prometheus
- Grafana

## Comandos Útiles

```bash
# Ejecutar tests
pytest tests/

# Ejecutar tests con cobertura
pytest tests/ --cov=src --cov-report=term-missing

# Ejecutar linter
ruff check src/ tests/

# Ejecutar formatter
ruff format src/ tests/

# Ejecutar type check
mypy src/

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## Decisiones Arquitectónicas

### Por qué Dispatcher en vez de directo a agentes
- Elimina al humano como cuello de botella
- Permite routing automático
- Facilita tracking de tareas

### Por qué reglas deterministas en vez de LLM
- Los LLMs son no deterministas
- Las reglas son auditables
- El LLM solo se usa como fallback

### Por qué Redis Streams en vez de RabbitMQ
- Ya tenemos Redis
- Redis Streams es más simple
- Consumer groups resuelven el problema

### Por qué wrappers en vez de modificar agentes
- Los agentes existentes ya funcionan
- No queremos dependencias directas
- Los wrappers facilitan testing

## Contacto

- **Proyecto**: Harvis OS
- **Organización**: Sonora Digital Corp
- **Autor**: Luis Daniel Guerrero Enciso

## Licencia

Por definir
