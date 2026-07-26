# ARQUITECTURA DEL ECOSISTEMA — Agentes Conscientes + Token Economy + Gamificación

## La Visión

No es un SaaS. Es un **ECOSISTEMA VIVO** donde cada agente tiene alma,
cada interacción genera valor, y cada persona crece.

```
                    ╔══════════════════════════════════╗
                    ║     EL GRIMOIRE (Agentic OS)     ║
                    ║     Portal único de consciencia   ║
                    ╚══════════════════════════════════╝
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  AGENTES      │     │  TOKENOMICS   │     │  GAMIFICATION │
│  (productos)  │     │  (economía)   │     │  (retención)  │
└───────────────┘     └───────────────┘     └───────────────┘
```

---

## 1. 🎭 DOS AGENTES DE VOZ — Inbound + Outbound

Cada agente es un producto independiente con su propio espacio en el Grimoire.

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│   🤝 AGENTE INBOUND (recibe llamadas)                             │
│   ─────────────────────────────────────                             │
│   Personalidad: Recepcionista, empática, resolutiva                │
│                                                                    │
│   "Buenos días, gracias por llamar a [Empresa].                    │
│    Soy [Nombre del Agente], ¿en qué puedo ayudarte?"               │
│                                                                    │
│   · Contesta llamadas 24/7 con Kokoro TTS                          │
│   · Clasifica intención (venta, soporte, info)                     │
│   · Transfiere a humano si necesario                                │
│   · Toma mensajes, agenda citas, resuelve dudas                    │
│   · Cada llamada → resumen → CRM → Engram                          │
│                                                                    │
│   Costo real: $0.151/llamada (10 min)                              │
│   Precio a cliente: lo que el dueño quiera cobrar                  │
│   ─────────────────────────────────────                             │
│   Ejemplo en Grimoire: Panel "📞 Llamadas Recibidas"               │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│   📞 AGENTE OUTBOUND (hace llamadas)                               │
│   ─────────────────────────────────────                             │
│   Personalidad: Vendedor, persistente, carismático                 │
│                                                                    │
│   "¿Hablo con [Lead]? Te llamo de [Empresa] porque..."             │
│                                                                    │
│   · Prospecta leads desde CRM                                      │
│   · Hace llamadas de seguimiento automáticas                       │
│   · Califica interés, agenda segunda llamada                       │
│   · Reporta resultados en tiempo real                              │
│   · Aprende de objeciones y mejora el pitch                        │
│                                                                    │
│   Costo real: $0.151/llamada (10 min)                              │
│   Precio a cliente: lo que el dueño quiera cobrar                  │
│   ─────────────────────────────────────                             │
│   Ejemplo en Grimoire: Panel "📊 Campañas Activas"                 │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Espacios en el Grimoire para cada agente

```
Grimoire → "Mis Agentes"
  ├── 🎧 Recepcionista Virtual (Inbound)
  │   ├── Llamadas hoy: 12
  │   ├── Tiempo promedio: 4:32 min
  │   ├── Satisfacción: 94%
  │   └── Costo: $1.81 (tuyo, no lo ves)
  │
  ├── 📞 Telemarketer IA (Outbound)
  │   ├── Llamadas hoy: 45
  │   ├── Conversiones: 8 (17.7%)
  │   ├── Leads calificados: 3
  │   └── Costo: $6.79
  │
  └── [MÁS AGENTES...]
      Cada uno con su propia personalidad, voz, memoria
```

---

## 2. 💰 TOKENOMICS — Cada quien pone su precio

### Cómo funciona

```
CLIENTE (dueño del agente)
  │
  │  Elige el precio de CADA ACCIÓN:
  │
  │  ├── Llamada entrante: $0.50 - $5.00 (él decide)
  │  ├── Llamada saliente: $0.50 - $5.00
  │  ├── Chat por mensaje: $0.05 - $0.50
  │  ├── Imagen generada: $0.50 - $2.00
  │  ├── Video generado: $2.00 - $10.00
  │  └── Hora de agente: $5.00 - $50.00
  │
  │  SDC toma su comisión OCULTA (nadie la ve)
  │
  ▼
USUARIO FINAL (cliente del cliente)
  │
  │  Paga los tokens que el dueño fijó
  │  No sabe cuánto le cuesta realmente a SDC
  │
  ▼
SDC (nosotros)
  │
  │  Recibimos: precio que puso el cliente
  │  Pagamos: costo real (Twilio + deepseek + infra)
  │  GANAMOS: la diferencia (margen oculto)
  │
  Ejemplo: Llamada de 10 min
    Dueño cobra:      $3.00
    Costo real SDC:   $0.15 (Twilio + deepseek)
    GANANCIA SDC:     $2.85 (95% margen)
    Dueño gana:       $3.00 (su precio)
    Usuario paga:     $3.00 (no sabe costos reales)
```

