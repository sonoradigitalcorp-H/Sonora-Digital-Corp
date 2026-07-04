# SDD-20260703-003: UNIFIED BRAIN v2

**Status**: Plan · **Prioridad**: HIGH
**Inherits**: OMEGA PROMPT v10.0 + SOUL.md (asteroid)
**Enterprise Score Target**: 35 → 82

---

## VDD: ¿Por qué?

Unificar Engram + Neo4j + Qdrant + Hermes state + eventos + lecciones en un solo cerebro consultable. Cualquier agente (JARVIS, Hermes, OpenClaw, Telegram bot) pregunta una vez y obtiene respuesta desde la mejor fuente disponible.

## EDD: ¿Qué cambió vs el plan original?

| Aspecto | Plan original (ayer) | Realidad hoy |
|---------|---------------------|--------------|
| Target machine | Laptop + VPS | Solo VPS (149.56.46.173) |
| OpenClaw skills | 0 en VPS | 42 en VPS |
| TRUTH.md | No existía | Existe con datos verificados |
| SOUL.md | "com layer" | "asteroid" |
| Configs | 278+39+28 | 193+25+18 |
| Load VPS | ~0.5 | 0.15 |
| Personality sdc-mystic | No existía | Creada |
| Daily pipeline | python error | Fixed |
| Laptop OpenClaw | Running | Muerto (override Restart=no) |

**Lo que NO cambia de la data real en stores:**
- Neo4j: 36 nodos (Service, Achievement, Spec, Person, Capability, Session)
- Qdrant: 2 colecciones (abe-artists 5pts dim7, abe-business 5pts dim384)
- Engram: 52 memorias, 7 layers
- Hermes state.db: sesiones con FTS5+trigram
- Events JSONL: generándose cada 15 min

**Nuevas consideraciones post-cambios:**
- BrainService corre en VPS como systemd o Docker
- Los paths son /home/ubuntu/sonora-digital-corp/ (no /home/mystic/)
- Hermes state.db está en /home/ubuntu/.hermes/state.db (292MB)
- Ya hay cron jobs cada 15 min → sync puede integrarse ahí
- MCP tool debe registrarse en Hermes config.yaml (no en OpenCode)

---

## PDD: Políticas

1. BrainService es SOLO para consulta — no es fuente de verdad primaria (TRUTH.md lo es)
2. TRUTH.md > Neo4j > Qdrant > Engram — orden de autoridad
3. Sync incremental cada 30 min via cron existente
4. Deduplicación automática post-sync
5. Toda consulta registra acceso (self-learning)
6. Si Neo4j falla → Qdrant → Engram → "no sé" (graceful degradation)

---

## ODD: Arquitectura en VPS

```
VPS (sdc-prod, 149.56.46.173)
┌─────────────────────────────────────────────────────┐
│  BrainService (systemd)                             │
│  ┌─────────────────────────────────────────────┐    │
│  │  MCP Tool: unified_brain_query              │    │
│  │  Web: /brain/search, /brain/stats           │    │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────────┐  │    │
│  │  │ Neo4j   │ │ Qdrant   │ │ Engram      │  │    │
│  │  │ :7687   │ │ :6333    │ │ state/*.db  │  │    │
│  │  └─────────┘ └──────────┘ └─────────────┘  │    │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────────┐  │    │
│  │  │ Hermes  │ │ Events   │ │ Lecciones   │  │    │
│  │  │ state   │ │ JSONL    │ │ JSON        │  │    │
│  │  └─────────┘ └──────────┘ └─────────────┘  │    │
│  └─────────────────────────────────────────────┘    │
│                                                     │
│  Agentes que consultan:                             │
│  Hermes (:8643) → MCP tool call                     │
│  OpenClaw (:18789) → HTTP a /brain/search           │
│  JARVIS (:5174) → MCP bridge → BrainService        │
│  Telegram bot → Hermes → BrainService               │
└─────────────────────────────────────────────────────┘
```

---

## PLAN DE SPRINTS

