# Implementation Plan: Infraestructura y Seguridad

**Spec**: [spec.md](./spec.md)

---

## Technical Context

**Language/Version**: Python 3.10+, YAML (docker, CI), Bash (scripts)
**Primary Dependencies**: pytest, docker, docker-compose, GitHub Actions
**Architecture**: Docker para servicios, pytest para tests, GitHub Actions para CI

## Constitution Check

| Principio | Cómo lo cumple |
|-----------|---------------|
| Privacidad y control | Secrets fuera del repo, `.env` gitignored |
| Seguridad por defecto | Credenciales rotadas, historial git limpiado |
| Calidad y testing | 93 tests, CI pipeline, cobertura en capa de decisión |
| Documentación | README, CHANGELOG, specs en `specs.new/` |

## Implementación

### Archivos existentes

| Archivo | Propósito |
|---------|-----------|
| `.env.example` | Placeholders de credenciales (commiteable) |
| `.gitignore` | Ignora `.env`, `__pycache__/`, `*.db`, etc. |
| `docker-compose.yml` | 3 servicios (Neo4j, Qdrant, MCP), networks, volumes, health checks |
| `.github/workflows/ci.yml` | CI: lint, test, docker build |
| `.github/workflows/deploy.yml` | CD: deploy on tag/release |
| `tests/` | 6 test files, 93 tests |
| `scripts/backup.sh` | Backup diario de Neo4j + Qdrant + config |
| `scripts/healthcheck.sh` | Health check de todos los servicios |
| `scripts/setup-systemd.sh` | Systemd services + timers |
| `SESSION_SUMMARY.md` | Registro de sesiones de desarrollo |

### Pendiente

| Tarea | Prioridad |
|-------|-----------|
| Tests unitarios para MemoryAgent, ExploreAgent, SkillAgent, VoiceAgent, ReviewAgent | P1 |
| Tests para `embeddings.py` y `rag.py` | P1 |

## Archivos del spec

```
specs.new/006-infraestructura/
├── spec.md
├── plan.md
└── tasks.md
```
