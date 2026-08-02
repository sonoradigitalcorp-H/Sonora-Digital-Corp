# SPEC — Self-Healing Loop + Notificaciones

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260701-007` |
| **Fecha** | 2026-07-01 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Hoy el monitor detecta contenedores caídos y escribe a JSONL — pero NADIE reacciona. Que el sistema se repare solo: cuando un contenedor muere, reinicio automático con verificación. Si no revive tras 3 intentos, que notifique a Luis Daniel por Telegram.

---

## 2. Value Driver

founder-independence, automation, reliability

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | `scripts/healer.py` lee eventos `container_down` recientes de events.jsonl |
| FR2 | Ejecuta `docker restart <container>` con timeout 30s |
| FR3 | Verifica health después del restart (poll cada 10s, max 3 intentos) |
| FR4 | Si revive: escribe `healing_success` a events.jsonl |
| FR5 | Si falla 3 intentos: escribe `container_critical` a events.jsonl |
| FR6 | `container_critical` dispara notificación Telegram via webhook n8n |
| FR7 | Healer corre via systemd timer 30s después del monitor (2min ciclo) |
| FR8 | No reinicia contenedores que ya están siendo healing (dedup) |
| FR9 | Tests mock para healer (simular docker, events, webhook) |

---

## 4. Success Criteria

- [ ] Container caído → reinicio automático en <60s
- [ ] 3 intentos fallidos → `container_critical` en events.jsonl
- [ ] 3 intentos fallidos → notificación Telegram a Luis Daniel
- [ ] Healer no reinicia contenedores duplicados (in-flight dedup)
- [ ] Tests mock pasan en CI
- [ ] Score ≥60

---

## 5. Gherkin Scenarios

Ver `gherkin/SPEC-20260701-007.feature`

---

## 6. Edge Cases

- [EC1] Docker daemon no responde → healer no reintenta infinitamente (max 2 fails)
- [EC2] Contenedor ya restarting → healer skip (docker ps status checking)
- [EC3] events.jsonl corrupto → healer no crash, log warning
- [EC4] Webhook n8n caído → no reintentar, solo log

---

## 7. Technical Approach

```
Flujo:
  monitor (cada 2min) → detecta container_down → events.jsonl
                          ↓ (30s despues)
  healer (cada 2min)  → lee container_down de events.jsonl
                          ↓
                        docker restart $container
                          ↓ (espera 30s, poll 10s)
                        si healthy → healing_success
                        si no → reintentar (max 3)
                          ↓ si 3 fails
                        container_critical → n8n webhook → Telegram
```

Archivos:
- `scripts/healer.py` — lógica de healing
- `.config/systemd/user/healer.timer` — cada 2min, 30s offset
- `.config/systemd/user/healer.service` — ejecuta healer.py
- `tests/collectors/test_healer.py` — tests con mock
- n8n webhook — endpoint POST en n8n que envía Telegram

---

## 8. Dependencies

- `scripts/monitor.py` funcionando ✅
- n8n en :5678 ✅
- Telegram bot @ABEfenix_bot ✅
- Docker CLI accesible ✅

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `healing_attempt` | Healer intenta restart |
| `healing_success` | Container revive tras restart |
| `healing_failure` | Container no revive tras 3 intentos |
| `container_critical` | 3 fails consecutivos, notificando |

---

## 10. Kill Criteria

Si después de 1 semana el healing ha hecho más daño que beneficio (reinicia contenedores que no debía), desactivar timer y mantener solo notificaciones.

---

## 11. Scale Criteria

- Healing con evaluación de dependencias (Neo4j: "no reiniciar X sin Y")
- Healing progresivo: primero un intento, si falla escalar a acciones más agresivas
- Dashboard de healing con histórico 7 días
