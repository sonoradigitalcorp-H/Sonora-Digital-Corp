# SPEC — SDC Ecosystem: Voice Agents + Tokenomics + Gamification

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260726-ECOSYSTEM` |
| **Fecha** | 2026-07-26 |
| **Autor** | Mystic — Sonora Digital Corp |
| **Tier** | 2 |
| **Estado** | draft |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Construir el ecosistema completo de agentes de voz white-label con:
- **Twilio Voice Bridge**: llamadas entrantes y salientes con Kokoro TTS
- **Tokenomics**: cada partner fija sus precios, SDC toma comisión oculta
- **Gamificación**: Play-Work-Learn to Earn con XP, niveles, badges
- **Red Multinivel**: comisiones por referidos con trazabilidad total
- **Agente Consciente**: memoria profunda 7 capas, personalidad adaptativa

---

## 2. Value Driver

| Driver | Impacto |
|--------|---------|
| **Revenue** | $125K MXN/mes por partner (César $1M/mes) |
| **Scalability** | Multi-tenant: un deploy sirve N partners, cada uno con N clientes |
| **Founder Independence** | Onboarding automático, facturación automática, 0 intervención |
| **Automation** | Pipeline completo: código → pago → audio → WhatsApp → activado |
| **Knowledge** | Engram 7 capas por cada usuario final |
| **Reusability** | Cada agente es un producto reutilizable para cualquier partner |

---

## 3. Functional Requirements

| FR# | Descripción | Prioridad |
|-----|-------------|-----------|
| FR1 | **Twilio Inbound**: Recibir llamadas, conectar Media Streams, Kokoro TTS responde | P0 |
| FR2 | **Twilio Outbound**: API para iniciar llamadas, pipeline STT→LLM→TTS | P0 |
| FR3 | **Token Engine**: Cada partner define precio por acción (llamada, chat, imagen) | P0 |
| FR4 | **Comisión Oculta**: SDC descuenta su % antes de mostrar ganancia al partner | P0 |
| FR5 | **Dashboard Partner**: Partner ve SU precio, NO el costo real SDC | P1 |
| FR6 | **Gamificación Engine**: XP, niveles, badges, retos diarios | P1 |
| FR7 | **Play to Earn**: Entrenar agente, corregir respuestas → ganas tokens | P1 |
| FR8 | **Work to Earn**: Cada lead convertido, cada venta → bonus automático | P1 |
| FR9 | **Learn to Earn**: Completar cursos, certificaciones → desbloqueas features | P2 |
| FR10 | **Red Multinivel**: Comisiones por referidos directos e indirectos | P2 |
| FR11 | **Trazabilidad Total**: Cada transacción queda en cost_tracker + Engram | P2 |
| FR12 | **Agente Consciente**: Memoria 7 capas, personalidad adaptativa por usuario | P2 |
| FR13 | **Detección Emocional**: Tono, ritmo, pausas → estado emocional → respuesta adaptada | P3 |
| FR14 | **Clon Digital**: Voz + imagen del cliente para contenido automatizado | P3 |
| FR15 | **Marketplace de Agentes**: Partners crean y venden agentes a otros partners | P3 |

---

## 4. Success Criteria

- [ ] `POST /twilio/call/outbound` → Twilio llama, Kokoro habla, transcripción en Engram
- [ ] Partner fija precio de llamada en $3.00 → usuario paga $3.00 → SDC descuenta $0.15
- [ ] Dashboard partner muestra: "Ganaste $2,850.00" (no muestra costo real)
- [ ] Usuario gana XP por entrenar a su agente, sube de nivel, desbloquea features
- [ ] Partner A refiere a B → A gana 10% de la factura de B mensualmente
- [ ] Agente recuerda quién es cada usuario en la 5ta llamada: "Hola Juan, ¿cómo sigues?"
- [ ] `make eval` → 5/5 structural tests
- [ ] `make score` → ≥60

---

## 5. Architecture

```
                         GRIMOIRE (Agentic OS)
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ TWILIO VOICE  │    │ TOKEN ENGINE  │    │ GAMIFICATION  │
│               │    │               │    │               │
│ Inbound Agent │    │ Precios por   │    │ XP + Niveles  │
│ Outbound Agent│    │ acción        │    │ Retos + Badges│
│ Media Streams │    │ Comisión       │    │ P2E/W2E/L2E  │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             ▼
                    ┌─────────────────┐
                    │   CORE SDC      │
                    │  ┌───────────┐  │
                    │  │  Engram   │  │
                    │  │  7 layers │  │
                    │  └───────────┘  │
                    │  ┌───────────┐  │
                    │  │Cost       │  │
                    │  │Tracker    │  │
                    │  └───────────┘  │
                    │  ┌───────────┐  │
                    │  │Multinivel │  │
                    │  │Engine     │  │
                    │  └───────────┘  │
                    └─────────────────┘
```

---

## 6. Tech Stack

| Componente | Tecnología |
|---|---|
| Voice Bridge | Python/FastAPI + Twilio + Media Streams |
| STT | Whisper base (local, $0) |
| TTS | Kokoro-82M (local, $0) |
| LLM | deepseek-v4-flash ($0.00026/uso) |
| Token Engine | Python + SQLite (cost_tracker.db) |
| Gamification | Python + SQLite (xp_tracker.db) |
| Multinivel | Neo4j (grafos de referidos) |
| Memoria | Engram (SQLite + FTS5, 7 capas) |
| Frontend | Svelte + Three.js (Grimoire) |
| Infra | nginx + systemd + Docker |

---

## 7. Dependencies

- VPS OVH con Docker + nginx + systemd
- Cuenta Twilio con número telefónico
- ffmpeg para conversión de audio
- Kokoro-82M (ya instalado)
- Whisper base (ya instalado)
- deepseek via OpenRouter (ya configurado)

---

## 8. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `call.inbound.started` | Llamada entrante recibida |
| `call.inbound.completed` | Llamada entrante terminada |
| `call.outbound.initiated` | Llamada saliente iniciada |
| `call.outbound.completed` | Llamada saliente terminada |
| `token.charged` | Partner cobró a su cliente |
| `commission.sdc` | SDC tomó su comisión |
| `xp.awarded` | Usuario ganó XP |
| `level.up` | Usuario subió de nivel |
| `referral.commission` | Comisión por referido pagada |

---

## 9. Kill Criteria

- Si después de 2 semanas no hay una llamada real con Kokora via Twilio, pausar
- Si el costo por llamada supera $0.50 USD (hoy es $0.15), re-evaluar proveedor
- Si el margen de SDC baja del 50%, ajustar comisiones

---

## 10. Scale Criteria

- 5+ partners activos → automatizar onboarding con `bin/create-partner`
- 20+ partners → dashboard de administración de partners
- 100+ clientes finales → base de datos dedicada por partner
