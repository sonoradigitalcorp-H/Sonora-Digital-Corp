# Aciertos y No Aciertos — Do's and Don'ts Absolutos

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md + 10-RULES.md
**Version**: 1.0.0
**Updated**: 2026-07-01
**Source**: Todo lo aprendido desde constitution, sesiones, errores, y fixes.

---

## 🔥 ABSOLUTOS (De la Constitución)

### ✅ ACIERTO — Optimizar para:
| Prioridad | Optimizar por | Por qué |
|-----------|--------------|---------|
| 1 | **Value** | Si no crea valor medible, no se construye |
| 2 | **Revenue** | Cada feature debe atar a un business metric |
| 3 | **Reliability** | La confianza se gana con uptime, no con features |
| 4 | **Simplicity** | Complejidad técnica sin valor medible = deuda |
| 5 | **Reusability** | Una solución reusable > 3 soluciones one-off |
| 6 | **Survivability** | Si el founder desaparece, el sistema opera solo |
| 7 | **Scalability** | 10x sin redesign o no pasa el gate |
| 8 | **Automation** | Manual work = founder dependency = riesgo |
| 9 | **Knowledge** | Todo conocimiento debe inmortalizarse |

### ❌ NO ACIERTO — Optimizar para:
| Prioridad | No optimizar por | Por qué |
|-----------|-----------------|---------|
| 1 | **Activity** | Movimiento ≠ progreso. Output ≠ outcome |
| 2 | **Novelty** | Nuevo ≠ mejor. Shiny object syndrome mata |
| 3 | **Tool adoption** | Tools son reemplazables. Capabilities son permanentes |
| 4 | **Framework adoption** | Frameworks mueren. Arquitectura sobrevive |
| 5 | **Model adoption** | Modelos cambian cada 3 meses. Policies no |
| 6 | **Technical complexity** | Complejidad sin valor justificado = deuda técnica |

---

## 🏛️ DECISION HIERARCHY (Obligatorio)

### ✅ ACIERTO — Seguir este orden SIEMPRE:
```
VDD → EDD → PDD → ODD → SDD → BDD → TDD → Implementation → Technology → Tools
```

- **VDD**: ¿Qué valor genera?
- **EDD**: ¿Qué evidencia tenemos de que funciona?
- **PDD**: ¿Qué políticas aplican?
- **ODD**: ¿Cómo opera en producción?
- **SDD**: Spec escrito y aprobado antes de código
- **BDD**: Gherkin scenarios (happy path + edge cases)
- **TDD**: Tests first, code second
- **Technology/Tools**: Último, después de todo lo anterior

### ❌ NO ACIERTO — Tools first
```
Tools → Technology → Implementation → (el resto)
```
Tools nunca deben conducir decisiones. El valor conduce.

---

## 📋 10 REGLAS ABSOLUTAS (10-RULES.md)

| # | ✅ ACIERTO | ❌ NO ACIERTO |
|---|-----------|--------------|
| 1 | **Spec first**: Escribir spec.md con Gherkin antes de tocar código | Código sin spec aprobado |
| 2 | **Tests green**: Todos los tests pasan antes de merge | PR bloqueado, force-push para saltar |
| 3 | **Humans decide**: Proponer, no imponer | Auto-merge sin approval humano |
| 4 | **Todo en el repo**: Código, specs, ADRs, decisiones, memoria | Conocimiento en chats, emails, o cabeza del founder |
| 5 | **PR + 1 approval**: Toda cambio a main via PR | Commit directo a main |
| 6 | **OpenCode always**: Sin Copilot, sin Claude Code, sin Codex | Modelos externos como primary |
| 7 | **Stack fixed**: Python 3.10+, pytest, GitHub Actions, OpenRouter | Cambio de stack sin ADR |
| 8 | **Continuous learning**: Escribir lecciones a memory/lecciones.json | Ignorar errores pasados |
| 9 | **Value first**: Toda feature atada a revenue/retention/CAC/LTV | Features sin business metric |
| 10 | **One brain**: Un repo, una verdad, una constitución | Servicios duplicados, paths múltiples |

