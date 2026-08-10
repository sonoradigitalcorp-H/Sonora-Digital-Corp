# Aztrotech — Campañas Outbound Multi-Nicho

## Sistema Completo de Captación y Seguimiento de Leads

---

## 1. Seis Campañas por Nicho

### Campaña 1: 🍽️ Sazón Digital — Restaurantes
| Campo | Valor |
|-------|-------|
| **Nombre** | Sazón Digital |
| **Target** | Dueños de restaurantes, fondas, cocinas económicas en Hermosillo |
| **Leads/día** | 20 (scraper Google Business + redes) |
| **Agente voz** | María — "recepcionista que habla como tu mejor mesera" |
| **Mensaje inicial** | "¿Sabías que puedes recibir pedidos por WhatsApp sin tener que contestar?" |
| **Lead frío** | SMS/WA 1x/semana: "María ya tomo 3 pedidos hoy sin que toques el teléfono" |
| **Lead tibio** | Llamada cada 3 días: caso real de restaurante similar + demo del orbe |
| **Lead caliente** | → César en vivo (notificación inmediata) |
| **CTA final** | Referido: "Invita a otro restaurante y ambos tienen 10% OFF" |

### Campaña 2: 👗 Moda AI — Tiendas de Ropa
| Campo | Valor |
|-------|-------|
| **Nombre** | Moda AI |
| **Target** | Dueñas de boutiques, tiendas de ropa, accesorios en HMO |
| **Agente voz** | Sofía — "vendedora que conoce tu catálogo al 100%" |
| **Lead frío** | WA: "Sofía ya vendió 5 prendas hoy. ¿Cuántas vendiste tú?" |
| **Lead tibio** | Llamada: "Te muestro cómo Sofía atiende clientes mientras tú descansas" |

### Campaña 3: 🦷 Sonrisa Inteligente — Clínicas Dentales
| Campo | Valor |
|-------|-------|
| **Nombre** | Sonrisa Inteligente |
| **Target** | Dentistas, clínicas dentales, ortodoncia |
| **Agente voz** | Dra. Carmen — "asistente que agenda y recuerda citas" |
| **Lead frío** | WA: "El 30% de tus pacientes no confirman cita. Dra. Carmen lo hace por ti." |

### Campaña 4: 💈 Estilo 360 — Barberías y Salones
| Campo | Valor |
|-------|-------|
| **Nombre** | Estilo 360 |
| **Target** | Barbershops, salones de belleza, estilistas |
| **Agente voz** | Valentina — "recepcionista que nunca olvida un corte" |
| **Lead frío** | WA: "Tus clientes quieren agendar desde WhatsApp. Valentina los atiende 24/7." |

### Campaña 5: ☕ Café Conectado — Cafés
| Campo | Valor |
|-------|-------|
| **Nombre** | Café Conectado |
| **Target** | Cafeterías, bares de especialidad, panaderías |
| **Agente voz** | Barista AI — "toma pedidos anticipados para llevar" |

### Campaña 6: 🏢 PyME al Futuro — Negocios Locales
| Campo | Valor |
|-------|-------|
| **Nombre** | PyME al Futuro |
| **Target** | Agencias, consultorías, despachos, servicios |
| **Agente voz** | Ejecutiva — "captura leads calificados 24/7" |

---

## 2. Pipeline de Contacto (Cold → Warm → Hot)

```
                          ┌─────────────────┐
                          │  20 leads/día    │
                          │  (scraper auto)  │
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │  📞 LLAMADA VOZ │  ← Agente IA del nicho
                          │  (FreeSWITCH)   │
                          └────────┬────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                              │
              ┌─────▼─────┐                 ┌──────▼──────┐
              │  CONTESTÓ  │                 │ NO CONTESTÓ │
              └─────┬─────┘                 └──────┬──────┘
                    │                              │
        ┌───────────▼───────────┐          ┌───────▼────────┐
        │  Clasificar lead      │          │  📱 WhatsApp   │
        │  (lead_classifier.py) │          │  "Te llamé..." │
        └───────────┬───────────┘          │  + link orbe   │
                    │                      └───────┬────────┘
        ┌───────────┼───────────┐                  │
        ▼           ▼           ▼                  ▼
    ┌──────┐  ┌────────┐  ┌────────┐     ┌────────────────┐
    │ COLD │  │  WARM  │  │  HOT   │     │  Si no abre WA │
    └──┬───┘  └───┬────┘  └───┬────┘     │  → SMS + IG DM │
       │          │           │          └────────────────┘
       ▼          ▼           ▼
  WA 1x/sem   Llamada     → César
  (beneficio  cada 3d     notif. inmediata
   diferente)  (caso real) + agenda orbe
```

