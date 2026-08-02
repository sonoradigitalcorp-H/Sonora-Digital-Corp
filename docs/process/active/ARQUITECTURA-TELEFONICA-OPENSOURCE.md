# Arquitectura Telefónica Open Source — SDC

## Conclusión: No necesitamos Twilio

Twilio es caro ($0.013/min MX) y nos hace dependientes.
Podemos usar **FreeSWITCH** + **SIP Trunk barato** por ~$0.003/min.

---

## Lo que YA tenemos (y funciona)

```
✅ Kokoro TTS        → Síntesis de voz (local, $0)
✅ Whisper STT       → Transcripción (local, $0)
✅ deepseek LLM      → Razonamiento ($0.00026/uso)
✅ Engram            → Memoria 7 capas ($0)
✅ cost_tracker.db   → Trazabilidad de costos ($0)
✅ Grimoire 3D       → Dashboard ($0)
✅ n8n (imagen)      → Orquestación (docker ready)
✅ Postgres (imagen)  → Datos estructurados (docker ready)
✅ Docker            → Infraestructura lista
```

## Lo que necesitamos agregar

```
❌ FreeSWITCH        → PBX telefónica (open source, $0)
❌ SIP Trunk         → Conexión a red telefónica (~$0.003/min)
❌ Número telefónico → Identificación en llamadas (~$1/mes)
```

---

## Arquitectura Final

```
                         ┌─────────────────────────────┐
                         │       GRIMOIRE 3D            │
                         │  (dashboard, agentes, voz)   │
                         └─────────────┬───────────────┘
                                       │
                         ┌─────────────┴───────────────┐
                         │         n8n (campañas)       │
                         │  Orquesta: leads, llamadas,  │
                         │  seguimiento, automatización │
                         └─────────────┬───────────────┘
                                       │
                         ┌─────────────┴───────────────┐
                         │       FreeSWITCH (PBX)       │
                         │                              │
                         │  Llamadas entrantes:         │
                         │    Cliente → FreeSWITCH      │
                         │    → Whisper → LLM → Kokoro  │
                         │    → FreeSWITCH → Cliente    │
                         │                              │
                         │  Llamadas salientes:         │
                         │    n8n → FreeSWITCH          │
                         │    → SIP Trunk → Lead        │
                         │    → Whisper → LLM → Kokoro  │
                         │    → Lead                    │
                         └─────────────┬───────────────┘
                                       │
                         ┌─────────────┴───────────────┐
                         │       SIP Trunk              │
                         │  (Telnyx / VoIP.ms / DIDWW)  │
                         │  ~$0.003/min · $1/mes num   │
                         └─────────────┬───────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │  RED TELEFÓNICA  │
                              │  (PSTN)          │
                              │  Telcel · AT&T   │
                              │  Movistar · etc  │
                              └─────────────────┘
```

---

## Comparativa de Costos

### Twilio (actual)

| Concepto | Costo |
|----------|-------|
| Minuto llamada MX | $0.013/min |
| Número telefónico | $1/mes |
| Media Streams | $0.002/min |
| **Llamada 10 min** | **$0.15** |

### FreeSWITCH + SIP Trunk barato

| Concepto | Costo |
|----------|-------|
| Minuto llamada MX (Telnyx) | $0.003/min |
| Número telefónico | $0.85/mes |
| FreeSWITCH | $0 (open source) |
| **Llamada 10 min** | **$0.03** |

### Ahorro

```
Twilio:      $0.15/llamada
FreeSWITCH:  $0.03/llamada
─────────────────────────
AHORRO:      80% por llamada

Con 1,000 llamadas/mes:
  Twilio:      $150.00
  FreeSWITCH:  $30.00
  ────────────────────
  AHORRO:      $120.00/mes
```

---

