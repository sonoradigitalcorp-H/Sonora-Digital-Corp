# SDD 0004: Aztrotech Onboarding Inteligente + Plataforma White-Label (v2 - Data Real)
## Objetivo
Sistema autónomo que: (1) Onboardea leads de Aztrotech 24/7 por Telegram/WhatsApp/Web, captura voz+texto, califica (cold/warm/hot), agenda cita diagnóstica y avisa a César con resumen completo + objeciones evaluadas; (2) Base white-label reutilizable para cualquier tenant. Comunicación determinista, LLM solo para escenarios nuevos no contemplados.

## Constitution Check
### Principio I: Orquestación Única
- [x] Todo entra por `multi_tenant_webhook.py` → `tenant_router.py` → agente correcto
- [x] No hay comunicación directa entre agentes

### Principio II: Separación Determinista vs LLM
- [x] Routing (bot→tenant→agente): determinista (registry JSON + lookup)
- [x] Captura lead (nombre/empresa/servicio/fecha): LLM con schema estricto (JSON mode)
- [x] **Lead scoring (cold/warm/hot): determinista (reglas de negocio + OKF)**
- [x] **Resumen empresa + objeciones: LLM con plantilla evaluada + OKF**
- [x] Agendamiento cita: determinista (calendario SQLite + validación zona horaria)
- [x] Notificación César: determinista (wacli/Telegram send + template estructurado)
- [x] Respuesta natural al lead: LLM + OKF pricing exacto
- [x] **Generación assets (imagen/video/mockup/audio): LLM con prompts evaluados Midjourney/NanoBanana**
- [x] **Auto-mejora por reacciones: determinista (reglas de feedback loop) + LLM para síntesis**
- [x] Voice pipeline: determinista (edge-tts + ffmpeg + wacli/Telegram API)

### Principio III: Local-first
- [x] Datos en SQLite/Neo4j/Engram locales
- [x] LLM vía OpenRouter (deepseek-v4-flash) solo cuando necesario
- [x] Voice TTS local (edge-tts) — no modelo pesado

### Principio IV: Testing
- [x] Tests de routing multi-tenant
- [x] Tests de captura lead (schema JSON)
- [x] Tests de lead scoring (cold/warm/hot rules)
- [x] Tests de agendamiento (conflictos, zonas horarias)
- [x] Tests de notificación César (formato CRM)
- [x] Tests de voice pipeline (generación OGG, envío)
- [x] Tests de generación assets (prompts evaluados)
- [x] Tests de auto-mejora (feedback loop)

### Principio V: Trazabilidad
- [x] Cada lead: ID único, timestamp, tenant, canal, estado, score, objeciones
- [x] Decisiones de routing registradas
- [x] Log de auditoría consultable (César + Mystic)

## Spec

### Inputs
| Canal | Formato | Destino |
|-------|---------|---------|
| Telegram | Update (message/voice) | `multi_tenant_webhook.py` POST /webhook |
| WhatsApp | Webhook (wacli/Business API) | Mismo webhook |
| Web (landing) | Formulario / widget voz | Mismo webhook |

### Outputs
| Acción | Destino | Formato |
|--------|---------|---------|
| Respuesta al lead | Canal origen | Texto / Voz (OGG) |
| Lead calificado + cita + resumen + objeciones | César (WhatsApp/Telegram) | Texto estructurado CRM + audio abordaje |
| Lead en CRM (César + Mystic) | SQLite dual + Engram | Tabla `leads` + `lead_intelligence` |
| Métricas | Prometheus/Engram | Contadores + latencia + score distribution |
| Assets generados | Usuario que lo pide | Imagen/Video/Mockup/Audio + prompt usado |

### Servicios Reales Aztrotech (desde aztrotech.mx)
| Categoría | Oferta | Precio |
|-----------|--------|--------|
| **Empleado Digital (Agente IA)** | Starter AI Agent | $999 USD |
| | Growth AI Agent | $1,999 USD |
| | Enterprise AI Agent | $3,999 USD |
| **Automatizaciones** | Flujos + Reportes + Integraciones | Cotización según procesos |
| **Plataformas Empresariales** | CRM/ERP a medida + Dashboards + Apps | Cotización por proyecto |
| **Plataformas Especializadas** | Jurídica / Inmobiliaria / Academia Interna | Ya construidas, adaptables |
| **Diagnóstico IA** | 30 min, 5 preguntas, resultado inmediato | GRATIS |