---

## 3. Seguimiento con Beneficios Diferentes

Cada interacción muestra un beneficio DISTINTO (nunca repetir el mismo):

| Interacción | Medio | Mensaje (beneficio) |
|-------------|-------|---------------------|
| #1 Llamada | 📞 Voz | "Atención 24/7 a tus clientes sin que pagues horas extra" |
| #2 WA | 📱 Texto | "Clientes te escriben y el agente responde AL INSTANTE" |
| #3 Llamada | 📞 Voz | "Nunca más pierdes una venta porque no contestaste" |
| #4 WA | 📱 Texto | "Tus clientes pueden PEDIR y PAGAR desde WhatsApp" |
| #5 Llamada | 📞 Voz | "Tienes un VENDEDOR digital que trabaja mientras duermes" |
| #6 WA | 📱 Texto | "Sabes cuántos leads generaste HOY en tiempo real" |
| #7 Llamada | 📞 Voz | "CASO REAL: Restaurante X aumentó 40% sus pedidos en 1 mes" |
| #8 WA | 📱 Texto | "Tu competencia YA tiene agente IA. ¿Tú?" |

**Cierre:** En cada interacción se comparte el **link de referidos**:
> "Invita a otro negocio como el tuyo y AMBOS reciben 10% de descuento en su siguiente mes"

---

## 4. Sistema de Referidos

```
Tú refieres a → Tu amigo contrata → AMBOS reciben 10% OFF el siguiente mes
     ↓
Link único por cliente: wa.me/526621072254?text=Quiero%20mi%2010%25%20off%20(referido%20por:[NOMBRE])
```

- **Link único** por cada lead que contrata
- Se comparte en CADA interacción (al final, después del beneficio)
- 10% para el referidor en su siguiente mes
- 10% para el nuevo cliente en su primer mes
- Tracking automático en Postgres + Engram

---

## 5. Tenants + Persistencia Eterna

### Creación automática al convertir lead
```
Cada lead que contrata →
  1. tenant_id = slug(nombre_negocio)
  2. Carpeta: 02_Client_Projects/<tenant_id>/03_Media_Assets/{Audio,Video,Images,Documents}
  3. Postgres: contacts + interactions
  4. Engram: memoria persistente tipo "persona-<id>"
  5. Qdrant: colección kb_<tenant_id>
  6. Config.yaml heredado de Aztrotech con overrides
```

### Datos que persisten por persona para siempre
| Dato | Dónde | Formato |
|------|-------|---------|
| Nombre, empresa, teléfono | Postgres (contacts) | Relacional |
| Interacciones completas | Postgres (interactions) | Relacional + JSONB |
| Conversaciones texto/audio | Engram (type=interaction) | Vectorial + metadata |
| Preferencias del cliente | Engram (type=preference) | Vectorial |
| Historial emocional | Engram (type=emotion) | Vectorial |
| Media (audios, imágenes) | Carpeta tenant | Archivos + path en DB |
| Lead score histórico | Postgres + Engram | Híbrido |

---

## 6. Proyección Mensual

| Campaña | Leads/día | Leads/mes | Tasa Conv. | Clientes | Ingreso Est. |
|---------|-----------|-----------|-----------|----------|-------------|
| Sazón Digital | 20 | 400 | 5% | 5 | $1,495/mes |
| Moda AI | 20 | 400 | 4% | 4 | $1,196/mes |
| Sonrisa Inteligente | 15 | 300 | 6% | 3 | $897/mes |
| Estilo 360 | 15 | 300 | 5% | 3 | $747/mes |
| Café Conectado | 10 | 200 | 4% | 2 | $598/mes |
| PyME al Futuro | 10 | 200 | 3% | 2 | $598/mes |
| **Total** | **90** | **1,800** | **~4.5%** | **19 clientes** | **$5,531/mes** |