## Canales de Comunicación — SDC

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ORGANIZACIÓN (interno)              CLIENTES (externo)              │
│  ──────────────────────              ─────────────────               │
│                                                                     │
│  Telegram Bot         ← control      WhatsApp API  ← mensajes       │
│    · Notificaciones     agentes        · Cotizaciones               │
│    · Comandos                           · Seguimiento               │
│    · Alertas                           · Soporte                    │
│                                                                     │
│  Dashboard Grimoire  ← monitoreo     Llamadas VoIP  ← prospección  │
│    · Costos en vivo                    · FreeSWITCH                 │
│    · Agentes activos                   · SIP Trunk barato           │
│    · Sesiones activas                  · Kokoro contesta            │
│                                                                     │
│  WebSockets          ← tiempo real   Web (Grimoire) ← dashboard    │
│    · Streaming audio                   · Partners ven sus datos     │
│    · Eventos en vivo                   · Sin costos reales SDC      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ¿FreeSWITCH o Asterisk?

| Criterio | FreeSWITCH | Asterisk |
|----------|------------|----------|
| Escalabilidad | ✅ Decenas de miles | ⚠️ Cientos |
| WebRTC nativo | ✅ Sí | ❌ Con módulos |
| API moderna | ✅ HTTP/WS | ❌ AGI/AMI |
| Multi-tenant | ✅ Nativo | ⚠️ Complejo |
| Integración IA | ✅ WebSocket streaming | ⚠️ Limitado |
| Documentación | ❌ Escasa | ✅ Abundante |
| Curva de aprendizaje | ⚠️ Empinada | ✅ Suave |

**Recomendación: FreeSWITCH** por su WebSocket nativo para streaming de audio con IA.

---

## Plan de Implementación

### Semana 1 — FreeSWITCH básico
```bash
# En VPS (Docker)
docker run -d --name freeswitch \
  -p 5060:5060/udp -p 5060:5060/tcp \
  -p 7443:7443 -p 8021:8021 \
  -v freeswitch_conf:/etc/freeswitch \
  -v freeswitch_db:/var/lib/freeswitch/db \
  signalwire/freeswitch:latest

# Probar extensión interna
# Registrar softphone (Zoiper, Linphone) → llamada entre extensiones
```

### Semana 1 — SIP Trunk
```bash
# 1. Registrarse en Telnyx o VoIP.ms (~$10 crédito inicial)
# 2. Comprar número MX (~$0.85/mes)
# 3. Configurar trunk en FreeSWITCH
# 4. Probar llamada saliente a celular

# Llamada de prueba:
fs_cli -x "originate user/1001 &bridge(sofia/gateway/telnyx/526621072254)"
```

### Semana 2 — Integración con IA
```
1. FreeSWITCH recibe llamada → WebSocket envía audio a Mystic
2. Whisper STT → deepseek → Kokoro TTS
3. Audio sintetizado vuelve a FreeSWITCH → se reproduce al cliente
4. Transcripción completa → Engram + cost_tracker
```

### Semana 2-3 — n8n + Campañas
```
1. n8n toma leads del CRM
2. Programa llamada en FreeSWITCH
3. IA habla con el lead
4. Resultado vuelve al CRM
5. Si califica → agenda cita en calendario
```

---

## Costo Inicial

| Concepto | Costo |
|----------|-------|
| FreeSWITCH (open source) | $0 |
| SIP Trunk (Telnyx crédito) | $10 |
| Número telefónico MX | $0.85/mes |
| Minuto llamada MX | $0.003 |
| Docker + VPS (ya lo tienes) | $0 extra |
| **Total setup** | **~$10 USD** |

---

## Conclusión

```
Twilio:       $0.15/llamada · Dependencia externa · Vendor lock-in
FreeSWITCH:   $0.03/llamada · Control total · Open source · 80% más barato

PARA SDC:
  · FreeSWITCH + SIP Trunk (Telnyx) es la opción correcta
  · Telegram para control interno de agentes
  · WhatsApp para comunicación con clientes
  · Kokoro + Whisper + deepseek = stack completo de IA
  · Todo corre en tu VPS actual
  · Setup: $10 USD + 1 semana
```