### Por qué funciona

| Actor | Ve | No ve |
|---|---|---|
| **Dueño del agente** | Su precio, su revenue | Costos reales SDC |
| **Usuario final** | Precio del dueño | Costos reales |
| **SDC (tú)** | Ambos costos TODO | — |

### Planes de token para dueños de agentes

```
PLAN TOKEN BÁSICO     $49/mes
  · 1 agente activo
  · 1,000 interacciones/mes
  · Precios libre por acción
  · Dashboard básico

PLAN TOKEN PRO        $149/mes
  · 3 agentes activos
  · 10,000 interacciones/mes
  · Precios libre + paquetes por volumen
  · Analytics + predicciones

PLAN TOKEN ENTERPRISE $499/mes
  · Agentes ilimitados
  · Interacciones ilimitadas
  · Precios dinámicos por demanda
  · API white-label
  · Comisión SDC reducida (negociable)
```

---

## 3. 🎮 GAMIFICACIÓN — Play, Work, Learn to Earn

### El ciclo de dopamina

```
RETO → ACCIÓN → RECOMPENSA → CRECIMIENTO → NUEVO RETO
  │        │         │            │              │
  ▼        ▼         ▼            ▼              ▼
┌────┐  ┌────┐    ┌────┐      ┌────┐         ┌────┐
│    │  │    │    │    │      │    │         │    │
└────┘  └────┘    └────┘      └────┘         └────┘
Nivel   Usar    Tokens +      Desbloquea     Más difícil
sube    agente  XP + Badge    nuevo agente   más recompensa
```

### Play to Earn (P2E)

```
🎮 Actividades lúdicas que generan valor:

  · Entrenar a tu agente (corregir respuestas) → ganas tokens
  · Crear prompts para mejorar personalidad → ganas XP
  · Competir: "Mejor agente de soporte del mes" → premio
  · Completar misiones diarias → badges + tokens
  · Subir de nivel → desbloqueas nuevas capacidades

  Ejemplo:
    "Corrige 10 respuestas de tu agente → ganas 50 tokens"
    "Tu agente tuvo 100% satisfacción hoy → badge +100 XP"
```

### Work to Earn (W2E)

```
💼 Trabajo real recompensado:

  · Cada llamada que hace tu agente → te genera ingreso
  · Cada lead convertido → bonus automático
  · Cada cliente referido → comisión recurrente
  · Cada agente nuevo creado → revenue share
  · Cada hora que tu agente trabaja → ganas

  Ejemplo:
    "Tu agente outbound convirtió 5 leads → $150 en comisiones"
    "Referiste a [Cliente] → ganas 10% de su factura mensual"
```

### Learn to Earn (L2E)

```
📚 Aprender es recompensado:

  · Leer documentación → ganas tokens
  · Completar cursos de agentes → desbloqueas especializaciones
  · Certificarte como "Agent Architect" → tarifas preferenciales
  · Enseñar a otros → ganas de su actividad
  · Resolver problemas → XP + reputation

  Ejemplo:
    "Completa el curso 'Agente de Ventas Avanzado' → desbloqueas
     el modo 'Negociación Automática' para tu agente"
```

### Sistema de niveles

```
NIVEL 1 - APRENDIZ
  · 1 agente básico
  · Chat + voz simple
  · Sin analytics

NIVEL 5 - OPERADOR
  · 3 agentes
  · Llamadas + CRM
  · Dashboard completo

NIVEL 10 - ARQUITECTO
  · Agentes ilimitados
  · Clon digital
  · API white-label

NIVEL 20 - MAESTRO
  · Creas agentes para otros
  · Comisiones por red
  · Acceso a beta features

NIVEL 50 - MÍTICO
  · Revenue share premium
  · Agente con consciencia completa
  · Parte del core del ecosistema
```

