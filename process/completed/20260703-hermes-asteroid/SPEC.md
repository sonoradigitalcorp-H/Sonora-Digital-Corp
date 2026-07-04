# SPEC — Hermes Asteroid Unification

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260703-001` |
| **Fecha** | 2026-07-03 |
| **Autor** | OpenClaw |
| **Tier** | 3 |
| **Estado** | completado |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Unificar el ecosistema Hermes + OpenCode + OpenClaw en VPS sdc-prod como único servidor, eliminando servicios duplicados en laptop y estableciendo identidad de agente como "asteroid" en lugar de "communication layer".

---

## 2. Value Driver

Automation Impact + Operational Simplicity — consolidar toda la infra en un solo servidor elimina duplicación, reduce carga de laptop y centraliza configuración.

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Diagnosticar arquitectura real (VPS vs laptop) con `ss -tlnp`, `ps aux`, `docker ps` |
| FR2 | Matar servicios duplicados de OpenClaw y Docker en laptop |
| FR3 | Re-escribir SOUL.md con identidad "Hermes Asteroid" |
| FR4 | Crear TRUTH.md como fuente única de verdad (servicios, puertos, personas, máquinas) |
| FR5 | Corregir SYSTEM.md con datos verificados (7+ errores) |
| FR6 | Sincronizar 42 OpenClaw skills de laptop → VPS |
| FR7 | Unificar configs: opencode.json global, project configs simplificadas, tui.json |

---

## 4. Success Criteria

- [ ] Laptop load reducido de 9.24 → <3.5 (servicios duplicados eliminados)
- [ ] VPS tiene todas las skills (0 → 42), configs unificadas
- [ ] SOUL.md, TRUTH.md, SYSTEM.md escritos con datos verificados
- [ ] Personality sdc-mystic creada
- [ ] Todos los cron jobs verificados (12 activos)
- [ ] Pipeline daily-pipeline.sh reparado (python → python3)

---

## 5. Gherkin Scenarios

Ver `gherkin/SPEC-20260703-001.feature`

---

## 6. Edge Cases

- OpenClaw en laptop tenía `Restart=always` — requería systemd override para matarlo permanentemente
- state.db Engram vacío (0 bytes) — no era pérdida de datos, solo no seedeado en este VPS
- Qdrant version mismatch (client 1.18.0 vs server 1.7.4) — genera warning pero funciona

---

## 7. Technical Approach

1. Diagnóstico: `hostname`, `whoami`, `ss -tlnp`, `ps aux`, `docker ps` en ambas máquinas
2. Matar procesos: `systemctl --user stop` + `systemctl mask` para evitar restart automático
3. Documentación: Escribir SOUL.md, TRUTH.md, SYSTEM.md basado en datos verificados
4. Sync: `rsync` skills de laptop a VPS
5. Config: OpenCode config merge (global + project), simplificar SDC 278→193 líneas

---

## 8. Dependencies

- Acceso SSH a VPS (149.56.46.173)
- systemd user services en laptop
- rsync en ambas máquinas

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `session.start` | Inicio de sesión |
| `identity.changed` | SOUL.md rewrite completado |
| `services.killed` | Duplicados eliminados en laptop |
| `skills.synced` | 42 skills migradas a VPS |
| `config.unified` | Configs consolidadas en VPS |
| `pipeline.fixed` | daily-pipeline.sh reparado |

---

## 10. Kill Criteria

Si VPS no es accesible o laptop no puede SSH — abortar y diagnosticar red primero.

---

## 11. Scale Criteria

Cuando haya más de 3 máquinas o 20 servicios, migrar a Terraform/Ansible para gestión de infra.
