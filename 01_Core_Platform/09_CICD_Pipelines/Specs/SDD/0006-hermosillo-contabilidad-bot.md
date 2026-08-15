# Spec SDD 0006 — Hermosillo Contabilidad (Nathaly): Bot IA + Subdominio + Orbe + CRM

**ID**: 0006-hermosillo-contabilidad-bot
**Version**: 1.0.0
**Date**: 2026-08-15
**Author**: Luis Daniel Guerrero Enciso (MYSTIC / SDC)
**Status**: EN IMPLEMENTACIÓN (F0+F1 completos 2026-08-15; F2/F3 pendientes)

## Resumen

Nuevo cliente: **Nathaly** (@HermosilloCont_bot). Negocio de contabilidad en Hermosillo.
Objetivo: atender 24/7 por **Telegram + Web (subdominio propio)** a clientes que necesiten
contabilidad/administración, capturando leads, agendando citas SAT, con **chat + voz**
(STT fast-whisper + TTS edge-tts) y **dashboard CRM** para Nathaly.

Reutiliza toda la infra white-label de SDD 0004 (router multi-tenant, agente factory,
pipeline voz, orbe hero, provision_tenant). **No se inventa nada nuevo**: se provisiona
un tenant nuevo con la fábrica existente.

## Constitution Check

### Principio I: Orquestación Única
- [x] Todo entra por `tenant_router.py` (multi-tenant) → agente `nathaly` (Hermosillo Cont)
- [x] Un solo gateway Hermes (8643) sirve el chat web + bots Telegram
- [x] No hay comunicación directa entre agentes

### Principio II: Separación Determinista vs LLM
- [x] Routing (bot→tenant→agente): determinista (registry JSON + lookup)
- [x] Captura lead (nombre/servicio/fecha SAT): LLM con schema estricto (JSON mode)
- [x] Lead scoring (cold/warm/hot): determinista (reglas de negocio + OKF)
- [x] Agendamiento cita SAT: determinista (SQLite + validación zona horaria America/Hermosillo)
- [x] Notificación Nathaly: determinista (Telegram send + template CRM)
- [x] Respuesta natural al lead: LLM + OKF servicios exactos
- [x] Voice pipeline: determinista (edge-tts + ffmpeg + Telegram sendVoice)

### Principio III: Local-first (con REGLA DE ORO SDC)
- [x] Datos en SQLite/Engram locales
- [x] LLM vía OpenRouter (`deepseek/deepseek-v4-flash-0731`) solo cuando necesario
- [x] TTS local edge-tts (ligero) — permitido en laptop
- [x] STT fast-whisper: modelo **tiny/small int8** en VPS OVH o local si RAM lo permite
  (NUNCA modelos pesados en local — RAM 3.3GB, regla canónica)

### Principio IV: Testing
- [x] Tests routing multi-tenant (nathaly)
- [x] Tests captura lead (schema JSON)
- [x] Tests lead scoring
- [x] Tests agendamiento cita (zona America/Hermosillo)
- [x] Tests notificación Nathaly (formato CRM)
- [x] Tests voice pipeline (STT + TTS + envío)

### Principio V: Trazabilidad
- [x] Cada lead: ID único, timestamp, tenant, canal, estado, score
- [x] Log de auditoría consultable (Nathaly + Mystic)
- [x] Token del bot en secrets (`~/.hermes/.env` / secrets store), NUNCA en repo

## Spec

### Servicios Reales de Nathaly (OKF `hermosillo-cont.servicios`)
| Categoría | Oferta |
|-----------|--------|
| **Contabilidad** | Llevar contabilidad mensual, estados financieros, IVA/ISR |
| **Administración** | Gestión administrativa, nómina, flujo de caja |
| **Manifestación de Importación** | Trámite completo de pedimento/importación |
| **Marketing** | Estrategia y servicios de marketing para negocios |
| **Consultas ante el SAT** | Consultas, aclaraciones, trámites SAT |
| **Citas ante el SAT** | Agendar citas SAT a nombre del cliente |

*Precios NO fijos → Nathaly los define en llamada. Bot NUNCA inventa precios:
"solo te paso con Nathaly para cotizarte exacto".*

### Inputs
| Canal | Formato | Destino |
|-------|---------|---------|
| Telegram @HermosilloCont_bot | Update (message/voice/photo) | webhook → `tenant_router.py` → agente nathaly |
| Web subdominio (orbe hero) | Chat widget + voz (MediaRecorder) | POST `/api/v1/chat/completions` (gateway 8643) |
| WhatsApp (futuro) | wacli bridge | mismo router |

### Outputs
| Acción | Destino | Formato |
|--------|---------|---------|
| Respuesta al lead | Canal origen | Texto / Voz (OGG) |
| Lead + score + cita | Nathaly (Telegram) | Texto estructurado CRM |
| Lead en CRM | SQLite `leads_hermosillo_cont.db` | Tabla `leads` + `lead_intelligence` |
| Dashboard | Web `/dashboard-hermosillo/` | Panel leads + score + citas |
| Página hero | NatContability.sonoradigitalcorp.com | Orbe 3D + chat + voz |