### Contrato del Agente Onboarding (por tenant)
```json
{
  "tenant_id": "aztrotech",
  "agent_id": "cesar-onboard",
  "identity": {
    "nombre": "Asistente Aztrotech",
    "rol": "Onboarding comercial 24/7: captura lead, califica (cold/warm/hot), agenda cita diagnóstica, avisa a César con resumen + objeciones",
    "directrices": [
      "Nunca revelar que es de Sonora Digital Corp",
      "Siempre presentarse como asistente de César Holguín en Aztrotech",
      "NUNCA dar precios inventados: usar SOLO OKF exacto. Si no está en OKF: 'Los precios exactos te los da César en llamada.'",
      "SIEMPRE ofrecer Diagnóstico IA Gratis (30 min) como primer paso",
      "Si piden info técnica compleja o se pone difícil: 'Te paso con César directamente' + notificar inmediato",
      "Voz por defecto: edge-tts es-MX-DaliaNeutral (rápida). Texto si usuario no pide voz",
      "Capturar: nombre, empresa, giro, tamaño_equipo, servicio_interés, fecha_hora_preferida, canal_respuesta, objeciones",
      "Calificar lead: COLD/WARM/HOT con reglas deterministas",
      "Generar resumen empresa + objeciones evaluadas para César",
      "Generar assets (imagen/video/mockup/audio) con prompts evaluados si lo piden"
    ],
    "skill_requerida": "wacli + telegram + voice_reply + asset_generation",
    "canal_sugerido": "telegram|whatsapp|web"
  },
  "knowledge": {
    "okf_concepts": ["aztrotech.pricing", "aztrotech.servicios", "aztrotech.casos_reales"],
    "faq": "Preguntas frecuentes de Aztrotech (empleado digital, automatizaciones, plataformas, diagnóstico)"
  },
  "crm": {
    "tabla_leads": "leads_aztrotech",
    "tabla_intelligence": "lead_intelligence_aztrotech",
    "campos_leads": ["id", "tenant", "chat_id", "nombre", "empresa", "giro", "tamano_equipo", "servicio", "fecha", "hora", "estado", "score", "canal", "creado_en", "actualizado_en"],
    "campos_intelligence": ["lead_id", "resumen_empresa", "objeciones", "score_detalle", "next_action", "cesar_notificado_en"]
  },
  "notificacion_cesar": {
    "canales": ["whatsapp", "telegram"],
    "chat_cesar": "6621072254",
    "template": "📋 LEAD {score} | {nombre} ({empresa}, {giro}, {tamano_equipo}) | {servicio} | Cita: {fecha} {hora} | Resumen: {resumen_empresa} | Objeciones: {objeciones} | Next: {next_action}"
  }
}
```

### Flujo Onboarding (determinista + LLM donde corresponde)
```
1. RECIBIR mensaje (webhook) → router determina tenant/agente (determinista)
2. SI voz → STT (faster-whisper) → texto
3. CLASIFICAR intención + extraer campos (LLM + schema JSON estricto):
   - "nuevo_lead" → capturar campos + calificar score
   - "agendar_cita" → validar disponibilidad (determinista)
   - "precio" → responder con OKF exacto + capturar lead + calificar
   - "tecnico/dificil" → escalar a César
   - "info_general" → responder con FAQ + web + ofrecer diagnóstico gratis
   - "generar_asset" → LLM con prompt evaluado → entregar asset
4. CALIFICAR LEAD (determinista - reglas cold/warm/hot):
   COLD: solo nombre/empresa, sin fecha, sin presupuesto claro
   WARM: tiene empresa + giro + servicio_interés + fecha tentativa
   HOT: WARM + presupuesto alineado + urgencia + tomador decisiones
5. PERSISTIR lead + intelligence en SQLite dual (determinista)
6. SI cita confirmada → NOTIFICAR a César con resumen completo (determinista)
7. RESPONDER al lead (LLM + OKF para precios exactos + diagnóstico gratis)
8. SI usuario pide voz → TTS (edge-tts) → OGG → enviar (determinista)
9. FEEDBACK LOOP: reacción del lead → actualizar score + auto-mejora prompts
```

