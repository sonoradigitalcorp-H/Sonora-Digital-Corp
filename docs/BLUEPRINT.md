# BLUEPRINT EJECUTIVO — Sonora Digital Corp

**Version**: 1.0.0 | **Fecha**: 2026-07-01 | **CI**: 5 verdes consecutivos (#221)

---

## 1. VISION

Un sistema operativo de inteligencia musical que opera solo, sin que Luis Daniel toque nada.
Abraham consume via PWA. Los datos fluyen solos. Los agentes se reparan solos.
El sistema se conoce a si mismo y mejora cada dia.

---

## 2. SITUACION ACTUAL

```
┌─────────────────────────────────────────────────────────────────┐
│                         🟢 HOY                                  │
│                                                                 │
│  3 specs completadas (Score 84, 77, 76)                        │
│  88 tests, 5 CI verdes consecutivos                            │
│  12 containers, 7 DBs, 19 nodos Neo4j                          │
│  6 modelos Ollama, $0 API cost                                 │
│  7/7 providers healthy                                         │
│  3 productos: ABE Music, JARVIS, AGENTIC OS                    │
│                                                                 │
│  ️ Accesible via: 149.56.46.173:8080 (War Room)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. PILARES ARQUITECTONICOS

| Pilar | Tecnologia | Proposito | Status |
|-------|-----------|-----------|--------|
| **Registry** | planner/ + config/registry.json | Abstraer fuentes de datos del codigo cliente | ✅ |
| **Decision Engine** | planner/decision_engine.py | Seleccionar mejor provider con fallback | ✅ |
| **Health** | planner/health.py | Saber que providers estan vivos | ✅ |
| **Eventos** | state/logs/events.jsonl | Traza auditable de todo | ✅ |
| **Sync** | scrapers/sync.py + cron 6h | Datos siempre frescos | ✅ |
| **Monitor** | scripts/monitor.py + systemd timer | Alertar cuando algo muere | ✅ |
| **CI** | .github/workflows/ci.yml | Validar cada cambio automaticamente | ✅ |
| **MCP Bridge** | Hermes + OpenClaw | Comunicacion entre agentes | 🟡 |

---

## 4. ROADMAP

```
SPEC-003 ──── SPEC-004 ──── SPEC-005 ──── SPEC-006 ──── SPEC-007 ──── SPEC-008
 84 ✅        77 ✅        76 ✅        activo       futuro       futuro
                          
Live Data    Capability  Production   CI Completo  Produccion   Productos
Pipeline     Registry    Hardening    + Mock       Instagram    ABE Store
Deezer,      3 caps,      Neo4j fix,  88→100+      Wikipedia    Portal,
Apple,       10 prov,     Monitor,    tests        Notifica-    Business
YouTube      70 tests    Arquitectura mockeados    ciones       Suite
```

---

## 5. QUE SIGUE ROTO (y el plan para cada uno)

| Item | Severidad | Plan | Status |
|------|-----------|------|--------|
| Instagram login wall | 🔴 CRITICAL | Inyectar cookies de sesion o remover del sync | Pendiente |
| Wikipedia 403 | 🔴 HIGH | Probar proxy residencial o API REST alternativa | Pendiente |
| TikTok handles | 🟡 HIGH | Verificar datos CEO vs handles reales | Pendiente |
| Mock tests incompletos | 🟡 MEDIUM | SPEC-006: Apple, YouTube, TikTok, Spotify, Wiki | En progreso |
| Monitor sin alertas | 🟡 MEDIUM | Agregar webhook Telegram cuando container muere | Pendiente |

---

## 6. REGLAS DE ORO (no negociables)

```
1.  SPEC antes de codigo        6.  Documentar mientras construyes
2.  CI verde antes de push      7.  Si algo queda roto → BROKEN list
3.  Verificar desde IP publica   8.  No construir con CRITICAL abiertos
4.  Tests locales antes commit   9.  Cada fix requiere verificacion
5.  Un cambio por commit        10. Session summary en memory/ al cerrar
```

---

## 7. METRICAS CLAVE

| Metrica | Hoy | Target | Proximo hito |
|---------|-----|--------|-------------|
| CI verdes consecutivos | 5 | >30 | 10 |
| Tests totales | 88 | >100 | 90 (SPEC-006) |
| Broken items | 5 | 0 | 4 |
| Providers healthy | 7/7 | 7/7 | Mantener |
| Container health | 12/12 | 12/12 | Mantener |
| Specs completadas | 3 | 5 | 4 (SPEC-006) |
| API cost | $0 | $0 | $0 siempre |

---

## 8. PROXIMA ACCION

```
ESPECIFICACION: SPEC-20260701-006 — CI Completo (activo)
FALTAN: mock tests para Apple Music, YouTube, TikTok, Spotify, Wikipedia
META: 90+ tests en CI, 6/6 collectors mockeados
TIEMPO: 1 sesion
```

**War Room**: `http://149.56.46.173:8080/`  
**Especificacion**: `process/active/SPEC-20260701-006/spec.md`  
**Arquitectura**: `docs/ARQUITECTURA.md`  
**Protocolo**: `docs/PROTOCOLO.md`  

---

*"Construye el registry. Todo lo demas emerge."*