### Contrato del Agente (tenant `hermosillo-cont`)
```json
{
  "tenant_id": "hermosillo-cont",
  "agent_id": "nathaly",
  "bot_name": "HermosilloCont_bot",
  "identity": {
    "nombre": "Asistente de Hermosillo Contabilidad",
    "rol": "Recepcionista comercial 24/7: captura lead, identifica servicio, agenda cita SAT, avisa a Nathaly",
    "directrices": [
      "Presentarse como asistente de Nathaly en Hermosillo Contabilidad",
      "NUNCA inventar precios: 'El costo exacto te lo da Nathaly en una llamada o WhatsApp'",
      "Ofrecer Diagnóstico inicial GRATIS (5 preguntas) como puerta de entrada",
      "Servicios: contabilidad, administración, manifestación de importación, marketing, consultas SAT, citas SAT",
      "Si piden info técnica compleja → escalar a Nathaly + notificar inmediato",
      "Capturar: nombre, negocio, servicio_interés, fecha_hora_preferida, canal_respuesta",
      "Calificar lead COLD/WARM/HOT con reglas deterministas",
      "Zona horaria: America/Hermosillo",
      "Voz por defecto: edge-tts es-MX-DaliaNeutral"
    ],
    "skill_requerida": "telegram + voice_reply + crm + agendar_cita",
    "canal_sugerido": "telegram|web"
  },
  "knowledge": {
    "okf_concepts": ["hermosillo-cont.servicios", "hermosillo-cont.faq"],
    "faq": "Contabilidad, administración, importaciones, SAT, citas, marketing"
  },
  "crm": {
    "tabla_leads": "leads_hermosillo_cont",
    "campos": ["id", "tenant", "chat_id", "nombre", "negocio", "servicio", "fecha", "hora", "estado", "score", "canal", "creado_en", "actualizado_en"]
  },
  "notificacion_nathaly": {
    "canales": ["telegram"],
    "chat_nathaly": "<pendiente — preguntar a Nathaly su chat_id>",
    "template": "📋 LEAD {score} | {nombre} ({negocio}) | Servicio: {servicio} | Cita: {fecha} {hora} | Canal: {canal}"
  }
}
```

### Flujo Onboarding (determinista + LLM donde corresponde)
```
1. RECIBIR mensaje (webhook / chat web) → router determina tenant/agente
2. SI voz → STT (faster-whisper) → texto
3. CLASIFICAR intención + extraer campos (LLM + schema JSON estricto):
   - "nuevo_lead" → capturar campos + score
   - "agendar_cita_sat" → validar disponibilidad + agendar
   - "precio" → "cotiza Nathaly en llamada" + capturar lead
   - "tecnico/dificil" → escalar a Nathaly
   - "info_general" → FAQ + ofrecer diagnóstico gratis
4. CALIFICAR LEAD (determinista cold/warm/hot)
5. PERSISTIR en SQLite leads_hermosillo_cont (determinista)
6. SI cita confirmada → NOTIFICAR a Nathaly (determinista)
7. RESPONDER al lead (LLM + OKF)
8. SI pide voz → TTS (edge-tts) → OGG → enviar (determinista)
```

### Infraestructura Web — Subdominio + DNS + SSL
- **Subdominio**: `NatContability.sonoradigitalcorp.com`
- **DNS**: A record → IP pública que sirve nginx (pendiente confirmar: DNS actual apunta a
  149.56.46.173 = VPS OVH; nginx local escucha en 187.245.110.211 — **tarea 0: verificar
  quién sirve el dominio hoy y a dónde apuntar el subdominio**)
- **SSL**: certbot (instalado) → cert para `NatContability.sonoradigitalcorp.com`
  (o wildcard si el provider DNS permite)
- **Nginx**: nuevo `location` o `server{}` para el subdominio → sirve la página hero
- **Página hero (orbe)**: copia del orbe existente (`Aztrotech/04_Deployment/orbe/index.html`)
  rebrandeado a Hermosillo Contabilidad, con chat widget + micrófono (MediaRecorder → API)

### Dashboard (CRM para Nathaly)
- Panel web en subdominio `/dashboard-hermosillo/` (o ruta local)
- Muestra: leads del día, score distribution, citas SAT, botones acción
- Tech: reutilizar patrón dashboard existente (proxy nginx → puerto local)

## Plan de Implementación

### Fase 0: Descubrimiento y Setup (P0 — hoy)
| Task | Descripción | Dependencia |
|------|-------------|-------------|
| T0.1 | Confirmar quién sirve el dominio sonoradigitalcorp.com (VPS OVH vs local) y dónde apuntar el subdominio | — |
| T0.2 | Registrar tenant `hermosillo-cont` en `tenants.json` + `tenant_router.py` + `people.json` (Nathaly) | T0.1 |
| T0.3 | Guardar token del bot en secrets (`~/.hermes/.env`), NO en repo | — |
| T0.4 | Crear agente `nathaly` con `hermes_agent_factory.py` (persona recepcionista comercial) | T0.2 |
| T0.5 | Crear OKF `hermosillo-cont.servicios` (lista de servicios, sin precios) | T0.4 |
| T0.6 | Preguntar a Nathaly: chat_id de Telegram para notificaciones | — |