### Lead Scoring Determinista (Reglas de Negocio)
```python
def calculate_lead_score(lead: dict) -> tuple[str, dict]:
    """Retorna (score, detalle). Solo reglas, cero LLM."""
    score = 0
    detalle = {"factores": []}
    
    # Datos básicos (max 30 pts)
    if lead.get("nombre"): score += 5; detalle["factores"].append("nombre: +5")
    if lead.get("empresa"): score += 10; detalle["factores"].append("empresa: +10")
    if lead.get("giro"): score += 5; detalle["factores"].append("giro: +5")
    if lead.get("tamano_equipo"): score += 5; detalle["factores"].append("tamano: +5")
    if lead.get("servicio"): score += 5; detalle["factores"].append("servicio: +5")
    
    # Intención clara (max 25 pts)
    if lead.get("fecha") and lead.get("hora"): score += 15; detalle["factores"].append("cita_agendada: +15")
    elif lead.get("fecha"): score += 8; detalle["factores"].append("fecha_tentativa: +8")
    if lead.get("presupuesto_mencionado"): score += 10; detalle["factores"].append("presupuesto: +10")
    
    # Urgencia/Autoridad (max 25 pts)
    if lead.get("urgencia_alta"): score += 15; detalle["factores"].append("urgencia: +15")
    if lead.get("es_tomador_decisiones"): score += 10; detalle["factores"].append("autoridad: +10")
    
    # Engagement (max 20 pts)
    if lead.get("respondio_voz"): score += 5; detalle["factores"].append("voz: +5")
    if lead.get("pidio_asset"): score += 5; detalle["factores"].append("asset: +5")
    if lead.get("click_diagnostico"): score += 10; detalle["factores"].append("diagnostico: +10")
    
    # Clasificar
    if score >= 70: return "HOT", {"score": score, **detalle}
    elif score >= 40: return "WARM", {"score": score, **detalle}
    else: return "COLD", {"score": score, **detalle}
```

### White-Label: Provisionar Nuevo Tenant (determinista)
```bash
python3 provision_tenant.py \
  --tenant miempresa \
  --bot @miempresa_bot \
  --owner "Juan Pérez" \
  --cliente "MiEmpresa SA" \
  --voz es-MX-JorgeNeural \
  --canales telegram,whatsapp,web \
  --okf-concepts miempresa.pricing,miempresa.servicios,miempresa.faq \
  --servicios "empleado_digital,automatizaciones,plataformas" \
  --precios "starter:999,growth:1999,enterprise:3999"
```
Genera: registry entry, directorio tenant con configs, landing page, webhook routing, Engram space aislado.

### Landing Page por Tenant (Plantilla)
- `tenants/{tenant}/web/index.html` — Three.js + branding + botón WhatsApp + widget voz + diagnóstico gratis
- Configurable: colores, logo, nombre, voz, servicios, precios
- Sirve como "página/app propia" donde el cliente define su tecnología

### Generación de Assets (Prompts Evaluados Midjourney/NanoBanana/Pro)
| Tipo | Prompt Base Evaluado | Parámetros Usuario |
|------|---------------------|-------------------|
| **Imagen** | `midjourney_v6 --style raw --ar 16:9 --q 2 --stylize 750` + template por caso de uso | estilo, tema, colores, formato |
| **Video** | `runway_gen3 --duration 10 --ratio 16:9 --motion 80` + template | concepto, duración, estilo |
| **Mockup** | `figma_mockup --device mobile --theme dark --brand colors` + template | tipo app, pantallas, branding |
| **Audio** | `elevenlabs_tts --voice cesár_clone --stability 0.5 --similarity 0.8` + template | texto, voz, emoción |

*Prompts almacenados en `asset_prompts/` con versión, score de calidad, feedback de usuarios.*

### Auto-Mejora por Reacciones (Feedback Loop)
```
1. Usuario reacciona (click, respuesta, tiempo, conversion)
2. Regla determinista: si reacción positiva → reforzar prompt/path
3. Si reacción negativa → marcar para revisión + variante alternativa
4. LLM sintetiza patrones semanales → propone mejoras a prompts/reglas
5. Humano (César/Mystic) aprueba → se versiona en asset_prompts/
6. Próxima iteración usa versión mejorada
```
Almacena en Engram: `feedback:{tenant}:{lead_id}` + `asset_prompt_versions`

