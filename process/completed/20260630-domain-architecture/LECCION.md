# Lección — SPEC-20260630-006

| Campo | Valor |
|-------|-------|
| **Spec** | `SPEC-20260630-006` |
| **Tier** | 2 |
| **Fecha** | 2026-06-30 |

---

## ¿Qué pasó?

Organización explícita de los 11 contenedores Docker en 3 dominios (Core, UX, Data) con labels, health survey script, y Redis Stream consumer groups.

---

## ¿Qué salió bien?

- [x] 11 contenedores con labels `sdc.domain=data|core|ux`
- [x] `agents-survey.sh` — healthcheck consolidado por dominio
- [x] Redis consumer groups: agents-core, agents-ux
- [x] Dependencias claras en docker-compose.yml
- [x] docker-compose.yml válido y build exitoso

---

## ¿Qué salió mal?

- [ ] Las inserciones con sed rompieron YAML (duplicaron labels)
- [ ] Los labels duplicados tardaron 3 intentos en corregirse
- [ ] La separación real de contenedores por dominio sigue siendo conceptual (todos corren en el mismo host)

---

## ¿Qué haríamos diferente?

- No usar sed para modificar YAML — siempre editar con precisión
- La verdadera separación por dominio requeriría hosts Docker separados o Swarm
- Para el tamaño actual (1 VPS), la estructura de labels es suficiente

---

## Engram Tags

domain-architecture, docker, labels, survey, consumer-groups, spec-006