---

## 🧠 VERDAD ABSOLUTA (TRUTH.md)

### ✅ ACIERTO — Paths y symlinks
| Regla | Ejemplo |
|-------|---------|
| Usar `~/sdc` como symlink unificado | `~/sdc → /home/ubuntu/sonora-digital-corp/` |
| Symlinks para directorios canónicos | `harnesses/ → sonora-enterprise-os/harnesses/` |
| Actualizar TRUTH.md después de cada sesión | Commit hash, docker state, services |
| Verificar CHECKSUMS.sha256 tras editar constitution | `sha256sum -c CHECKSUMS.sha256` |

### ❌ NO ACIERTO — Paths rotos
| Antipatrón | Por qué | Fix |
|------------|---------|-----|
| Paths hardcodeados `/home/mystic/...` en workflows | No existen en VPS | Usar `~/sdc` o variable de entorno |
| Systemd + Docker mismo servicio corriendo | Causa 409 Conflict, recursos duplicados | Elegir Docker (más portable), matar systemd |
| Crontabs con paths inconsistentes | ~/sdc vs /home/ubuntu/sdc vs /home/ubuntu/sonora-digital-corp | Siempre usar la resolución via symlink |
| Docker containers con healthcheck a `localhost` | Next.js escucha en IP Docker, no 127.0.0.1 | Usar hostname del container: `http://sdc-langfuse:3000` |

---

## 🧩 INFRAESTRUCTURA (Lecciones prácticas)

### ✅ ACIERTO
| Área | Práctica |
|------|----------|
| **Healthchecks** | Langfuse: `http://sdc-langfuse:3000/api/public/health`. Playwright MCP: `pgrep -f playwright-mcp` |
| **Docker** | Un solo docker-compose.yml en infra/. Servicios con prefijo `sdc-` |
| **Cron** | Todas las rutas via `~/sdc` symlink. Logging a `state/logs/` |
| **Systemd** | Solo para servicios sin Docker (e.g., `abe-daemon`) |
| **Self-healing** | Cadena completa: Detect→Diagnose→Recover→Retest→Document→Learn |
| **Coverage** | `fail_under = 80` en pyproject.toml + CI |
| **Monitor** | Health check automático cada 15 min |

### ❌ NO ACIERTO
| Antipatrón | Lección |
|------------|---------|
| Dejar containers unhealthy | Langfuse estuvo semanas unhealthy por mal healthcheck |
| Systemd + Docker split-brain | jarvis-core, telegram-bot, mcp-gateway duplicados → 409 Conflict |
| `fail_under = 60` | Constitución exige ≥80 |
| Workflows con `/home/mystic/...` | Runner no existe en VPS |
| No verificar checksums | TRUTH.md tenía commit hash incorrecto (`9420abc` vs `a7d9ee9`) |

---

## 🧬 MEMORIA (Engram)

### ✅ ACIERTO
| Concepto | Implementación |
|----------|---------------|
| 7 capas de memoria | working(0), task(1), project(2), customer(3), business(4), historical(5), strategic(6) |
| 4 niveles de importancia | critical(3), high(2), medium(1), low(0) |
| Decay automático | 30 días sin acceso → demote |
| FTS5 search | Búsqueda full-text en summary + context |
| Layer-aware queries | Filtrar por capa para respuestas más precisas |

### ❌ NO ACIERTO
- 4 niveles de importancia sin capas (old behavior) — no distingue dominio
- Memoria sin decay — se llena de ruido
- DB en ubicación inconsistente (`~/.engram/` vs `state/`) — auto-detect resuelve

---

## 📊 ENTERPRISE SCORE

### ✅ ACIERTO
| Métrica | Peso |
|---------|------|
| 10 métricas × 10 puntos = 100 max | Threshold: ≥60 para aprobar |
| Revenue Impact, Scalability, Reusability | Automation Impact, Knowledge Impact |
| Reliability, Founder Independence | Operational Simplicity, Customer Value, FinOps Efficiency |