```
SPRINT 1: Foundation (6 tasks)    ~45 min
SPRINT 2: Ingestors (6 tasks)     ~60 min
SPRINT 3: Sync + Cron (4 tasks)   ~30 min
SPRINT 4: MCP Tool (3 tasks)      ~30 min
SPRINT 5: Web UI + Tests (4 tasks) ~45 min
─────────────────────────────────────────
TOTAL: 23 tasks                    ~3.5 hours
```

---

### SPRINT 1: FOUNDATION — BrainService Core

---

#### TASK S1-1: Create apps/brain/ directory structure on VPS

```
Máquina: VPS
Objective: Scaffold the BrainService package
Comando:
  ssh ubuntu@149.56.46.173 "mkdir -p /home/ubuntu/sonora-digital-corp/apps/brain/ingestors && touch /home/ubuntu/sonora-digital-corp/apps/brain/__init__.py /home/ubuntu/sonora-digital-corp/apps/brain/ingestors/__init__.py"
Postcondición: apps/brain/ con __init__.py y ingestors/__init__.py
Verificación: test -d /home/ubuntu/sonora-digital-corp/apps/brain/ && echo "OK"
```

---

#### TASK S1-2: Create BrainConfig (VPS paths)

```
Máquina: VPS
Archivo: /home/ubuntu/sonora-digital-corp/apps/brain/config.py

Contenido:
```python
from pydantic import BaseSettings

class BrainConfig(BaseSettings):
    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "sdc-neo4j-p4ss"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Engram
    engram_path: str = "state/engram.db"

    # Hermes state
    hermes_state_path: str = "/home/ubuntu/.hermes/state.db"

    # Eventos
    events_path: str = "state/logs/events.jsonl"

    # Embeddings
    embed_model: str = "all-MiniLM-L6-v2"
    embed_device: str = "cpu"

    # Sync
    sync_interval_minutes: int = 30

    class Config:
        env_prefix = "BRAIN_"
```

Verificación: `python3 -c "from apps.brain.config import BrainConfig; c=BrainConfig(); print(c.neo4j_uri)"`
```

---

#### TASK S1-3: Create unified KnowledgeNode model

```
Máquina: VPS
Archivo: /home/ubuntu/sonora-digital-corp/apps/brain/models.py
Verificación: python3 -c "from apps.brain.models import KnowledgeNode; print('OK')"
```

---

#### TASK S1-4: Create BrainService scaffold with connections

```
Máquina: VPS
Archivo: /home/ubuntu/sonora-digital-corp/apps/brain/service.py
Conexiones a: Neo4j (bolt driver), Qdrant (client), Engram (sqlite3)
Métodos: ready (health check), close
Verificación: python3 -c "from apps.brain.service import BrainService; b=BrainService(); print(b.ready())"
```

---

#### TASK S1-5: Verify Neo4j connectivity from BrainService

```
Test: BrainService connects to Neo4j at bolt://localhost:7687
Comando: python3 -c "
from apps.brain.service import BrainService;
b=BrainService();
with b.neo4j.session() as s:
    r=s.run('MATCH (n) RETURN count(n) as c').single()
    print(f'Neo4j OK: {r[\"c\"]} nodes')
"
Expected: "Neo4j OK: 36 nodes" (o el número actual)
```

---

#### TASK S1-6: Verify Qdrant + Engram connectivity

```
Test: Qdrant returns collections list
Comando: python3 -c "
from apps.brain.service import BrainService;
b=BrainService();
cols=b.qdrant.get_collections()
print(f'Qdrant OK: {len(cols.collections)} collections')
"
Test: Engram can read memories
Comando: python3 -c "
import sqlite3;
c=sqlite3.connect('state/engram.db');
cur=c.execute('SELECT count(*) FROM memories');
print(f'Engram OK: {cur.fetchone()[0]} memories')
"
```

---

### SPRINT 2: INGESTORS — Poblar el cerebro

---

#### TASK S2-1: Engram ingestor (52 memories → Neo4j + Qdrant)

```
Archivo: /home/ubuntu/sonora-digital-corp/apps/brain/ingestors/engram_ingestor.py
Lee: state/engram.db → tabla memories
Escribe: Neo4j (nodos MEMORY) + Qdrant (vectores)
Verificación: Cuenta nodos MEMORY en Neo4j después de ingestar
```

