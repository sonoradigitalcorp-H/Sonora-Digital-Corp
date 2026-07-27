# Propuesta Comercial — Sonora Digital Corp × Aztrotech

**Fecha:** 2026-07-27 · **Para:** Cesar (Aztrotech)  
**Desde:** Abraham "Perroni" / Mystic — Sonora Digital Corp

---

## 📊 Costos por Interacción (Tecnología Base)

### Pipeline de Audio (Voz en Tiempo Real)

```
Usuario habla → Whisper STT (local) → LLM (deepseek) → Kokoro TTS (local) → Audio
```

| Componente | Tecnología | Ubicación | Costo por uso |
|------------|-----------|-----------|--------------|
| STT (voz a texto) | Whisper base | VPS local | **$0.00** |
| LLM (razonamiento) | deepseek-v4-flash | Cloud OpenRouter | **$0.0004** (~500 tokens) |
| TTS (texto a voz) | Kokoro 82M | VPS local | **$0.00** |
| **Total interacción audio 2min** | | | **~$0.0004** |

### Llamadas Telefónicas (Inbound/Outbound)

| Vía | Costo/minuto | Procesamiento IA | Total llamada 2min |
|-----|-------------|-----------------|-------------------|
| **Twilio** (cloud) | $0.014/min MX | $0.0004 | **~$0.028** |
| **FreeSWITCH + Telnyx** (propio) | $0.003/min MX | $0.0004 | **~$0.006** |

### Mensajería Telegram

| Componente | Costo |
|------------|-------|
| Mensaje texto | **$0.00** (API gratuita) |
| Mensaje con IA (generación) | **$0.0002** |
| Audio/ multimedia | **$0.0004** |

> 💡 **El VPS corre 24/7 a $15/mes fijo — mientras más interacciones, más barato el costo unitario.**

---

## 🎯 Pack 1: Call Agent — Agente de Llamadas

### Inbound Agent (Recibe llamadas)

```
Cliente llama → Twilio/Telnyx → Whisper STT → Mystic IA → Kokoro TTS → Responde
```

**Capacidades:**
- Atiende llamadas entrantes 24/7
- Entiende contexto del cliente (memoria a largo plazo)
- Resuelve dudas, agenda citas, califica leads
- Transfiere a humano si es necesario
- Graba y transcribe cada llamada

**Stack técnico:**
- Twilio (inbound) o FreeSWITCH + Telnyx
- Whisper STT (local) → deepseek-v4-flash → Kokoro TTS (local)
- Memoria persistente (Engram)

### Outbound Agent (Hace llamadas)

```
Mystic detecta lead → Genera guión → Kokoro TTS → Twilio → Llama al lead
```

**Capacidades:**
- Campaigns automáticas de llamadas salientes
- Calentamiento de leads con guión dinámico
- Voicemail detection + leave message
- Callback scheduling
- Reporte de resultados por campaña

### KPIs del Call Agent

| KPI | Target | Medición |
|-----|--------|----------|
| Tasa de conversación completada | >85% | Llamadas completadas / intentadas |
| Tiempo promedio de atención | <3 min | Por llamada |
| Satisfacción (encuesta post-llamada) | >4.0/5 | NPS integrado |
| Tasa de transferencia a humano | <20% | Transferencias / total llamadas |
| Costo por lead calificado | <$0.50 | Gasto total / leads calificados |
| ROI | >300% | (Ventas generadas - costo) / costo |

### Precios Call Agent

| Plan | Llamadas/mes | Incluye | Precio |
|------|-------------|---------|--------|
| **Starter** | 500 min | Inbound + Outbound, 1 número | **$299/mes** |
| **Business** | 2,000 min | + 3 números, campañas, analytics | **$799/mes** |
| **Enterprise** | Ilimitado | + Números ilimitados, SIP trunk, SLA | **$1,999/mes** |

---

## 📱 Pack 2: Marketing Agent — Agente de Contenido Telegram

```
Plan editorial → Mystic genera contenido → Diseña asset → Publica en Telegram → Mide ROI
```

**Capacidades:**
- Genera contenido diario para canales Telegram (texto, imágenes, audio)
- Programa publicaciones según audiencia
- Responde preguntas de seguidores automáticamente
- Segmenta audiencia por interés/ comportamiento
- Escala a múltiples canales simultáneamente