### Deliverables para César (CRM)
- Lead completo: datos + score (COLD/WARM/HOT) + detalle scoring
- Resumen empresa: giro, tamaño, dolor detectado, presupuesto estimado
- Objeciones evaluadas: lista + probabilidad + contraargumento sugerido
- Next action concreta: "Llamar mañana 10am", "Enviar caso Jewelry", "Agendar demo"
- Audio de abordaje personalizado (voz César clonada)
- Link a landing del lead + diagnóstico si lo hizo

### Deliverables para Mystic (Plataforma)
- Mismo formato que César + métricas agregadas por tenant
- Dashboard multi-tenant: leads por score, conversion, tiempo respuesta
- Alertas: lead HOT sin contacto 2h, score drop, objeción recurrente
- Auto-mejora global: patrones cross-tenant → mejores prompts/reglas para todos

### Testing (TDD)
| Test | Qué valida |
|------|------------|
| `test_routing.py` | bot_name → tenant_id correcto |
| `test_lead_capture.py` | LLM extrae campos obligatorios en JSON válido |
| `test_lead_scoring.py` | Reglas cold/warm/hot deterministas, edge cases |
| `test_scheduling.py` | Conflictos fecha/hora, zona horaria Hermosillo |
| `test_notification.py` | César recibe lead formateado CRM en ambos canales |
| `test_okf_pricing.py` | Respuesta precio usa SOLO valores exactos OKF |
| `test_voice_pipeline.py` | Texto → OGG < 5s, envío Telegram OK |
| `test_asset_generation.py` | Prompts evaluados generan assets válidos |
| `test_feedback_loop.py` | Reacción → actualiza score + propone mejora |
| `test_provision_tenant.py` | Un comando crea tenant operable |

## Plan de Implementación

### Fase 1: Core Onboarding Aztrotech Real (P0)
1. **OKF actualizado** ✓ (`aztrotech.pricing.json` real)
2. **Tests TDD** `tests/integration/test_aztrotech_onboard.py`
3. **onboarding_engine.py** — motor determinista + lead_scoring + dual CRM
4. **lead_classifier.py** — LLM + schema JSON + OKF context
5. **voice_pipeline.py** — STT + TTS + envío unificado
6. **lead_intelligence.py** — resumen empresa + objeciones + next_action
7. **asset_generation.py** — prompts evaluados para imagen/video/mockup/audio
8. **feedback_loop.py** — auto-mejora por reacciones
7. **Extender webhook + router** para voz + routing completo
8. **SQLite dual** leads + intelligence
9. **Entry point** `run_onboarding.py`

### Fase 2: White-Label Provisioning (P1)
1. `provision_tenant.py` — crea tenant operable < 30s
2. Plantillas configs + landing page + asset_prompts base
3. Test `test_provision_tenant.py`

### Fase 3: Multi-Canal + Voz Completa (P1)
1. WhatsApp Business API webhook (wacli bridge)
2. Widget voz en landing (MediaRecorder → webhook)
3. Tests E2E voz+texto

### Fase 4: Dashboard César + Mystic (P2)
- Panel César: leads día, score, objeciones, botones acción
- Panel Mystic: multi-tenant, métricas agregadas, auto-mejora global

## Criterios de Éxito
- [ ] Lead entra → capturado + score (COLD/WARM/HOT) + cita + César notificado < 30s
- [ ] Voz funciona: audio → STT → respuesta en voz < 10s
- [ ] Provisionar tenant: 1 comando → bot + landing + webhook listos
- [ ] Precios SIEMPRE exactos desde OKF (cero alucinación)
- [ ] Escalación a César: "te paso con él" + notificación inmediata con resumen CRM
- [ ] Assets generados con prompts evaluados (imagen/video/mockup/audio)
- [ ] Feedback loop: reacción usuario → actualiza score + propone mejora prompt
- [ ] Tests pasan: routing, lead capture, scoring, scheduling, notification, voice, assets, feedback, provision

## Riesgos
| Riesgo | Mitigación |
|--------|------------|
| STT lento en CPU | faster-whisper small int8 (< 2s para 10s audio) |
| WhatsApp sandbox limitado | Empezar Telegram; WhatsApp cuando haya Business API |
| Token bot hardcodeado | Secrets en `~/.openclaw/secrets/` + registry hash |
| Zona horaria cita | Guardar UTC, mostrar en America/Hermosillo |
| Prompts assets no evaluados | Versionar en `asset_prompts/` con score + feedback |
| Auto-mejora deriva | Humano aprueba cambios; LLM solo propone |