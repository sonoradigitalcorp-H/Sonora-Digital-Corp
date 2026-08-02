# Sales Engine AztroTech — Especificación Completa

## Visión: Cliente para toda la vida

No es un call center. Es un **sistema de ventas que nunca para**.

```
Busca 20 negocios/día → Los contacta → Los califica → Los nutre → Los cierra → Los retiene → Les upsalea
```

---

## 1. Modelo de Cobro

### Opción A: Paquete de minutos (recomendado para starters)

| Paquete | Minutos/mes | Incluye | Precio |
|---------|-------------|---------|--------|
| **Starter** | 500 min | Calls + campañas básicas | **$299/mes** |
| **Business** | 2,000 min | + campañas con marketing | **$799/mes** |
| **Enterprise** | 5,000 min | + campañas ilimitadas + ads | **$1,999/mes** |
| **Minuto extra** | — | fuera del paquete | **$0.05/min** |

### Opción B: Por lead generado (escalable)

| Concepto | Precio |
|----------|--------|
| Por lead calificado (Warm+) | $2.00/lead |
| Por cita agendada | $5.00/cita |
| Por venta cerrada | 10% comisión |
| Costo llamada | $0.003/min (costo real) |

### Opción C: Suscripción plana (lo que César prefiere)

| Volumen leads/día | Precio fijo/mes |
|-------------------|----------------|
| 10 leads/día (200/mes) | **$499/mes** |
| 20 leads/día (400/mes) | **$999/mes** |
| 50 leads/día (1,000/mes) | **$2,499/mes** |

**Mi recomendación: Opción C.** César paga fijo, sin sorpresas. El costo real para SDC es ~$30-50/mes de infraestructura + $0.003/min Telnyx. Margen: 94-97%.

---

## 2. KPIs de Llamadas

### Por llamada individual

| KPI | Qué mide | Target |
|-----|----------|--------|
| **Duración** | Tiempo real de conversación | >2 min = buena |
| **Costo** | $0.003/min Telnyx + $0.0004 IA | ~$0.01/llamada |
| **Intención detectada** | ¿El sistema entendió el propósito? | >95% |
| **Rapport** | ¿Se usó el nombre del lead? ¿Tono correcto? | Check automático |
| **Objeción manejada** | ¿Se aplicó Brian Tracy 5 pasos? | Check en transcript |

### Por campaña

| KPI | Qué mide | Target |
|-----|----------|--------|
| **Tasa de conexión** | Llamadas contestadas / intentadas | >30% |
| **Tasa de conversación** | Conversaciones completas / conectadas | >80% |
| **Lead calificado (Warm+)** | Calificados / contactados | >25% |
| **Costo por lead** | Gasto total / leads calificados | <$2.00 |
| **Tasa de cierre** | Ventas / leads calificados | >10% |
| **ROI** | (Ventas - costo) / costo | >300% |
| **Tasa de transferencia** | Escalados a César / total | <20% |

### Por cliente (longitudinal)

| KPI | Qué mide | Target |
|-----|----------|--------|
| **LTV** | Ingreso total del cliente | >$5,000 |
| **Churn mensual** | Clientes perdidos / activos | <5% |
| **Tasa de upsell** | Clientes que migran a plan superior | >20% |
| **NPS** | Satisfacción del cliente | >8/10 |
| **Tiempo de vida** | Meses como cliente activo | >12 meses |

---

## 3. Intenciones de Llamada (Call Intents)

Cada llamada OUTBOUND tiene una intención. Cada llamada INBOUND también. Así se clasifican:

### Outbound Intents (cuando el sistema llama)

| Intención | Cuándo se usa | Prompt específico | Acción post-llamada |
|-----------|--------------|-------------------|---------------------|
| **cold_discovery** | Primer contacto, lead frío | Presentación + calificación BANT | Si califica → Warm. Si no → descartar o nutrir |
| **warm_followup** | Lead ya mostró interés | Recordatorio + resolver dudas + cerrar | Si cierra → contrato. Si duda → agendar con César |
| **hot_closing** | Lead listo para comprar | Cierre rápido + FOMO + pago | Enviar link de pago + onboarding |
| **nurturing** | Lead tibio, necesita cariño | Tips, casos de éxito, valor gratuit | Si responde → subir a warm. Si no → nutrir 3x y descartar |
| **reengagement** | Lead que se enfrió | Oferta especial, novedad, "te extrañamos" | Si responde → warm. Si no → descartar |
| **survey** | Cliente existente | Satisfacción, NPS, recomendación | Si NPS <7 → escalar a César |
| **upsell** | Cliente en plan actual | Presentar plan superior, beneficios | Si acepta → migrar plan. Si duda → info + followup |
| **renewal** | Cliente por vencer | Recordatorio renovación, oferta exclusiva | Si renueva → confirmar. Si duda → César |
| **referral** | Cliente satisfecho | Pedir referidos, programa de afiliados | Si da referido → agregar a campaña + agradecer |