**Tipos de contenido:**
- Posts educativos / promocionales
- Audio-resúmenes (voz Mystic)
- Infografías generadas por IA
- Encuestas interactivas
- Respuestas automáticas a comentarios

### KPIs del Marketing Agent

| KPI | Target | Medición |
|-----|--------|----------|
| Engagement rate | >15% | reacciones + comentarios / alcance |
| Crecimiento semanal de suscriptores | >5% | Nuevos / total |
| Tasa de apertura de contenido | >60% | Vistos / enviados |
| Leads generados por campaña | >10 | Registros / campaña |
| Costo por lead (CPL) | <$0.10 | Gasto / leads |
| ROI | >500% | (Clientes × LTV) / costo campaña |
| Retención de audiencia | >70% | Activos después 30 días |

### Precios Marketing Agent

| Plan | Canales | Contenido/mes | Precio |
|------|---------|---------------|--------|
| **Starter** | 1 canal | 30 posts + respuestas auto | **$199/mes** |
| **Business** | 3 canales | 90 posts + audio + imágenes | **$499/mes** |
| **Enterprise** | 10 canales | Ilimitado + campañas segmentadas | **$1,299/mes** |

---

## 🚀 Pack 3: Full Agent Suite (Call + Marketing + Analytics)

Todo incluido + dashboard unificado + analytics cross-channel.

| Componente | Incluye |
|-----------|---------|
| Call Agent Inbound | ✅ Ilimitado |
| Call Agent Outbound | ✅ Ilimitado |
| Marketing Agent | ✅ 10 canales |
| Dashboard Tiempo Real | ✅ Métricas unificadas |
| API Personalizada | ✅ Integración con sistemas existentes |
| SLA 99.9% | ✅ Garantía de disponibilidad |
| Soporte Dedicado | ✅ Canal directo con equipo SDC |

**Precio:** **$2,499/mes** (ahorro 33% vs paquetes por separado)

---

## 📈 ROI Proyectado (Escenario Cliente Tipo)

| Concepto | Sin agentes | Con agentes SDC | Mejora |
|----------|------------|-----------------|--------|
| Llamadas atendidas/mes | 200 | 2,000 | 10x |
| Tiempo respuesta promedio | 4 hrs | 30 seg | 99.8% más rápido |
| Leads generados/mes | 15 | 120 | 8x |
| Costo por lead | $15 USD | ~$0.30 USD | 98% menos |
| Contenido publicado/mes | 8 posts | 90+ posts | 11x |
| Engagement rate | 5% | 15%+ | 3x |
| **Ingreso mensual estimado** | **$3,000** | **$12,000+** | **4x** |

---

## ⚙️ Infraestructura Técnica

```
                    ┌─────────────┐
                    │   VPS OVH   │
                    │  $15/mes    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │ Whisper  │ │  Kokoro  │ │  Engram  │
       │ STT      │ │  TTS     │ │ Memoria  │
       │ (local)  │ │ (local)  │ │ (local)  │
       └──────────┘ └──────────┘ └──────────┘
              │            │            │
              └────────────┼────────────┘
                           ▼
                    ┌──────────────┐
                    │  deepseek    │
                    │ v4-flash     │
                    │ (OpenRouter) │
                    │ $0.0002/1k i │
                    │ $0.0008/1k o │
                    └──────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │ Twilio   │ │ Telnyx   │ │ Telegram │
       │ Telephony│ │ SIP      │ │ API      │
       │ $0.014/m │ │ $0.003/m │ │ FREE     │
       └──────────┘ └──────────┘ └──────────┘
```

---

## 🎁 Propuesta de Colaboración (Aztrotech como Partner)

Como Aztrotech es **partner estratégico**, propongo:

| Concepto | Partner Price | Retail Price |
|----------|-------------|--------------|
| Setup inicial | **$499** (50% descuento) | $999 |
| Call Agent Starter | **$199/mes** | $299/mes |
| Marketing Agent Starter | **$129/mes** | $199/mes |
| Full Suite | **$1,799/mes** | $2,499/mes |
| Revenue Share | **10%** sobre ventas referidas | — |

---

*Propuesta generada por Mystic (SDC Orchestrator) — 2026-07-26*  
*Tecnología: Whisper STT + deepseek-v4-flash + Kokoro TTS + Twilio/FreeSWITCH + Engram Memory*