#### TASK S2-2: Neo4j ingestor (36 existing nodes → Qdrant vectors)

```
Archivo: /home/ubuntu/sonora-digital-corp/apps/brain/ingestors/neo4j_ingestor.py
Lee: Neo4j nodos existentes (Service, Spec, Person, Capability, Achievement, Session)
Escribe: Qdrant (embeddings para búsqueda semántica de nodos existentes)
Verificación: Qdrant colección brain-knowledge tiene ≥36 puntos
```

#### TASK S2-3: Events ingestor (events.jsonl → Neo4j)

```
Archivo: /home/ubuntu/sonora-digital-corp/apps/brain/ingestors/events_ingestor.py
Lee: state/logs/events.jsonl (línea por línea, JSONL)
Escribe: Neo4j nodos EVENT con timestamp, producer, payload
Dedup: mismo event+timestamp+producer = skip
Verificación: Conteo de nodos EVENT en Neo4j
```

#### TASK S2-4: Hermes state ingestor (state.db → Neo4j)

```
Archivo: /home/ubuntu/sonora-digital-corp/apps/brain/ingestors/hermes_ingestor.py
Lee: /home/ubuntu/.hermes/state.db (292MB, SQLite)
Extrae: sesiones recientes (últimas 100), mensajes destacados
Escribe: Neo4j nodos SESSION con resumen
Precaución: state.db es GRANDE (292MB) — solo leer sesiones recientes
Verificación: Nodos SESSION creados en Neo4j
```

#### TASK S2-5: Lecciones ingestor (lecciones.json → Neo4j)

```
Archivo: /home/ubuntu/sonora-digital-corp/apps/brain/ingestors/lecciones_ingestor.py
Lee: products/yami/memory/lecciones.json y cualquier archivo LECCION.md
Escribe: Neo4j nodos LECCION con qué-pasó, qué-salió-bien, qué-salió-mal
Verificación: Nodos LECCION creados
```

#### TASK S2-6: TRUTH ingestor (TRUTH.md sections → Neo4j)

```
Archivo: /home/ubuntu/sonora-digital-corp/apps/brain/ingestors/truth_ingestor.py (NUEVO vs plan original)
Lee: /home/ubuntu/.hermes/memories/TRUTH.md (secciones: Services, MCP, People, Machines)
Escribe: Neo4j nodos SERVICE (cada puerto), PERSON (cada persona), MACHINE
Relaciones: SERVICE → runs_on → MACHINE, PERSON → owns → MACHINE
Verificación: Nodos SERVICE = número de puertos en TRUTH.md
```

---

### SPRINT 3: SYNC + CRON

---

#### TASK S3-1: Create BrainSyncer with full + incremental sync

```
Archivo: /home/ubuntu/sonora-digital-corp/apps/brain/sync.py
Métodos:
  full_sync(): Ejecuta todos los ingestors en orden
  incremental_sync(): Solo cambios desde última sync (usa timestamp)
  status(): Reporta última sync, counts por ingestor
Verificación: python3 -c "from apps.brain.sync import BrainSyncer; print('OK')"
```

#### TASK S3-2: Create brain-sync.sh script

```
Archivo: /home/ubuntu/sonora-digital-corp/scripts/brain-sync.sh
Contenido:
  #!/bin/bash
  cd /home/ubuntu/sonora-digital-corp
  python3 -m apps.brain.sync --mode incremental >> state/logs/brain-sync.log 2>&1
  echo "[$(date)] Brain sync done" >> state/logs/brain-sync.log
Permisos: chmod +x
Verificación: ./scripts/brain-sync.sh → exit 0
```

#### TASK S3-3: Register brain-sync in crontab (every 30 min)

```
Comando:
  ssh ubuntu@149.56.46.173 "(crontab -l 2>/dev/null; echo '*/30 * * * * /home/ubuntu/sonora-digital-corp/scripts/brain-sync.sh') | crontab -"
Verificación: crontab -l | grep brain-sync
```

#### TASK S3-4: Add brain sync to health-monitor.sh

```
Modificar: /home/ubuntu/sonora-digital-corp/scripts/health-monitor.sh
Agregar: healthcheck de BrainService (última sync < 60 min)
Verificación: tail -5 state/logs/health-monitor.log | grep brain
```