### Inbound Intents (cuando le llaman al negocio)

| Intención | Señales | Acción |
|-----------|---------|--------|
| **support** | "tengo un problema", "no funciona" | Resolver o escalar a soporte |
| **quote** | "cuánto cuesta", "presupuesto" | Calificar + enviar cotización |
| **complaint** | "estoy enojado", "mala experiencia" | Escalar a César INMEDIATAMENTE |
| **information** | "qué hacen", "cómo funciona" | Presentación + calificación |
| **existing_client** | "soy cliente", "mi cuenta" | Identificar + resolver |
| **wrong_number** | "quién es?", "equivocado" | Disculparse + colgar |

---

## 4. Sistema de Campañas

Cada campaña es un **proyecto de ventas completo**.

### Ciclo de vida de una campaña

```
Paso 1: DEFINIR CAMPAÑA
────────────────────────
César (o el sistema) define:
  • Nicho/industria objetivo (ej: "despachos contables en Hermosillo")
  • Oferta (ej: "Call Agent por $299/mes, primera semana gratis")
  • Volumen diario (ej: 20 leads/día)
  • Duración (ej: 2 semanas)

Paso 2: GENERAR LEAD LIST
─────────────────────────
El sistema busca 20 negocios/día:
  • Google Maps (despachos contables en Hermosillo)
  • Directorios web (Sección Amarilla, etc.)
  • Redes sociales (LinkedIn, Facebook)
  • Resultado: Nombre, teléfono, rubro, ubicación

Paso 3: CREAR ASSETS DE MARKETING
──────────────────────────────────
El sistema genera automáticamente:
  • 🖼️ Imagen promocional para WhatsApp/redes
  • 🎥 Video corto (30s) explicando la oferta
  • 📝 Guión de llamada personalizado para el nicho
  • 💬 Mensaje de WhatsApp de seguimiento
  • 📧 Email de bienvenida (si aplica)

Paso 4: EJECUTAR LLAMADAS
──────────────────────────
  • El sistema llama a los 20 leads del día
  • Cada llamada sigue el prompt según la intención
  • Clasifica automáticamente: Cold → Warm → Hot
  • Si Hot → intenta cerrar o escala a César

Paso 5: SEGUIMIENTO AUTOMÁTICO
───────────────────────────────
  • Warm: WhatsApp automático a las 24h con info
  • Warm: Segunda llamada a las 72h
  • Hot: Transferencia a César + audio-resumen
  • Cold que no contestó: Reintento en 48h (máx 3 intentos)

Paso 6: REPORTE
───────────────
  • Al final del día: leads contactados, calificados, cerrados
  • Al final de la campaña: ROI, costo por lead, mejor hora, mejor guión
```

### Template de campaña

```yaml
campaña:
  nombre: "Despachos Contables HMO - Octubre"
  nicho: "contabilidad"
  ubicación: "Hermosillo, Sonora"
  oferta: "Call Agent $299/mes - 1er mes gratis"
  duración: 14 días
  volumen_diario: 20
  intención_inicial: cold_discovery
  assets:
    imagen: true
    video: true
    guión: true
    whatsapp_msg: true
  reglas:
    max_intentos: 3
    intervalo_reintento_horas: 48
    escalar_a_cesar: hot
    followup_warm_horas: 24
  kpis_target:
    tasa_conexión: ">30%"
    costo_por_lead: "<$2.00"
    leads_calificados_por_día: ">5"
    tasa_cierre: ">10%"
```

---

## 5. Sistema de Clasificación Cold/Warm/Hot

### Cold — Primer contacto

| Señal | Significado |
|-------|-------------|
| Nunca ha oído de AztroTech | Frío total |
| Contestó pero no mostró interés | Frío informativo |
| Pidió que no llamen más | 🚫 Bloquear permanentemente |
| No contestó (3 intentos) | Frío — descartar |

**Acción:** Presentación rápida + calificación BANT. Si no califica → descartar. Si califica algo → Warm.

### Warm — Mostró interés

| Señal | Significado |
|-------|-------------|
| Preguntó precios | 🟡 Warm — informativo |
| Pidió más información | 🟡 Warm — investigando |
| Dijo "llámame después" | 🟡 Warm — programado |
| Vio el video/imagene y respondió | 🟢 Warm — caliente |

