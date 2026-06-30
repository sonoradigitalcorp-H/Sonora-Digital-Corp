# Lección — SPEC-20260630-003

| Campo | Valor |
|-------|-------|
| **Spec** | `SPEC-20260630-003` |
| **Tier** | 2 |
| **Fecha** | 2026-06-30 |

---

## ¿Qué pasó?

Migración de Jarvis Core y WebUI de systemd a contenedores Docker con Python 3.12-slim.

---

## ¿Qué salió bien?

- [x] Dockerfile multi-stage: base → test (432 tests) → jarvis-core → jarvis-webui
- [x] Build exitoso en local y VPS
- [x] Healthchecks HTTP reales (reemplazan pgrep)
- [x] docker-compose.yml unificado con 11 servicios
- [x] Systemd apagado, Docker como único entrypoint
- [x] WebUI responde: GET /api/enterprise-score → 200 OK

---

## ¿Qué salió mal?

- [ ] PyAudio no compila en python:3.12-slim (requirements-docker.txt sin voice pesado)
- [ ] 2 tests de ReviewAgent fallaban por paths de archivo (AGENTS.md no copiado)
- [ ] MCP Server sigue unhealthy (preexistente)
- [ ] Healthcheck de webui tarda ~1 min en transicionar a healthy
- [ ] Variables ENV con defaults en Dockerfile generan warnings de seguridad

---

## ¿Qué haríamos diferente?

- Separar voice en su propio contenedor (no mezclar con core)
- Usar --build-arg para secrets en vez de ENV con defaults
- Healthcheck más rápido: intervalo 15s, start_period 10s

---

## Engram Tags

docker, containerization, migration, python3.12, systemd, healthcheck, ci-cd, spec-003