### Fase 1: Bot Telegram funcional (P0)
| Task | Descripción |
|------|-------------|
| T1.1 | Tests TDD: routing, lead capture, scoring, agendamiento, notificación |
| T1.2 | `onboarding_engine` tenant-aware (o reuso con config de tenant) |
| T1.3 | `lead_classifier` con schema servicios Hermosillo Cont |
| T1.4 | `voice_pipeline` reutilizado (STT fast-whisper + TTS edge-tts + sendVoice) |
| T1.5 | Webhook Telegram conectado al bot @HermosilloCont_bot (setWebhook) | ✅ 2026-08-15: `telegram_webhook_hermosillo.py` (webhook :5291 + polling). 13/13 tests. Verificado HTTP end-to-end. Modo polling activo; setWebhook real pendiente de F2 (URL pública) |
| T1.6 | SQLite `leads_hermosillo_cont.db` | ✅ 2026-08-15: `Databases/leads_hermosillo_cont.db` (motor determinista, tabla leads + lead_intelligence) |

### Fase 2: Subdominio + Orbe + Chat/Voz Web (P1)
| Task | Descripción |
|------|-------------|
| T2.1 | A record DNS subdominio + certbot SSL |
| T2.2 | Server block nginx para NatContability.sonoradigitalcorp.com |
| T2.3 | Página hero orbe rebrandeada + widget chat (POST `/api/v1/chat/completions`) |
| T2.4 | Botón micrófono → MediaRecorder → STT → responder (voz) |
| T2.5 | Prueba E2E: visitar subdominio → hablar → responde con voz |

### Fase 3: CRM + Dashboard (P1)
| Task | Descripción |
|------|-------------|
| T3.1 | Panel leads + citas SAT + score para Nathaly |
| T3.2 | Notificación push a Nathaly por nuevo lead HOT |
| T3.3 | Export CSV de leads (Nathaly pide datos para su proceso) |

### Fase 4: Multi-canal y mejora (P2)
| Task | Descripción |
|------|-------------|
| T4.1 | WhatsApp (wacli) para Nathaly |
| T4.2 | Feedback loop (reacción lead → score) |
| T4.3 | Dashboard multi-tenant en panel MYSTIC |

## Testing (TDD)
| Test | Qué valida |
|------|------------|
| `test_routing.py` | bot_name → tenant `hermosillo-cont` correcto |
| `test_lead_capture.py` | LLM extrae campos obligatorios (nombre, servicio, fecha) |
| `test_lead_scoring.py` | Reglas cold/warm/hot, edge cases |
| `test_scheduling.py` | Cita SAT zona America/Hermosillo, conflictos |
| `test_notification.py` | Nathaly recibe lead formateado CRM |
| `test_voice_pipeline.py` | STT + TTS + envío Telegram/web |
| `test_okf.py` | Respuesta de servicios usa SOLO OKF exacto |

## Criterios de Éxito
- [ ] Lead entra (Telegram o web) → capturado + score + cita + Nathaly notificada < 30s
- [ ] Voz funciona: audio → STT → respuesta en voz < 10s
- [ ] Subdominio NatContability.sonoradigitalcorp.com activo con SSL
- [ ] Página hero con orbe + chat + micrófono funcionando
- [ ] Precios: cero alucinación (bot NUNCA inventa, deriva a Nathaly)
- [ ] Dashboard muestra leads/citas/score para Nathaly
- [ ] Tests pasan

## Riesgos
| Riesgo | Mitigación |
|--------|------------|
| DNS del dominio apunta a VPS inalcanzable (149.56.46.173) | T0.1 confirma y corrige antes de tocar nada |
| STT lento en CPU | faster-whisper tiny/small int8 (< 2s), o VPS OVH |
| Token bot filtrado en repo | Secrets en `~/.hermes/.env`, redact_secrets ON |
| Zona horaria cita | Guardar UTC, mostrar en America/Hermosillo |
| Precios inexistentes | OKF sin precios → derivar a Nathaly siempre |
| Chat_id Nathaly desconocido | T0.6: pedirle que escriba al bot primero |

## Entregables del Cliente (Nathaly)
- Bot @HermosilloCont_bot operativo (texto + voz)
- Subdominio con página hero (orbe + chat + voz)
- Dashboard CRM con sus leads y citas
- Manual: "Cómo te llegan tus clientes" (1 hoja)

## Entregables para MYSTIC
- Tenant registrado + agente + OKF + spec
- Métricas: leads por score, citas, tiempo respuesta
- Reutilización: todo corre sobre infra white-label existente