**Acción:** Followup automático a las 24h (WhatsApp) + 72h (llamada). Si en 3 followups no avanza → reengagement o descartar.

### Hot — Listo para comprar

| Señal | Significado |
|-------|-------------|
| Preguntó "cómo empiezo" | 🔥 Hot — intención de compra |
| Pidió cotización formal | 🔥 Hot — negociación |
| Preguntó por formas de pago | 🔥🔥 Hot — ready to buy |
| Dijo "lo quiero" o "me urge" | 🔥🔥🔥 Hot — cierre inmediato |
| Pidió hablar con César | 🔥 Hot — escalar YA |

**Acción:** Cierre rápido + FOMO + link de pago. Si duda → escalar a César con resumen completo.

### Escala de Temperatura (Score)

| Score | Estado | Acción |
|-------|--------|--------|
| 0-20 | 🧊 Frío | Descartar o nutrir 1 vez |
| 21-40 | 🧊 Frío con potencial | Nutrir 3 veces |
| 41-60 | 🌤️ Tibio | Followup automático |
| 61-80 | ☀️ Warm | Seguimiento cercano + info |
| 81-90 | 🔥 Hot | Preparar cierre |
| 91-100 | 🔥🔥🔥 Hot ready | Cerrar o escalar YA |

**Score se calcula de:** BANT (40%) + Engagement (30%) + Urgencia (20%) + Señales de compra (10%)

---

## 6. Customer for Life — Flujo Completo

```
PRIMERA LLAMADA (Cold)
    ↓
¿Califica BANT? → No → Descartar o nutrir
    ↓ Sí
SEGUNDO CONTACTO (Warm) — 24h después
    ↓
¿Sigue interesado? → No → Reengagement campaign
    ↓ Sí
TERCER CONTACTO (Warm+) — 72h después
    ↓
¿Listo para comprar? → No → Seguir nutriendo (máx 3)
    ↓ Sí
CIERRE (Hot)
    ↓
🎉 VENTA CERRADA
    ↓
ONBOARDING — Automático
    • Cuenta creada
    • Agente configurado
    • Video de bienvenida
    ↓
PRIMER MES
    • Llamada de checkup a los 7 días
    • Encuesta de satisfacción a los 30 días
    ↓
MES 2-6
    • Newsletter semanal con tips
    • Llamada de upsell a los 90 días
    • Programa de referidos
    ↓
MES 6+
    • Revisión de plan (¿necesita más?)
    • Ofertas exclusivas para clientes existentes
    • Evento de comunidad (webinar, grupo)
    ↓
RENOVACIÓN ANUAL
    • Descuento por fidelidad
    • Plan premium con más features
    ↓
🔄 CICLO: Cliente → Embajador → Refiere → Crece
```

---

## 7. Lo que necesita el sistema (técnico)

| Componente | Qué hace | Estado |
|---|---|---|
| **Generador de lead lists** | Busca 20 negocios/día en Google Maps + directorios | ❌ No existe |
| **Generador de assets marketing** | Crea imagen + video + guión por campaña | ⚠️ Parcial (Content Studio existe) |
| **Twilio Voice Bridge** | Hace las llamadas | ⚠️ Código listo, sin credenciales |
| **Clasificador Cold/Warm/Hot** | Score automático post-llamada | ❌ No existe |
| **Sistema de campañas** | Orquesta ciclo de vida completo | ❌ No existe |
| **CRM de seguimiento** | Followups automáticos, historial | ⚠️ Parcial (pipeline de ventas existe) |
| **Dashboard de KPIs** | Métricas en tiempo real | ⚠️ Parcial (Grimoire existe) |
| **n8n workflows** | Orquestación de campañas | ✅ Listo (Docker) |

---

## 8. Lo que ve César vs lo que ve el cliente

### César ve (dashboard partner):
```
Campaña: "Despachos Contables HMO"
├── 📊 Leads hoy: 20/20 contactados
├── 🔥 Hot: 2 · ☀️ Warm: 5 · 🧊 Cold: 8 · ❌ No cont: 5
├── 💰 Costo hoy: $2.40 ($0.12/llamada)
├── 📈 Ventas esta campaña: $2,499
├── 📉 ROI: 15,000%
└── 🎯 Próxima acción: 1 Hot listo para cerrar
```

### El cliente final ve:
```
"Gracias por llamar a AztroTech.
Soy el asistente de ventas. ¿Cómo puedo ayudarte?"
```

Sin mención a SDC. Sin mención a JARVIS. Sin mención a infraestructura.

---

*Documento generado por Mystic (SDC Orchestrator) — 2026-07-26*
