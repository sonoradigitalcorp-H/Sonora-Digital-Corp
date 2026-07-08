# MAPA — Sonora Digital Corp

## 📁 ESTRUCTURA UNIFICADA

```
~/sdc/                                      ← ÚNICA FUENTE DE VERDAD
│
├── 📜 CONSTITUCIÓN
│   ├── constitution/  ← OMEGA-PROMPT, 10-RULES, TRUTH, SOUL
│   ├── AGENTS.md                           ← Referencia rápida
│   ├── CLAUDE.md                           ← Protocolo de operación
│   └── opencode.json                        ← Config del agente (25 agents, 6 instrucciones)
│
├── 🧠 CORE (el motor de la empresa)
│   ├── apps/jarvis/                        ← 18 agentes, orquestador, engram
│   ├── apps/webui/                         ← FastAPI frontend (:5174)
│   ├── apps/hermes/                        ← MCP bridge
│   ├── apps/voice/                         ← STT/TTS
│   ├── infra/                              ← Docker, nginx, monitoreo
│   ├── scripts/                            ← DevOps, pipeline, alertas
│   └── config/                             ← Configuraciones
│
├── 🤖 PLATAFORMAS (canales de comunicación)
│   ├── platforms/telegram/                 ← Bot Telegram (98 skills)
│   └── platforms/whatsapp/                 ← Bridge WhatsApp
│
├── 📦 PRODUCTOS (lo que SDC vende)
│   ├── products/mystika/                   ← Plataforma educación musical + NSFW
│   ├── products/yami/                      ← Yami (Mystic + Noel)
│   ├── products/telegram-masterclass/      ← Curso Telegram
│   ├── products/booking/                   ← Sistema de reservas
│   ├── products/chatbot/                   ← Chatbot setup
│   └── products/landing-artista/           ← Landing page genérica
│
├── 👤 CLIENTES (implementaciones específicas)
│   ├── clients/abe-music/                  ← ABE Music (Abraham)
│   └── clients/azrec/                      ← Alejandro Zamora Recording
│
├── 🧪 TESTS
│   └── tests/                              ← 442 tests
│
├── 📊 MEMORIA
│   ├── state/                              ← Logs, eventos, engram DB
│   ├── memory/                             ← Lecciones aprendidas
│   └── process/                            ← Pipeline de SPECs (7 completados)
│
├── 📚 DOCUMENTACIÓN
│   ├── README.md                           ← Guía rápida
│   ├── MAPA-SDC.md                         ← Este archivo
│   ├── mission-control.html                ← Dashboard vivo
│   └── presentations/                      ← Presentaciones HTML
│
└── ⚙️  RAÍZ (solo archivos esenciales)
    ├── opencode.json
    ├── AGENTS.md
    ├── CLAUDE.md
    ├── README.md
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