*Proyectado mes 3 (cuando maduran campañas)*

**Costo leads:** $0 (scraper orgánico) + $0.013/llamada ≈ $23 USD/mes (1,800 llamadas)
**Margen sobre paquetes:** 71-78%

---

## 7. Stack que lo Hace Posible

```
📞 FreeSWITCH (SIP Telnyx) → llamadas a $0.013/min
🎤 faster-whisper → STT local (int8, CPU)
🧠 DeepSeek V4 Flash → razonamiento + lead scoring
🔊 edge-tts → TTS natural (es-MX-DaliaNeural)
🗄️ Postgres → datos relacionales (contactos, interacciones)
🧠 Engram → memoria persistente eterna por persona
🔍 Qdrant → RAG con conocimiento del negocio
🤖 Hermes + OpenClaw → orquestación multi-agente
```

Sin Twilio · Sin ElevenLabs · Sin dependencias mensuales caras.

---

*Creado para César Holguín — AstroTech / Sonora Digital Corp — Agosto 2026*
---

## 8. Paquetes Detallados con ROI

### 🌙 Despertar — $15,000 Setup + $299/mes
*Para el negocio que quiere probar la IA sin riesgo*

| Componente | Incluye |
|-----------|---------|
| Setup inicial | $15,000 MXN (1 vez) |
| Agente de voz | 1 agente (Sofía, María o Dra. Carmen según nicho) |
| Interacciones/mes | 100 llamadas + 500 WA |
| Memoria del agente | ✅ 1 mes incluida |
| Canales | 1 (WhatsApp o Telegram) |
| Clon de voz | ✅ Básico (30s) |
| Link de referidos | ✅ (10% OFF al referir) |
| Video personalizado | ✅ 1 video/mes para lead caliente |
| Dashboard | ✅ Básico (transcripciones + resumen diario) |
| **Mantenimiento mensual** | **$299 MXN** |
| **ROI estimado** | **5x en 3 meses** |

**Upgrade memoria:** +$99/mes por memoria extendida (6 meses historial)

### 🚀 Crecer — $35,000 Setup + $1,499/mes
*Para el negocio que quiere automatizar sus ventas*

| Componente | Incluye |
|-----------|---------|
| Setup inicial | $35,000 MXN (1 vez) |
| Agentes de voz | 3 agentes (Recepción + Ventas + Soporte) |
| Interacciones/mes | 500 llamadas + 2,000 WA |
| Memoria del agente | ✅ 6 meses incluida |
| Canales | 3 (WhatsApp + Telegram + Llamadas) |
| Clon de voz profesional | ✅ Ajuste de tono y emoción |
| CRM con scoring BANT | ✅ Automático |
| Campañas outbound | ✅ 5 simultáneas |
| Automatización redes sociales | ✅ Comentario → ebook/slide/cita |
| Video personalizado | ✅ 4 videos/mes (1 por lead caliente) |
| Link de referidos | ✅ Personalizado por cliente |
| Scraper de leads | ✅ 20 leads/día automático |
| Dashboard avanzado | ✅ Métricas en tiempo real |
| Memoria persistente | ✅ 6 meses de historial completo |
| **Mantenimiento mensual** | **$1,499 MXN** |
| **ROI estimado** | **8x en 6 meses** |

**Upgrade memoria:** +$499 por 6 meses extra · +$999 por 1 año extra

### 👑 Transformar — $75,000 Setup + $3,999/mes
*Para la empresa que quiere su propio ecosistema digital*

