# SPEC — FASE 1: Dockerización de Jarvis + WebUI

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260630-003` |
| **Fecha** | 2026-06-30 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Migrar Jarvis Core y WebUI de systemd a contenedores Docker, eliminando la dependencia del Python del host VPS (3.10 → 3.12). Unificar toda la infraestructura bajo un solo `docker-compose.yml`.

---

## 2. Value Driver

reliability, scalability, automation, founder-independence

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Dockerfile para Jarvis Core basado en `python:3.12-slim` con todos los módulos |
| FR2 | Dockerfile para WebUI basado en `python:3.12-slim` con FastAPI + routes |
| FR3 | Ambos contenedores en `docker-compose.yml` con depends_on a servicios de datos |
| FR4 | Healthchecks HTTP para todos los contenedores (reemplazar pgrep en mcp-server) |
| FR5 | Variables de entorno via `.env` file, no hardcodeadas |
| FR6 | Tests (432) corren dentro del contenedor en build time |
| FR7 | GitHub Actions: build + test dentro del contenedor en cada push |
| FR8 | Systemd services apagados SOLO después de verificar que Docker funciona |

---

## 4. Success Criteria

- [ ] `docker compose build` produce imágenes sin errores
- [ ] `docker compose up -d` levanta los 11 contenedores (9 existentes + jarvis + webui)
- [ ] `GET /api/enterprise-score` responde desde el contenedor webui
- [ ] Tests corren dentro del contenedor en CI
- [ ] Systemd apagado, docker compose como único entrypoint

---

## 5. Gherkin Scenarios

Ver `process/active/gherkin/SPEC-20260630-003.feature`

---

## 6. Edge Cases

- [EC1] Puerto 5174 ocupado por systemd al migrar
- [EC2] Variables de entorno no propagadas al contenedor
- [EC3] Contenedor webui arranca antes que neo4j/qdrant (dependencia rota)
- [EC4] Build sin caché en VPS con poca RAM

---

## 7. Technical Approach

- Un solo Dockerfile base (`infra/docker/jarvis/Dockerfile`) con Python 3.12-slim
- docker-compose.yml usa `image:` (build local) con `command:` override
- Dependencias: neo4j (7687), qdrant (6333), redis (6379), postgres (5432)
- Healthchecks HTTP (wget/curl a endpoints internos)
- CI: `docker build` + `docker run pytest` en GitHub Actions

---

## 8. Dependencies

- Docker Engine en VPS ✅ (ya corre)
- docker-compose.yml existente con 9 servicios ✅
- `.env` con secrets (ya existe, chmod 600) ✅

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `docker_build_started` | Build de imágenes |
| `docker_build_completed` | Build exitoso |
| `migration_systemd_shutdown` | Systemd apagado |
| `migration_docker_active` | Docker compose funcionando |

---

## 10. Kill Criteria

Si después de 3 intentos el build falla o los contenedores no responden, revertir a systemd y documentar.

---

## 11. Scale Criteria

Cuando haya >4 contenedores de aplicación, migrar a Docker Swarm o Kubernetes.
