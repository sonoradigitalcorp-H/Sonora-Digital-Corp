# SPEC — FASE 4: Extracción por Dominios

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260630-006` |
| **Fecha** | 2026-06-30 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Organizar los 11 contenedores Docker en 3 dominios explícitos (Core, UX, Data) con dependencias claras y healthchecks por dominio. Añadir Redis Stream consumer groups para comunicación entre dominios.

---

## 2. Value Driver

reliability, scalability, operational-simplicity

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | docker-compose.yml organizado por dominios con labels |
| FR2 | `agents-survey.sh` — reporta healthcheck de todos los contenedores por dominio |
| FR3 | Redis Stream consumer groups: agents-core, agents-ux |
| FR4 | Dependencias claras: Core → Data, UX → Redis |
| FR5 | Healthcheck HTTP para todos los contenedores |
| FR6 | Tests de dominio: verificar que cada contenedor responde |

---

## 4. Success Criteria

- [ ] `docker compose ps` muestra 11 contenedores con labels de dominio
- [ ] `agents-survey.sh` reporta todos los servicios con su estado
- [ ] Consumer groups creados en Redis Streams
- [ ] Core puede caerse sin afectar UX
- [ ] Todos los tests pasan (443+)

---

## 5. Technical Approach

- Labels en docker-compose: `sdc.domain=core|ux|data`
- `scripts/agents-survey.sh` — curl a cada healthcheck + redis info
- `apps/jarvis/src/core/redis_streams.py` — agregar `ensure_consumer_group()`
- docker-compose.yml: depends_on solo intra-dominio, Redis como bus inter-dominio

---

## 6. Dependencies

- Redis Streams (FASE 2) operativo ✅
- Docker compose networks ✅

---

## 7. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `domain_architecture_defined` | Labels y grupos aplicados |
| `consumer_groups_created` | Redis consumer groups listos |

---

## 8. Kill Criteria

Si la separación por dominios introduce latencia de red perceptible, mantener la arquitectura actual y solo los labels.

---

## 9. Scale Criteria

Cuando haya >20 contenedores, migrar a Docker Swarm para orquestación multi-host.