| Componente | Incluye |
|-----------|---------|
| Setup inicial | $75,000 MXN (1 vez) |
| Agentes de voz | Ilimitados (todos los roles + custom) |
| Interacciones/mes | Ilimitadas |
| Memoria del agente | ✅ 1 año incluida |
| Canales | Ilimitados (WA + TG + web + redes + API) |
| White-label completo | ✅ Tu marca, tu dominio, tu logo |
| Dashboard 3D | ✅ Tipo JARVIS |
| API dedicada | ✅ REST + SDK |
| Evolution Engine | ✅ Auto-mejora cada 24h |
| Agentes swarm | ✅ Multi-agente coordinado |
| Fábrica de contenido Pro | ✅ Ilimitada (videos, slides, ebooks) |
| Scraper multi-fuente | ✅ 100 leads/día |
| Account Manager | ✅ Dedicado |
| Memoria perpetua | ✅ Ilimitada (toda la historia del cliente) |
| Link de referidos | ✅ Con tracking y analytics |
| **Mantenimiento mensual** | **$3,999 MXN** |
| **ROI estimado** | **15-20x en 6 meses** |

---

## 9. Memoria del Agente — Planes Independientes

| Plan | Período | Precio | Ideal para |
|------|---------|--------|------------|
| 📝 Básica | 1 mes | $99 MXN | Clientes Despertar que quieren historial |
| 📚 Avanzada | 6 meses | $499 MXN | Clientes Crecer que escalan |
| 🏛️ Eterna | 1 año | $999 MXN | Clientes Transformar que quieren todo |

La memoria incluye: historial completo de conversaciones (voz y texto), preferencias del cliente, lead score histórico, emociones detectadas, productos/servicios consultados, y referidos realizados.

---

## 10. ROI por Tipo de Cliente

### Mediano Ticket (Restaurantes, Tiendas, Barberías)
| Inversión Inicial | Mensualidad | Clientes nuevos/mes | Ingreso extra | ROI |
|------------------|-------------|-------------------|---------------|-----|
| $15,000 + $299/mes | $299 | 5 pedidos extra/día | $4,500/mes | **5x en 3 meses** |
| $35,000 + $1,499/mes | $1,499 | 15 clientes nuevos/mes | $15,000/mes | **8x en 6 meses** |

### Alto Ticket (Clínicas, Consultorías, Agencias)
| Inversión Inicial | Mensualidad | Clientes nuevos/mes | Ingreso extra | ROI |
|------------------|-------------|-------------------|---------------|-----|
| $35,000 + $1,499/mes | $1,499 | 5 pacientes nuevos/mes | $25,000/mes | **10x en 3 meses** |
| $75,000 + $3,999/mes | $3,999 | 15 clientes nuevos/mes | $75,000/mes | **15-20x en 6 meses** |

---

## 11. Beneficios Completos por Paquete (Resumen Visual)

| Beneficio | Despertar | Crecer | Transformar |
|-----------|:---------:|:------:|:-----------:|
| 🤖 Agente IA 24/7 | ✅ 1 | ✅ 3 | ✅ ∞ |
| 📞 Llamadas/mes | 100 | 500 | ∞ |
| 💬 WhatsApp + Telegram | ✅ | ✅ | ✅ |
| 🎤 Clon de voz | ✅ Básico | ✅ Profesional | ✅ Premium |
| 🧠 Memoria agente | 1 mes | 6 meses | 1 año+ |
| 📊 Scoring leads | ❌ | ✅ BANT | ✅ BANT+ |
| 🎯 Campañas outbound | ❌ | ✅ 5 | ✅ ∞ |
| 📱 Auto-redes | ❌ | ✅ | ✅ |
| 🎬 Video personalizado | 1/mes | 4/mes | ∞ |
| 🎁 Link referidos 10% | ✅ | ✅ | ✅ |
| 🔍 Scraper leads/día | ❌ | 20 | 100 |
| 🖥️ Dashboard | Básico | Avanzado | 3D JARVIS |
| 🏷️ White-label | ❌ | ❌ | ✅ |
| 🔄 Evolution Engine | ❌ | ❌ | ✅ |
| 👤 Account Manager | ❌ | ❌ | ✅ |
| 📈 ROI estimado | 5x | 8x | 15-20x |

---

*Creado para César Holguín y Luis Daniel Guerrero — AstroTech / Sonora Digital Corp — Agosto 2026*
