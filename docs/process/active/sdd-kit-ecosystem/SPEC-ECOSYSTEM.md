# SPEC — SDC Ecosystem Platform v3.0

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-SDC-ECOSYSTEM-V3` |
| **Fecha** | 2026-07-26 |
| **Autor** | Mystic — Sonora Digital Corp |
| **Tier** | 2 |
| **Estado** | active |
| **Score requerido** | ≥60 |
| **Score actual** | 65 ✅ |

---

## 1. Objetivo

Construir la plataforma de agentes IA white-label multi-tenant con:
- Voz telefónica via FreeSWITCH + SIP Trunk (80% más barato que Twilio)
- Tokenomics: cada partner fija sus precios, SDC toma comisión oculta
- Gamificación: Play-Work-Learn to Earn para retención de usuarios
- Red Multinivel: comisiones por referidos con trazabilidad total
- Agente Consciente: memoria 7 capas, personalidad adaptativa por usuario

---

## 2. Value Drivers

| Driver | Impacto |
|--------|---------|
| **Revenue** | $125K MXN/mes por partner como César ($1M facturación) |
| **Scalability** | Multi-tenant: 1 deploy = N partners = N×M clientes |
| **Founder Independence** | Onboarding automático, facturación automática, 0 intervención humana |
| **Automation** | Pipeline: código → pago → audio → WhatsApp → activado |
| **Knowledge** | Engram 7 capas por cada usuario final |
| **Reusability** | Cada agente es producto reutilizable para cualquier partner |

---

## 3. Functional Requirements

| FR# | Descripción | Prioridad | Estado |
|-----|-------------|-----------|--------|
| FR1 | FreeSWITCH recibe llamadas entrantes y las pasa al pipeline IA | P0 | 🚧 |
| FR2 | FreeSWITCH inicia llamadas salientes a leads desde n8n | P0 | 🚧 |
| FR3 | Whisper STT transcribe audio de llamadas en tiempo real | P0 | ✅ |
| FR4 | deepseek genera respuestas contextuales | P0 | ✅ |
| FR5 | Kokoro TTS sintetiza respuestas con voz natural española | P0 | ✅ |
| FR6 | Token Engine: partners definen precio por acción | P0 | 🚧 |
| FR7 | Comisión SDC oculta: se deduce antes de mostrar ganancia al partner | P0 | 🚧 |
| FR8 | Dashboard partner muestra solo su precio, no costos reales SDC | P1 | 🚧 |
| FR9 | Gamificación: XP, niveles, badges por acciones | P1 | 🚧 |
| FR10 | Play to Earn: entrenar agente → ganas tokens | P1 | 🚧 |
| FR11 | Work to Earn: ventas → bonus automáticos | P1 | 🚧 |
| FR12 | Learn to Earn: cursos → desbloqueos | P2 | 🚧 |
| FR13 | Red Multinivel: comisiones por referidos directos e indirectos | P2 | 🚧 |
| FR14 | Trazabilidad total en cost_tracker + Engram | P2 | ✅ |
| FR15 | Agente consciente: memoria 7 capas por usuario | P2 | ✅ |
| FR16 | Personalidad adaptativa según tono/estilo del usuario | P3 | 🚧 |
| FR17 | Clon digital: voz + imagen para contenido automatizado | P3 | 🚧 |

---

## 4. Architecture

```
                          GRIMOIRE (Agentic OS)
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ FREESWITCH    │     │ TOKEN ENGINE  │     │ GAMIFICATION  │
│ (PBX)         │     │               │     │               │
│               │     │ Precios por   │     │ XP + Niveles  │
│ Inbound Agent │     │ acción        │     │ Retos + Badges│
│ Outbound Agent│     │ Comisión       │     │ P2E/W2E/L2E  │
│ SIP Trunk     │     │ oculta        │     │               │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │   CORE SDC       │
                     │ ┌──────────────┐ │
                     │ │ Kokoro TTS   │ │
                     │ │ Whisper STT  │ │
                     │ │ deepseek LLM │ │
                     │ │ Engram 7 cap │ │
                     │ │ cost_tracker │ │
                     │ └──────────────┘ │
                     └──────────────────┘
```

---

## 5. Tech Stack

| Componente | Tecnología | Costo |
|------------|------------|-------|
| PBX | FreeSWITCH (Docker) | $0 |
| SIP Trunk | Telnyx / VoIP.ms | $0.003/min |
| STT | Whisper base (local) | $0 |
| TTS | Kokoro-82M (local) | $0 |
| LLM | deepseek-v4-flash (OpenRouter) | $0.00026/uso |
| Memoria | Engram (SQLite + FTS5) | $0 |
| Costos | cost_tracker.db (SQLite) | $0 |
| Dashboard | Svelte + Three.js (Grimoire) | $0 |
| Infra | VPS OVH (ya pagas) | $16/mes |

---

## 6. Success Criteria

- [ ] `docker run freeswitch` → extensión interna funciona
- [ ] `fs_cli -x "originate..."` → llamada sale a celular real
- [ ] Whisper + deepseek + Kokoro responden en llamada < 2s
- [ ] Partner fija precio de llamada en $3.00 → cliente paga $3.00 → SDC descuenta
- [ ] Dashboard partner muestra: "Ganaste $2,850.00" (no costo real SDC)
- [ ] Usuario gana XP por entrenar agente → sube nivel → desbloquea features
- [ ] Partner A refiere a B → A gana 10% de factura de B
- [ ] Agente dice "Hola Juan, ¿cómo sigues?" en 5ta llamada (memoria)
- [ ] `make eval` → all pass
- [ ] `make score` ≥ 60

---

## 7. Events

| Evento | Trigger |
|--------|--------|
| `call.inbound.started` | Llamada entrante conectada |
| `call.inbound.completed` | Llamada entrante terminada |
| `call.outbound.initiated` | Llamada saliente iniciada |
| `call.outbound.completed` | Llamada saliente terminada |
| `token.charged` | Partner cobró a su cliente |
| `commission.sdc` | SDC tomó su comisión |
| `xp.awarded` | Usuario ganó XP |
| `level.up` | Usuario subió de nivel |
| `referral.commission` | Comisión por referido pagada |

---

## 8. Dependencies

- VPS OVH con Docker (✅)
- FreeSWITCH image (⬜ por instalar)
- SIP Trunk (Telnyx) (⬜ por contratar, ~$10)
- Kokoro TTS (✅ instalado)
- Whisper STT (✅ instalado)
- deepseek via OpenRouter (✅ configurado)
- Engram (✅ listo)
- cost_tracker.db (✅ inicializado)
- Grimoire 3D (✅ construido)

---

## 9. Kill Criteria

- Si después de 2 semanas no hay llamada real con Kokoro, pausar
- Si costo/minuto > $0.01, re-evaluar SIP Trunk
- Si margen SDC < 50%, ajustar comisiones

---

## 10. Scale Criteria

- 5+ partners → `bin/create-partner` automatizado
- 20+ partners → Dashboard admin de partners
- 100+ clientes finales → DB dedicada por partner