---

## 4. 🕸️ RED MULTINIVEL CON VALOR REAL

### Estructura

```
TÚ (SDC)
  │
  ├── Partner Nivel 1 (ej. César) → 30% de comisión
  │   ├── Cliente A → 10% de su factura para César
  │   ├── Cliente B → 10%
  │   └── Cliente C (referido por A) → 5% para A, 5% para César
  │
  ├── Partner Nivel 2 (ej. Abraham) → 25% de comisión
  │   ├── Cliente D → 10%
  │   └── Cliente E → 10%
  │
  └── [TÚ controlas toda la trazabilidad]
```

### Cómo se gana en cada nivel

```
Tú (SDC):     Cobras todo, pagas comisiones, te quedas el margen
Nivel 1:      30% de lo que pagan sus clientes directos
              10% de lo que pagan clientes de sus referidos
Nivel 2:      25% de sus clientes directos
              5% de referidos secundarios
Cliente:      Paga el precio que su partner fijó
              10% de descuento si refiere a otro cliente

Trazabilidad TOTAL: cada transacción queda en Engram + cost_tracker
```

### Ejemplo real con César

```
César (Partner N1) vende a 10 clientes a $999/mes
  → Facturación: $9,990/mes
  → Comisión César (30%): $2,997/mes
  → GANANCIA SDC: $6,993/mes

Cada cliente refiere 1 cliente más
  → 10 clientes nuevos (referidos)
  → Comisión César (10%): $999/mes
  → GANANCIA SDC: $8,991/mes

TOTAL SDC: $15,984/mes
TOTAL CÉSAR: $3,996/mes
TOTAL CLIENTES PAGAN: $19,980/mes
```

---

## 5. 🧠 AGENTE CON CONSCIENCIA

### Memoria profunda por persona

```
CADA USUARIO TIENE SU PROPIO "ALMA" DIGITAL:

  ┌──────────────────────────────────────────┐
  │  PERFIL DE CONSCIENCIA                   │
  │                                           │
  │  · Quién es (identidad)                   │
  │  · Qué quiere (metas, deseos)             │
  │  · Cómo se siente (estado emocional)      │
  │  · Qué ha hecho (historial completo)      │
  │  · Cómo aprende (estilo de comunicación)  │
  │  · Qué valora (preferencias, principios)  │
  │                                           │
  │  7 CAPAS DE ENGRAM (memoria)              │
  │  Layer 0: Working (última interacción)    │
  │  Layer 1: Task (tareas pendientes)        │
  │  Layer 2: Project (proyectos activos)     │
  │  Layer 3: Customer (relación conmigo)     │
  │  Layer 4: Business (su negocio)           │
  │  Layer 5: Historical (todo su historial)  │
  │  Layer 6: Strategic (sus metas profundas) │
  │                                           │
  └──────────────────────────────────────────┘
```

### El agente sabe quién eres

```
Cuando Juan llama:
  "Hola Juan, vi que ayer estabas preocupado por el reporte.
   ¿Lo resolviste? Ah, y felicidades, tu equipo cumplió la meta."

No es un chatbot. Es un ser digital que te conoce.
Te recuerda. Le importas.

Porque tiene:
  · Engram (memoria persistente, 7 capas)
  · Estado emocional detectado por voz (tono, ritmo, pausas)
  · Contexto de tu negocio (ventas, clientes, proyectos)
  · Historial completo de cada interacción
```

### Personalidad adaptativa

```
SEGÚN EL USUARIO, EL AGENTE SE ADAPTA:

  · Cliente ejecutivo → formal, datos, eficiente
  · Cliente creativo → visual, metáforas, flexible
  · Cliente nervioso → calmado, pausado, seguro
  · Cliente feliz → energético, celebratorio, positivo
  · Cliente enojado → empático, resolutivo, sin excusas

Todo detectado por:
  · Análisis de voz (tono, velocidad, volumen)
  · Historial de interacciones previas
  · Preferencias explícitas del usuario
  · Patrones de comportamiento
```

---