### ❌ NO ACIERTO
- 3 definiciones contradictorias (OMEGA-PROMPT: 9 métricas, enterprise-score.md: "9 Metrics" pero lista 10, AGENTS.md: "9 metrics × 10") → Unificado a 10 métricas
- Score 23/100 sin acciones correctivas — debe generar `kill_recommendation` si < 60

---

## 🧪 TESTS Y CALIDAD

### ✅ ACIERTO
| Regla | Detalle |
|-------|---------|
| TDD: Tests first, código second | CI enforce: no test file → bloquea PR |
| Coverage ≥80% | fail_under=80 en pytest-cov |
| Ruff lint | CI corre ruff check |
| 42 tests pasando | Live data pipeline + ABE Music CRM |

### ❌ NO ACIERTO
- `test_rag.py` failing (ModuleNotFoundError: qdrant_client) — ISSUE abierto
- flake8 vs pyproject.toml line-length mismatch (100 vs 160)
- No hay tests de integración para scrapers reales (usan APIs públicas sin mock)

---

## 📦 CAPABILITIES (Harnesses, Skills, Initiatives)

### ✅ ACIERTO
| Asset | Estado | Campos requeridos |
|-------|--------|-------------------|
| 10 Harnesses (OS) | 100% completos | 12/12 campos |
| 10 Skills | 100% completos | 14/14 campos |
| 3 Initiatives | 100% completos | 9/9 campos |
| Skills canónicos via symlink | `skills/ → sonora-enterprise-os/skills/` |

### ❌ NO ACIERTO
- 10 harnesses catalogados en MANIFEST.md pero sin construir (antes de este fix) — ahora existen
- Skills solo en `platforms/telegram/skills/` (antes) — ahora en canónico + symlink

---

## 🔄 PIPELINE DE TRABAJO

### ✅ ACIERTO — Flujo correcto
```
1. Identificar valor (VDD)
2. Revisar evidencia (EDD)
3. Verificar policies (PDD)
4. Diseñar operación (ODD)
5. Escribir spec (SDD) → process/active/SPEC-{ID}.md
6. Escribir Gherkin (BDD) → process/active/gherkin/{ID}.feature
7. Calcular Score → process/active/SCORE-{ID}.md
8. Escribir tests (TDD) → tests/unit/test_{module}.py
9. Implementar código
10. Escribir ADR → process/active/ADR-{ID}.md
11. Escribir Lección → process/active/LECCION-{ID}.md
12. Emitir eventos → state/logs/events.jsonl
13. Hacer PR con ≥1 approval
14. Merge a main
15. Archivar en process/completed/
```

### ❌ NO ACIERTO — Atajos prohibidos
- Spec → Código (sin Score, Gherkin, Tests)
- Código → Commit (sin PR, sin approval)
- Commit → Push a main (sin branch)
- Implementar → Olvidar (sin ADR, sin Lección)
- Fix urgente → Sin evento (no documentado = no ocurrió)

---

## ⚡ COMANDOS RÁPIDOS

### ✅ ACIERTO
```bash
cd ~/sdc                          # ir al repo (via symlink)
bash scripts/process-pipeline.sh  # gestionar pipeline
pytest tests/unit/ -q             # tests unitarios
docker compose -f infra/docker-compose.yml ps  # ver containers
git pull --ff-only origin main    # sync
```

### ❌ NO ACIERTO
```bash
cd /home/ubuntu/sdc               # path directo (usa symlink ~/sdc)
cd /home/ubuntu/sonora-digital-corp # path físico (usa symlink ~/sdc)
git push --force                   # prohibido (10-RULES.md #2)
```

---

## 📌 RESUMEN — Regla de Oro

> **Acierto**: Código que sobrevive al founder, documentado en ADR, probado con tests, conectado a revenue, y almacenado en memoria perpetua.
>
> **No acierto**: Código que solo tú entiendes, solo tú puedes operar, y solo tú recuerdas por qué existe.

---

*Este documento se actualiza automáticamente. Fuente de verdad: OMEGA-PROMPT-v10.0.md*
