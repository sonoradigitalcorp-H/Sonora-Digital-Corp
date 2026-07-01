# MAPA — Sonora Digital Corp

## ⚠️ REALIDAD ACTUAL

Este repositorio (`~/sdc/`) tiene **1,617 archivos** mezclando:
- El **core** de SDC (lo que hace funcionar la empresa)
- Los **productos** que vendés
- Los **clientes** específicos
- Proyectos **independientes** que no deberían estar acá

---

## 📁 ESTRUCTURA ACTUAL (lo que hay)

```
~/sdc/                          ← EL REPOSITORIO
│
├── CORE (lo que hace funcionar la empresa)
│   ├── sonora-enterprise-os/   ← Constitución, prompts, skills, ADRs (352 archivos)
│   ├── apps/                   ← Aplicaciones
│   │   ├── jarvis/             ←   18 agentes, orquestador, engram (49 archivos)
│   │   ├── webui/              ←   FastAPI frontend puerto :5174 (67 archivos)
│   │   ├── hermes/             ←   MCP bridge, servicios (5 archivos)
│   │   └── voice/              ←   STT/TTS (6 archivos)
│   ├── infra/                  ← Docker, nginx, monitoreo (58 archivos)
│   ├── scripts/                ← DevOps, pipeline, alertas (65 archivos)
│   ├── process/                ← Pipeline de SPECs (34 archivos)
│   └── config/                 ← Configuraciones varias (63 archivos)
│
├── PLATAFORMAS (canales de comunicación)
│   ├── platforms/telegram/     ← Bot Telegram con 98 skills (104 archivos)
│   └── platforms/whatsapp/     ← Bridge WhatsApp (1 archivo)
│
├── PRODUCTOS (lo que vendés)
│   ├── products/abe-music/     ← ABE Music — sellos discográficos (82 archivos)
│   ├── products/azrec/         ← Alejandro Zamora Recording (30 archivos)
│   ├── products/booking/       ← Sistema de reservas (2 archivos)
│   ├── products/chatbot/       ← Chatbot setup (2 archivos)
│   ├── products/landing-artista/ ← Landing page artista (1 archivo)
│   ├── products/telegram-masterclass/ ← Curso Telegram (10 archivos)
│   └── products/yami/          ← Yami — proyecto completo (29 archivos)
│
├── TESTS
│   └── tests/                  ← 442 tests (40 archivos)
│
├── MEMORIA
│   ├── state/                  ← Logs, eventos, engram DB (28 archivos)
│   └── memory/                 ← Lecciones aprendidas (8 archivos)
│
├── RAÍZ (archivos sueltos)
│   ├── opencode.json           ← Config del agente
│   ├── AGENTS.md               ← Referencia rápida
│   ├── CLAUDE.md               ← Protocolo de operación
│   ├── README.md               ← Guía rápida
│   ├── pyproject.toml          ← Config Python
│   ├── requirements.txt        ← Dependencias
│   └── PLAN-OVH-MIGRATION.md   ← Plan de migración (histórico)
│
├── 🚫 NO DEBERÍA ESTAR ACÁ
│   ├── products/mystika/       ← Proyecto completo con Next.js (430 archivos)
│   │                             Dueño: Noel. Tiene su propio repo.
│   └── products/abe-music/studio/ ← ABE Music Studio (proyecto separado)
│
└── 🚫 EXTERNO (otros repos)
    ├── ~/projects/ABE-MUSIC-HUB/ ← Frontend + bot ABE (repo separado)
    └── ~/projects/mds-corp/      ← Otro proyecto
```

---

## 🧠 LO QUE YO (OpenCode) LEO CUANDO HABLAMOS

```
CUANDO VOS DECÍS ALGO → YO LEO:
                        1️⃣ opencode.json (25 agents, 6 instrucciones)
                        2️⃣ OMEGA-PROMPT-v10.0.md (651 líneas)
                        3️⃣ 10-RULES.md (41 líneas)
                        4️⃣ TRUTH.md (253 líneas)
                        5️⃣ SOUL.md (144 líneas)
                        6️⃣ AGENTS.md (96 líneas)
                        7️⃣ CLAUDE.md (22 líneas)
                        8️⃣ Engram DB (240 sesiones anteriores)
                        9️⃣ Archivos que necesite para la tarea
                        🔟 VPS via SSH si hace falta
```

---

## 🔴 PROBLEMAS QUE CAUSAN DESORDEN

| Problema | Dónde | Solución |
|----------|-------|----------|
| `products/mystika/` tiene **430 archivos** (Next.js completo) | ~/sdc/products/mystika/ | Mudar a su propio repo |
| `products/abe-music/studio/` tiene su propio docker-compose | ~/sdc/products/abe-music/studio/ | Separar de products/ |
| 3 repos sueltos fuera de ~/sdc/ | ABE-MUSIC-HUB, mds-corp, yt-dlp | Decidir si van adentro o afuera |
| Archivos en raíz mezclan configs, planes, y presentaciones | PLAN-OVH-MIGRATION.md, presentacion-dia.html, mission-control.html | Mover a docs/ |
| `products/` mezcla PRODUCTOS con CLIENTES | abe-music (cliente?), yami (producto?), mystika (proyecto ajeno?) | Definir categorías claras |

---

## ✅ CÓMO DEBERÍA SER (propuesta de orden)

```
~/sdc/
├── constitution/              ← Reglas, prompts, AGENTS.md
├── core/                      ← apps, infra, scripts (el motor)
├── platforms/                 ← Telegram, WhatsApp (canales)
├── products/                  ← Lo que vendés (abe-music, azrec, etc.)
├── clients/                   ← Proyectos de clientes específicos
├── tests/                     ← Tests
├── memory/                    ← Logs, estado, engram
└── docs/                      ← README, mapas, presentaciones
```

Sin archivos sueltos en la raíz. Sin node_modules de 37,000 archivos. Sin proyectos ajenos.
