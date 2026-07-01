# SPEC — Auto Session Start + Session Memory

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260630-000` |
| **Fecha** | 2026-06-30 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | completado |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Eliminar la fricción de inicio de sesión mostrando automáticamente el estado del proyecto (branch, cambios, otras sesiones) y guardando resumen al cerrar para que el usuario no tenga que repetir contexto.

---

## 2. Value Driver

**founder-independence** — El usuario pierde tiempo configurando cada sesión. Esto automatiza el diagnóstico inicial.

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Al iniciar sesión, mostrar automáticamente: carpeta actual, branch, diferencia con main, cambios pendientes, últimas ramas activas |
| FR2 | Al cerrar sesión, guardar resumen en `state/ultima-sesion.json` para que la próxima lo lea |
| FR3 | Las correcciones del usuario se guardan en `memory/sdc-rules.md` y se leen al iniciar |
| FR4 | Fusionar cambios de CLAUDE.md entre sesiones para no perder configuración |

---

## 4. Success Criteria

- [x] `scripts/session-status.sh` ejecuta y muestra toda la info
- [x] `scripts/close-session.sh` guarda resumen en JSON
- [x] `memory/sdc-rules.md` existe y session-status.sh lo lee
- [x] CLAUDE.md tiene instrucciones claras para el agente
- [x] Commit pusheado a GitHub

---

## 5. Gherkin Scenarios

Ver `gherkin/SPEC-20260630-000.feature`

---

## 6. Edge Cases

- [EC1] Sin conexión a GitHub: `git fetch` falla, script sigue funcionando
- [EC2] Engram caído: session-status.sh muestra "sin datos" en vez de fallar
- [EC3] Sin resumen previo: muestra "primera sesión" en vez de error

---

## 7. Technical Approach

- `CLAUDE.md`: protocolo que el agente debe seguir al iniciar sesión
- `scripts/session-status.sh`: bash script que corre `git status`, `git branch`, `git log`, y lee `state/ultima-sesion.json` + `memory/sdc-rules.md`
- `scripts/close-session.sh`: actualizado para guardar `state/ultima-sesion.json`
- `memory/sdc-rules.md`: reglas aprendidas escritas manualmente por el agente

---

## 8. Dependencies

- bash, git, python3

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `session_started` | Cada vez que se abre una sesión |
| `session_closed` | Cuando se ejecuta close-session.sh |

---

## 10. Kill Criteria

Si el usuario prefiere no tener resumen automático.

---

## 11. Scale Criteria

Cuando haya más de 10 reglas en sdc-rules.md, migrar a formato estructurado.
