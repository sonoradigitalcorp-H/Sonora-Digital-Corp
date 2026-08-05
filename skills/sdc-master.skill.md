# SDC Master Skill — Sonora Digital Corp

## Overview

Master skill for Sonora Digital Corp development. Encapsulates all patterns, lessons, and strategies from the last month of development.

## When to Use

- Starting any new feature or component
- Debugging issues
- Setting up new environments
- Reviewing code
- Planning sprints

## Core Principles

### 1. Constitution Check (MANDATORY)

Before EVERY implementation, verify:

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

### 2. SDD Lifecycle

Follow Spec-Driven Development:

1. **Revenue Gate** — Does this generate value?
2. **Discovery** — Understand the problem
3. **Spec** — Define inputs/outputs/contract
4. **BDD/ATDD** — Write scenarios first
5. **ADR** — Document decisions
6. **Plan** — Break into phases
7. **Tasks** — Break into small tasks
8. **Code** — TDD: test → implement → refactor
9. **Verify** — Run tests, check constitution
10. **Delivery** — Deploy and monitor
11. **Archive** — Document lessons learned

### 3. Architecture Rules

- **Golden Rule**: Core NEVER mixes with clients
- **Layer Separation**: kernel/ → infra/ → apps/ → products/ → clients/
- **Agent Wrappers**: Never modify agents directly, use wrappers
- **Event-Driven**: Use Redis Streams for async communication
- **Local-First**: Prefer Ollama over external APIs

## Common Patterns

### Pattern: New Feature

```bash
# 1. Pre-flight
make doctor-quick

# 2. Create spec
mkdir -p process/active/SPEC-$(date +%Y%m%d)-FEATURE-NAME
# Write spec.md, plan.md, tasks.md

# 3. Write tests first
# tests/unit/test_feature.py

# 4. Implement
# src/feature.py

# 5. Verify
make test
make lint

# 6. Commit
git add . && git commit -m "feat: FEATURE-NAME"
```

### Pattern: Debug Issue

```bash
# 1. Check error
# 2. Search engram for patterns
# 3. Check git log for similar fixes
# 4. Apply fix
# 5. Run tests
# 6. Document lesson in engram
```

### Pattern: Deploy

```bash
# 1. Run all tests
make test-all

# 2. Check constitution
python3 scripts/constitution-gate.py --plan process/active/PLAN.yaml

# 3. Deploy
docker compose -f infra/docker-compose.yml up -d

# 4. Health check
docker ps -a --format 'table {{.Names}}\t{{.Status}}'
```

## Error Patterns & Fixes

### Security
- **Never hardcode secrets** → Use .env files
- **Always rotate secrets** → Move to environment variables
- **Rate limiting** → Implement on all APIs

### Infrastructure
- **Docker ordering** → postgres before n8n
- **Path issues** → Use absolute paths in systemd
- **Volume mounts** → Mount at /config NOT /app/config

### Testing
- **Missing dependencies** → Add to CI workflow
- **External service calls** → Always mock in CI
- **Import paths** → Use PYTHONPATH=.

### Performance
- **Polling intervals** → Reduce for lower latency
- **Chunking overflow** → Handle model limits
- **Caching** → Use Redis for frequently accessed data

## Key Commands

```bash
# Daily workflow
make doctor-quick        # Pre-flight check
make test                # Run unit tests
make lint                # Check code style
make eval                # Run evaluations
make score               # Enterprise score

# Development
make test-all            # All tests
make test-integration    # Integration tests only
make eval-structural     # Structural evals

# Cleanup
make clean               # Clean cache files
```

## Agent Patterns

### Wrapper Pattern
```python
# src/agents/opencode.py
class OpenCodeWrapper:
    def __init__(self):
        self.cli = OpenCodeCLI()
    
    def execute(self, task):
        # Wrap OpenCode CLI calls
        return self.cli.run(task)
```

### Dispatcher Pattern
```python
# apps/core/dispatcher.py
class Dispatcher:
    def route(self, request):
        # Route to appropriate agent
        agent = self.registry.get_agent(request.type)
        return agent.execute(request)
```

### Event Pattern
```python
# apps/events/publisher.py
class EventPublisher:
    def publish(self, event):
        # Publish to Redis Streams
        self.redis.xadd('events', event)
```

## Quality Gates

### Before Commit
- [ ] Tests pass
- [ ] Lint passes
- [ ] Constitution check passes
- [ ] No hardcoded secrets
- [ ] Documentation updated

### Before Deploy
- [ ] All tests pass
- [ ] Integration tests pass
- [ ] Health checks pass
- [ ] Rollback plan ready
- [ ] Monitoring configured

## Memory & Learning

### Save to Engram
After every session:
1. What worked well
2. What didn't work
3. New patterns discovered
4. Errors encountered and fixes

### Search Engram
Before starting work:
1. Search for similar tasks
2. Check for known issues
3. Review past decisions
4. Learn from past mistakes

## Automation Checklist

### Daily
- [ ] Morning: git pull + doctor-quick
- [ ] During day: SDD cycle for each feature
- [ ] Evening: test + lint + commit

### Weekly
- [ ] Monday: Review sprint progress
- [ ] Wednesday: Architecture review
- [ ] Friday: Score review + retrospective

### Monthly
- [ ] Review all lessons learned
- [ ] Update skills and patterns
- [ ] Archive completed specs
- [ ] Plan next month's goals
