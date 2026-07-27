# MAPA — Sonora Digital Corp

## 📁 ESTRUCTURA UNIFICADA

```
~/sdc/                                      ← ÚNICA FUENTE DE VERDAD
│
├── 📜 CONSTITUCIÓN (Capa 0)
│   ├── kernel/            ← OMEGA-PROMPT, SOUL, TRUTH, 10-RULES
│   ├── AGENTS.md                           ← Referencia rápida
│   ├── CLAUDE.md                           ← Protocolo de operación
│   └── opencode.json                        ← Config del agente (25 agents)
│
├── 🧠 CORE (Capa 1-2 — motor + servicios)
│   ├── apps/              ← Servicios core del sistema
│   │   ├── core/          ← Motor principal (engine, planner, agents)
│   │   ├── evolution/     ← Auto-evolución, scorecard, aprendizaje
│   │   ├── hermes/        ← Gateway multi-canal (Telegram, WhatsApp)
│   │   ├── webui/         ← FastAPI frontend (:5174)
│   │   ├── voice/         ← STT/TTS
│   │   ├── frontends/     ← HTML/CSS/JS frontends y landings
│   │   └── ...            ← (collectors, handlers, agents, etc.)
│   ├── infra/             ← Docker, nginx, monitoreo, fleet.yml
│   ├── scripts/           ← DevOps, pipeline, automatización
│   ├── config/            ← Configuraciones, tenants, secrets
│   └── state/             ← Estado vivo: eventos, calidad, engram
│       └── events/        ← Sistema de eventos del core
│
├── 📦 PRODUCTOS (Capa 3 — lo que SDC vende)
│   ├── products/mystika/            ← Educación musical
│   ├── products/clon-digital/       ← Clon digital
│   ├── products/client_api/         ← API para clientes
│   └── products/manager.py          ← Gestor de productos
│
├── 👤 CLIENTES (Capa 4 — implementaciones)
│   ├── clients/abe-music/           ← ABE Music (Abraham)
│   └── clients/azrec/               ← Alejandro Zamora Recording
│
├── 🧪 TESTS Y EVALS
│   ├── tests/                       ← Tests unitarios, BDD, integración
│   └── tests/evals/                 ← Evaluaciones estructurales y promptfoo
│
├── 📚 DOCUMENTACIÓN
│   ├── docs/                        ← Documentación del sistema
│   ├── reference/                   ← Especificaciones cerradas, arqueología
│   └── adrs/                        ← Architecture Decision Records
│
├── 🛠️  OPERACIONES
│   ├── ops/playbooks/               ← Procedimientos estandarizados
│   ├── ops/runbooks/                ← Runbooks de recuperación
│   ├── process/                     ← Pipeline de SPECs activos/completados
│   ├── backups/                     ← Backups diarios
│   └── portal/                      ← Grimoire 3D (Three.js galaxy)
│
└── ⚙️  RAÍZ (solo archivos esenciales)
    ├── opencode.json
    ├── AGENTS.md
    ├── CLAUDE.md
    ├── README.md
    ├── Makefile
    ├── pyproject.toml
    └── requirements.txt
```

## 🧠 CÓMO TRABAJA EL AGENTE

Cuando hablás conmigo, yo LEO estas fuentes EN ESTE ORDEN:

```
1️⃣ opencode.json           → 25 agents, permisos, comandos
2️⃣ OMEGA-PROMPT-v10.0.md   → Constitución operativa (VDD→TDD)
3️⃣ 10-RULES.md             → 10 reglas absolutas
4️⃣ TRUTH.md                → Paths, VPS, servicios
5️⃣ SOUL.md                 → 5 elementos
6️⃣ AGENTS.md               → Referencia rápida
7️⃣ CLAUDE.md               → Protocolo (siempre desde ~/sdc/)
8️⃣ MAPA-SDC.md             → Este mapa de estructura
9️⃣ Engram                  → Memoria de sesiones anteriores (240+)
🔟 Archivos que necesite    → Código, configs, logs
```

## ✅ REGLAS DE ORO

1. **Siempre trabajamos desde `~/sdc/`** — el alias `sdc` te lleva ahí
2. **Tres categorías**: CORE (lo que hace funcionar SDC) + PRODUCTS (lo que vendés) + CLIENTS (implementaciones para clientes)
3. **Cero archivos sueltos en la raíz** — solo `opencode.json`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `pyproject.toml`, `requirements.txt`
4. **Cero proyectos ajenos** — lo que no es de SDC, no está acá
5. **Cada cosa en su lugar** — si no sabés dónde va, preguntame

## 🔄 ÚLTIMA ACTUALIZACIÓN

2026-06-30 — Reestructuración completa. Todo unificado bajo ~/sdc/.