---

### SPRINT 4: MCP TOOL — Integración con agentes

---

#### TASK S4-1: Create MCP tool unified_brain_query

```
Archivo: /home/ubuntu/sonora-digital-corp/apps/brain/mcp_tool.py
Tool: unified_brain_query
Args: query (str), type (str optional), mode (auto|semantic|graph|fts), limit (int=10)
Modo auto: semantic → fts → graph (fallback chain)
Returns: list[KnowledgeNode] con score, source, details
Verificación: python3 -c "
from apps.brain.mcp_tool import unified_brain_query;
r = unified_brain_query('Hermes port', mode='auto');
print(f'Resultados: {len(r[\"results\"])}')
"
```

#### TASK S4-2: Register MCP tool in Hermes config.yaml

```
Modificar: /home/ubuntu/.hermes/config.yaml
Agregar MCP server:
  brain:
    command: /usr/bin/python3
    args: [/home/ubuntu/sonora-digital-corp/apps/brain/mcp_tool.py]
    enabled: true
    timeout: 30
Verificación: Hermes recarga config → tool disponible
```

#### TASK S4-3: Test unified_brain_query from Hermes

```
Test: Via Hermes CLI o API, llamar unified_brain_query("Neo4j port")
Expected: Respuesta con "7687" y source "TRUTH.md §Services"
Verificación: Hermes responde con datos correctos
```

---

### SPRINT 5: WEB UI + TESTS

---

#### TASK S5-1: Create Brain Web UI (FastAPI)

```
Archivo: /home/ubuntu/sonora-digital-corp/apps/brain/web.py
Endpoints:
  GET /brain/search?q=<query>&type=<type>&mode=<mode>
  GET /brain/stats (total nodos, tipo counts, última sync, health)
  POST /brain/sync (trigger manual de full sync)
Corre en: mismo proceso que JARVIS Web UI o standalone
Verificación: curl http://localhost:5174/brain/stats → JSON
```

#### TASK S5-2: Create brain dashboard HTML

```
Archivo: /home/ubuntu/sonora-digital-corp/state/brain/dashboard.html
Contenido: stats en vivo, búsqueda, últimas sync, health status
Accesible vía: WAR ROOM (:8080) link
Verificación: Abrir en browser
```

#### TASK S5-3: Create tests

```
Archivo: /home/ubuntu/sonora-digital-corp/tests/brain/test_unified_query.py
Casos:
  1. Query semántica encuentra nodo correcto
  2. Query FTS encuentra por tag
  3. Query grafo encuentra relaciones
  4. Ingestor Engram importa 52 memorias
  5. Sync full no duplica
  6. Dedup fusiona duplicados
Verificación: pytest tests/brain/ -v
```

#### TASK S5-4: Integration test — full cycle

```
Test end-to-end:
  1. BrainSyncer.full_sync()
  2. unified_brain_query("Neo4j port") → "7687"
  3. unified_brain_query("Mystic") → persona correcta
  4. unified_brain_query("load average") → "0.15"
  5. GET /brain/stats → JSON con counts
Verificación: Todos los tests pasan
```

---

## ENTERPRISE SCORE

```
Métrica (10pts c/u)            │ Hoy │ Target │ Delta
───────────────────────────────┼─────┼────────┼──────
1. Revenue Impact              │  4  │   6    │  +2
2. Scalability                 │  8  │   9    │  +1
3. Reusability                 │  7  │   9    │  +2
4. Automation Impact           │  8  │   9    │  +1
5. Knowledge Impact            │  5  │   9    │  +4
6. Reliability                 │  8  │   9    │  +1
7. Founder Independence        │  7  │   9    │  +2
8. Operational Simplicity      │  7  │   8    │  +1
9. Customer Value              │  5  │   7    │  +2
10. FinOps Efficiency          │  8  │   8    │  +0
───────────────────────────────┼─────┼────────┼──────
TOTAL                          │ 67  │  83    │ +16
```

---

## DEPENDENCY GRAPH

