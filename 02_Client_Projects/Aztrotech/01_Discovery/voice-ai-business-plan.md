# Aztrotech Voice AI — Plan Estratégico Agosto-Diciembre 2026

## 1. Pack de Agentes de Voz por Nicho

### Nichos objetivo (Hermosillo, Sonora)

| Nicho | Agente de Voz | Skills | Prioridad |
|-------|--------------|--------|-----------|
| 🏪 Tiendas/Ropa | **Sofía** — recepcionista + ventas | catálogo, horarios, promociones, ubicación | 🔴 Mes 1 |
| 🍽️ Restaurantes | **María** — toma pedidos + reservas | menú, reservas, domicilio, horarios | 🔴 Mes 1 |
| 🦷 Clínicas Dentales | **Dra. Carmen** — agenda + info | servicios, cotizaciones, emergencias, recordatorios | 🟡 Mes 2 |
| 🏥 Consultorios Médicos | **Enfermera Laura** — triage + citas | síntomas, agenda, recetas, seguros | 🟡 Mes 2 |
| 💈 Barberías/Salones | **Valentina** — citas + productos | agenda, precios, productos, reseñas | 🟡 Mes 2-3 |
| ☕ Cafés | **Barista AI** — pedidos + eventos | menú, eventos, pedidos anticipados, fidelidad | 🟢 Mes 3 |
| 🏢 Agencias/Consultoras | **Ejecutiva** — captura leads | servicios, cotización, agendar call con dueño | 🟢 Mes 3-4 |

### Arquitectura de cada agente
```
FreeSWITCH (SIP) → faster-whisper (STT) → DeepSeek V4 (LLM) + RAG (Qdrant) → edge-tts (TTS) → FreeSWITCH
                      ↑ identidad + memoria + lead scoring + emotion (Engram + Postgres)
```
Sin ElevenLabs, sin Twilio: edge-tts (gratis) + faster-whisper (local) + FreeSWITCH (SIP trunk Telnyx ~$1/mes x número).

---

## 2. Campañas Agosto-Diciembre

### Entregables por mes

| Mes | Campaña | Entregable | Métrica | ROI Esperado |
|-----|---------|-----------|---------|-------------|
| **Ago** | ✅ Inbound Voice (web + Telegram) | 1 agente inbound funcional + grabación clon voz César 30s | 100 llamadas/mes | $299 MXN (1 Despertar) |
| **Sep** | 🚀 Outbound Warm Leads | 2 agentes outbound + campaña fríos/warm (WhatsApp → llamada) | 500 llamadas/mes, 20% conversión | $1,499 MXN (1 Elevar) |
| **Oct** | 📢 Campaña Restaurantes HMO | Agente María + scraper Google Business para 50 restaurantes | 1000 llamadas, 15 leads calificados | $5,000 MXN (3 Despertar) |
| **Nov** | 🎄 Campaña Buen Fin | Agente promocional + recordatorios WhatsApp para 20 clientes | 2000 llamadas, 30% más ventas | $7,500 MXN (5 Despertar) |
| **Dic** | 🎉 Cierre de año + renovaciones | Campaña fidelidad + upsell a Elevar para clientes activos | 3000 llamadas, 10 upgrades | $15,000 MXN (10 Despertar + 1 Elevar) |

### Proyección acumulada
```
Agosto:     1 cliente   =     $299 MXN
Septiembre: 3 clientes  =   $2,097 MXN
Octubre:    6 clientes  =   $7,097 MXN
Noviembre: 11 clientes  =  $14,597 MXN
Diciembre:  16 clientes  =  $30,000+ MXN
```

---

## 3. Costo Real Aztrotech (Tokens + Infra)

### Stack actual (lo que YA corre)

| Componente | Costo/mes | Notas |
|-----------|-----------|-------|
| VPS OVH (149.56.46.173) | $50 USD | 9 contenedores: PG, Redis, Neo4j, Qdrant, n8n, Hermes, OpenClaw, MCP, Langfuse |
| OpenRouter DeepSeek V4 Flash | ~$0.14/1M tokens | ~$0.35/mes por cliente Despertar (100 llamadas) |
| OpenRouter GLM-5.2 (razonamiento) | ~$0.50/1M tokens | ~$0.05/mes (15% del tráfico) |
| edge-tts (TTS) | $0 | Gratis, Microsoft Edge API |
| faster-whisper (STT) | $0 | Local, CPU |
| Ollama embeddings | $0 | Local, VPS |
| FreeSWITCH SIP trunk (Telnyx) | ~$1/número/mes | Sin Twilio |
| Números virtuales DID | ~$5 c/u/mes | Telnyx |
| **Total fijo** | **~$56 USD/mes** | |
| **Total variable por cliente Despertar** | **~$0.40 USD/mes** | 100 llamadas, ~2000 tokens c/u |
| **Total variable por cliente Elevar** | **~$2.00 USD/mes** | 500 llamadas, ~2000 tokens c/u |
| **Total variable por cliente Soberano** | **~$10 USD/mes** | 2000+ llamadas |