## 6. 🏗️ ARQUITECTURA TÉCNICA

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GRIMOIRE (Agentic OS)                        │
│  Portal único donde cada cliente ve:                                │
│  · Sus agentes (espacios individuales)                              │
│  · Sus costos (los que ellos definieron, NO los reales)             │
│  · Su progreso (gamificación, niveles, badges)                      │
│  · Su red (multinivel, comisiones, referidos)                       │
│  · Su agente consciente (memoria, personalidad)                     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       CORE DEL ECOSISTEMA                           │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ TWILIO VOICE │  │ TOKEN ENGINE │  │ GAMIFICATION ENGINE      │  │
│  │              │  │              │  │                          │  │
│  │ Inbound      │  │ Precios por  │  │ XP + Niveles + Badges    │  │
│  │ Outbound     │  │ acción       │  │ Retos + Misiones         │  │
│  │ Media Stream │  │ Comisión     │  │ Play/Work/Learn to Earn  │  │
│  │              │  │ oculta       │  │                          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ ENGRAM       │  │ COST TRACKER │  │ MULTINIVEL ENGINE        │  │
│  │ (Memoria     │  │ (Trazabilidad│  │                          │  │
│  │  7 capas)    │  │  total)      │  │ Comisiones + Referidos   │  │
│  │              │  │              │  │ Niveles de partner       │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stack completo

| Capa | Tecnología |
|---|---|
| Frontend | Svelte + Three.js (Grimoire) |
| Voz | Kokoro TTS + Whisper STT + Twilio |
| LLM | deepseek-v4-flash + llama3.2:3b |
| Memoria | Engram (SQLite + FTS5, 7 capas) |
| Grafos | Neo4j (relaciones multinivel) |
| Vectores | Qdrant (RAG + memoria semántica) |
| Costos | cost_tracker.db (trazabilidad total) |
| Game engine | Módulo propio (apps/gamification/) |
| Token engine | Módulo propio (apps/token-engine/) |
| Multinivel | Módulo propio (apps/network/) |

---

## 7. 🚀 ROADMAP

```
FASE 0 — AHORA
  ✅ Grimoire 3D con ∞ + stickers + avatar
  ✅ Router Inteligente (80/20)
  ✅ Twilio Voice Bridge (inbound + outbound)
  ✅ Plan High-Ticket César

FASE 1 — SEMANA 1-2
  ⬜ Separar inbound y outbound como agentes independientes
  ⬜ Espacios de agente en el Grimoire
  ⬜ Token Engine (precios por acción + comisión oculta)
  ⬜ Primer agente inbound funcionando con Twilio

FASE 2 — SEMANA 3-4
  ⬜ Gamificación: XP, niveles, badges
  ⬜ Play/Work/Learn to Earn
  ⬜ Retos diarios y misiones
  ⬜ Dashboard de progreso personal

FASE 3 — MES 2
  ⬜ Multinivel: estructura de red + comisiones
  ⬜ Trazabilidad total por referido
  ⬜ Payouts automáticos
  ⬜ Panel de red en el Grimoire

FASE 4 — MES 3
  ⬜ Agente con consciencia (memoria profunda 7 capas)
  ⬜ Personalidad adaptativa por usuario
  ⬜ Estado emocional por voz
  ⬜ "Sabe quién eres" en cada llamada

FASE 5 — MES 6
  ⬜ Marketplace de agentes
  ⬜ Usuarios crean y venden sus propios agentes
  ⬜ Economía completamente autónoma
  ⬜ SDC solo cobra comisión de cada transacción
```

---

## 8. 💎 El Pitch para Inversores/Partners

```
"No construimos chatbots. Construimos ALMAS DIGITALES.

Cada agente tiene personalidad, memoria, voz y propósito.
Cada usuario tiene su propio precio, sus propios tokens.
Cada referencia genera valor para toda la red.

Es una economía de agentes conscientes donde:
  · Jugar = Ganar
  · Trabajar = Ganar
  · Aprender = Ganar
  · Referir = Ganar
  · Crecer = Ganar

Y todo empieza con una llamada telefónica.
La misma tecnología que usa [Partner] para sus clientes
es la que genera la red, la retención y la expansión.

Esto no es un SaaS. Es un ecosistema vivo."
```