```
S1-1 (dirs) ─► S1-2 (config) ─► S1-3 (models) ─► S1-4 (service)
                                                      │
               ┌──────────────────────────────────────┤
               ▼                                      ▼
          S1-5 (Neo4j check)                   S1-6 (Qdrant check)
               │                                      │
               └──────────┬───────────────────────────┘
                          ▼
              ┌────── S2-1 to S2-6 (ingestors) ──────┐
              │  (can run in parallel!)               │
              └────────────────┬──────────────────────┘
                               ▼
                    S3-1 (syncer) ─► S3-2 (script) ─► S3-3 (cron)
                               │
                               ▼
                    S4-1 (MCP tool) ─► S4-2 (register) ─► S4-3 (test)
                               │
                               ▼
                    S5-1 (web) ─► S5-2 (dashboard) ─► S5-3 (tests)
                               │
                               ▼
                         S5-4 (integration test)
```

---

## ARCHIVOS A CREAR/MODIFICAR

```
CREAR (16 archivos):
  apps/brain/__init__.py
  apps/brain/config.py
  apps/brain/models.py
  apps/brain/service.py
  apps/brain/sync.py
  apps/brain/mcp_tool.py
  apps/brain/web.py
  apps/brain/dedup.py
  apps/brain/learning.py
  apps/brain/ingestors/__init__.py
  apps/brain/ingestors/engram_ingestor.py
  apps/brain/ingestors/neo4j_ingestor.py
  apps/brain/ingestors/events_ingestor.py
  apps/brain/ingestors/hermes_ingestor.py
  apps/brain/ingestors/lecciones_ingestor.py
  apps/brain/ingestors/truth_ingestor.py    ← NUEVO vs plan original
  scripts/brain-sync.sh
  state/brain/dashboard.html
  tests/brain/test_unified_query.py

MODIFICAR (3 archivos):
  /home/ubuntu/.hermes/config.yaml (agregar MCP brain server)
  /home/ubuntu/sonora-digital-corp/scripts/health-monitor.sh (agregar brain check)
  crontab (agregar brain-sync cada 30 min)
```

---

## VALIDATION CHECKLIST

```
[ ] S1-1: apps/brain/ directory structure exists on VPS
[ ] S1-2: BrainConfig carga con paths correctos
[ ] S1-3: KnowledgeNode model importa sin error
[ ] S1-4: BrainService conecta a Neo4j, Qdrant, Engram
[ ] S1-5: Neo4j responde con conteo de nodos
[ ] S1-6: Qdrant y Engram accesibles
[ ] S2-1: Engram memories → Neo4j + Qdrant
[ ] S2-2: Neo4j nodos → Qdrant embeddings
[ ] S2-3: Events JSONL → Neo4j EVENT nodos
[ ] S2-4: Hermes state.db → Neo4j SESSION nodos
[ ] S2-5: Lecciones → Neo4j LECCION nodos
[ ] S2-6: TRUTH.md → Neo4j SERVICE + PERSON + MACHINE
[ ] S3-1: BrainSyncer.full_sync() runs without error
[ ] S3-2: brain-sync.sh script executable
[ ] S3-3: Cron registrado cada 30 min
[ ] S3-4: Healthcheck monitorea brain sync
[ ] S4-1: unified_brain_query returns correct results
[ ] S4-2: Hermes config tiene MCP brain server
[ ] S4-3: query desde Hermes funciona
[ ] S5-1: /brain/stats endpoint responde JSON
[ ] S5-2: Dashboard HTML accesible
[ ] S5-3: Tests unitarios pasan
[ ] S5-4: Integration test end-to-end pasa
[ ] LECCION.md: Escrita con aprendizajes
```

---

## RESUMEN

```
SPRINT 1: Foundation   6 tasks  ~45 min  Conexiones a stores + modelo
SPRINT 2: Ingestors    6 tasks  ~60 min  7 ingestores (1 nuevo: truth)
SPRINT 3: Sync + Cron  4 tasks  ~30 min  Syncer + script + crontab
SPRINT 4: MCP Tool     3 tasks  ~30 min  Tool + registro Hermes
SPRINT 5: Web + Tests  4 tasks  ~45 min  UI + dashboard + tests
──────────────────────────────────────────────────────────────
TOTAL:                23 tasks  ~3.5h    Enterprise Score: 67→83
```