### Costo de Aztrotech para César (como cliente interno)
```
Costo fijo (infra + VPS):     $56 USD/mes  ← compartido entre todos los tenants
Costo tokens César:           ~$2 USD/mes  ← ~500 llamadas inbound + pruebas
Costo Telnyx (1 número DID):  $6 USD/mes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Costo real Aztrotech:         ~$64 USD/mes (~$1,088 MXN)
```

---

## 4. Tres Paquetes para César y sus Clientes

### Paquete A — "Despertar" (para clientes pequeños)
| Item | Precio MXN | Costo Real | Margen |
|------|-----------|-----------|--------|
| Agente IA 1 canal (WA o TG) | $299/mes | $5 USD ($85 MXN) | **71%** |
| Setup + clon voz 30s | $499 única vez | $0 | 100% |
| Campaña outbound simple | $199 extra/mes | $2 USD | **96%** |
| **Total primer mes** | **$798 MXN** | **$85 MXN** | |

### Paquete B — "Elevar" (para clientes medianos)
| Item | Precio MXN | Costo Real | Margen |
|------|-----------|-----------|--------|
| 3 agentes IA multi-canal | $1,499/mes | $25 USD ($425 MXN) | **71%** |
| CRM + scoring leads | incluido | $0 | - |
| Campañas outbound (10/mes) | $499 extra/mes | $5 USD | **98%** |
| Fabrica contenido 30 piezas | $299 extra/mes | $1 USD | **99%** |
| **Total primer mes** | **$2,297 MXN** | **$430 MXN** | |

### Paquete C — "Soberano Esencial" (para clientes grandes)
| Item | Precio MXN | Costo Real | Margen |
|------|-----------|-----------|--------|
| Agentes ilimitados + canales | $3,999/mes | $50 USD ($850 MXN) | **78%** |
| Dashboard 3D + white-label | $1,000 extra/mes | $0 | 100% |
| Campañas outbound ilimitadas | $1,000 extra/mes | $10 USD | **98%** |
| API dedicada + SDK | incluido | $0 | - |
| Account Manager | incluido | $0 | - |
| **Total primer mes** | **$5,999 MXN** | **$860 MXN** | |

---

## 5. Outbound: FreeSWITCH + Skills Propias (sin Twilio/ElevenLabs)

### Pipeline outbound
```
Campaña (n8n + Postgres) → FreeSWITCH (SIP Telnyx) → Llamada → 
  → faster-whisper (STT) → agente especialista (DeepSeek) → 
  → edge-tts (TTS) → FreeSWITCH → transcripción → lead scoring → notificación WhatsApp César
```

### Skills propias de voz (evita ElevenLabs)
| Skill | Qué hace | Costo |
|-------|---------|-------|
| edge-tts | TTS natural español (Microsoft) | $0 |
| Qwen3-TTS | Clon de voz César (local) | $0 (ya listo) |
| faster-whisper | STT local (small, es, int8) | $0 |
| emotion_analyzer.py | Detección de tono/urgencia | $0 |
| lead_classifier.py | Scoring BANT automático | $0 |
| emerge_memory.py | Memoria por cliente recurrente | $0 |

### Costo outbound real por llamada
```
SIP trunk (Telnyx): ~$0.013/min (entrada/salida)
STT (whisper):      $0 (local)
LLM (DeepSeek):     ~$0.00014/llamada (200 tokens)
TTS (edge-tts):     $0 (local)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Costo por llamada:  ~$0.013 USD  (menos de 1 centavo del stack IA)
```

---

## 6. Resumen Ejecutivo

| Concepto | Valor |
|----------|-------|
| **Inversión inicial César** | $0 (ya tiene todo funcionando) |
| **Costo fijo mensual Aztrotech** | ~$64 USD / $1,088 MXN |
| **Proyección ingresos Dic 2026** | $30,000+ MXN/mes (16 clientes) |
| **Margen promedio** | 70-98% |
| **Costo por llamada** | $0.013 USD |
| **Diferenciador** | Sin Twilio, sin ElevenLabs, sin dependencias caras |
| **Stack que lo hace posible** | edge-tts + faster-whisper + DeepSeek + FreeSWITCH + Telnyx |

*Creado para César Holguín — AstroTech / Sonora Digital Corp — Agosto 2026*