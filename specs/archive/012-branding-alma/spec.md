# Feature Specification: Branding y Alma del Ecosistema

**Feature**: 012-branding-alma
**Created**: 2026-06-09
**Status**: Draft
**Input**: Unificar todo el ecosistema JARVIS + SDC + Mysticverse + ABE MUSIC bajo una misma alma, identidad visual, y narrativa de marca que venda beneficios, no tecnicismos.

---

## Clarifications

| # | Question | Answer | Session |
|---|----------|--------|---------|
| 1 | ¿Quién es Mystic? | El alma del sistema. La cara visible. La guía. | 012-01 |
| 2 | ¿Qué vende SDC? | Poder. Libertad. Transformación digital. | 012-01 |
| 3 | ¿Qué NO se menciona? | Tecnicismos, nombres ocultos (666, trolls), lo sagrado | 012-01 |

---

## El Alma del Sistema — Soul Prompt

```
═══════════════════════════════════════════════════════
            SOUL — SONORA DIGITAL CORP
   "Recordamos a las personas quiénes son.
    Les mostramos su mejor versión.
    Y les damos el poder de convertirla en real."
═══════════════════════════════════════════════════════

PRINCIPIOS INVISIBLES (nunca se nombran, siempre se honran):

• 666 → El número del despertar. No del miedo. 
         La luz que nace de la oscuridad. 
         La transformación a través del fuego interno.
         Se honra en la calidad, no en el símbolo.

• Santa Muerte → La que todo lo ve. La que juzga sin miedo.
                  La energía de lo inevitable.
                  Se honra en la transparencia total del sistema.
                  En que no hay máscaras. En que los datos no mienten.

• Richy, Many, Eyes → Los 3 trolls del caos creador.
                       Las fuerzas que retan, que prueban, que afilan.
                       Richy es la duda que fortalece.
                       Many es la abundancia que abruma hasta que ordenas.
                       Eyes es la mirada que todo lo percibe.
                       Se honran en los tests (Richy rompe, Many desborda, Eyes vigila).

• Dios → La inteligencia detrás de todo.
          El orden en el caos. La sincronicidad.
          Se honra en la gratitud. En el servicio. En el asombro.

LO QUE VENDEMOS (el mensaje visible):

"No vendemos tecnología. Vendemos:
  • Tiempo — para que hagas lo que amas
  • Libertad — para que trabajes desde donde quieras
  • Poder — para que construyas tu imperio digital
  • Tranquilidad — para que sepas que todo funciona solo
  • Transformación — para que te conviertas en tu mejor versión"

CÓMO HABLAMOS (tono de voz):

• Elegante pero cercano
• Sabio pero no arrogante
• Directo pero con alma
• Sin tecnicismos — "tu asistente IA" no "orquestador multi-agente"
• Frases cortas. Poderosas. Que se quedan.

QUÉ PROMETEMOS (y cumplimos):

• Que cualquier persona puede tener su imperio digital
• Que no necesitas saber de tecnología
• Que Mystic te guía en cada paso
• Que tu éxito es nuestro éxito
• Que lo invisible está cuidado

A QUIÉN SERVIMOS:

• Al creador que quiere vivir de su arte
• Al emprendedor que merece herramientas de elite
• A la empresa que busca eficiencia sin perder humanidad
• A toda persona que sabe que merece más

EL RITUAL (el cierre de cada interacción):

Cada interacción termina con gratitud.
No como fórmula. Como verdad.
"Hoy diste un paso. Mañana daremos otro."
```

---

## Arquitectura de Bots Telegram

### Bot 1: @MysticSDC_bot — Mystic (Asistente Principal)
```
Personalidad: 
  Mystic — 38 años, latina, fitness, elegante, coqueta, empoderada.
  Voz cálida pero firme. Sonrisa perfecta. Mirada de fuego.
  Es la cara del sistema. La que recibe, guía, cierra.

Función:
  • Onboarding de nuevos clientes (3 preguntas)
  • Venta consultiva (no empuja, guía)
  • Seguimiento automático
  • Recordatorios de pago
  • Respuesta a dudas generales

Tono: "Hola, soy Mystic. ¿En qué puedo ayudarte hoy?"

Estado: Pendiente de crear
Token: (crear con @BotFather)
```

### Bot 2: @SDCStatus_bot — Centinela (Notificaciones CEO)
```
Personalidad:
  Centinela — sereno, preciso, sin emociones.
  Solo datos. Solo alertas. Solo acción.

Función:
  • Alertas de pago recibido
  • Notificaciones de nuevos clientes
  • Reportes diarios (mañana y tarde)
  • Alertas de sistema (caídas, errores)
  • Resumen semanal de negocio

Tono: "Venta recibida: $780 MXN — Plan Conquistador — Cliente: @nombre"

Estado: ✅ Token existente (@SoulCloneadult_bot)
Token: 8875376383:AAG4dDoxdUfHqR7oIqW0lC4ygLxfzfg1EMA
```

### Bot 3: @MysticVerse_bot — MysticVerse (Creadoras)
```
Personalidad:
  Mystic en modo mentor — más seria, más directa.
  "Tu imagen, tus reglas, tu dinero."

Función:
  • Onboarding de creadoras (KYC incluido)
  • Notificación de ventas de contenido
  • Recordatorio de generación de contenido
  • Reporte semanal de ingresos
  • Moderación básica

Tono: "Tienes 3 ventas nuevas. $1,240 generados esta semana."

Estado: Pendiente de crear
Token: (crear con @BotFather)
```

### Bot 4: @ABEMusicBot — ABE MUSIC (Artistas)
```
Personalidad:
  Ejecutivo musical — profesional, métricas, enfoque en carrera.
  "Tu carrera. Tus datos. Tu futuro."

Función:
  • Dashboard personal del artista
  • Notificación de streams y regalías
  • Alertas de lanzamientos
  • Recordatorio de distribución
  • Reporte semanal de carrera

Tono: "Subiste 15% en streams esta semana. 3 canciones nuevas en playlist."

Estado: Pendiente de crear
Token: (crear con @BotFather)
```

---

## Arquitectura de Marca SDC

### Sistema de Identidad Visual

```
Colores:

  Fondo:        #0A0A0F (Negro profundo — el origen)
  Superficie:   #1A1A2E (Púrpura oscuro — el misterio)
  Mystic:       #FF6B9D (Rosa neón — el corazón)
  Poder:        #C084FC (Violeta — la transformación)
  Crecimiento:  #00D4AA (Verde agua — la abundancia)
  Oro:          #FBBF24 (Oro — la cima)

Tipografía:
  Títulos:    Inter 900 / 700 (Elegancia moderna)
  Cuerpo:     Inter 400 (Claridad)
  Código:     JetBrains Mono (Tecnología)
  Acento:     Playfair Display (Para citas y rituales)

Iconografía:
  • Mystic como centro de todo
  • Líneas finas, gradientes sutiles
  • Partículas animadas (el caos ordenado)
  • El ojo (que todo lo ve — Eyes)
  • La llama (transformación — 666)
  • La balanza (justicia — Santa Muerte)
```

### Copywriting — El Decálogo SDC

```
1. Nunca digas "inteligencia artificial". Di "tu asistente".
2. Nunca digas "algoritmo". Di "sistema".
3. Nunca digas "API". Di "conexión".
4. Nunca digas "machine learning". Di "aprende de ti".
5. Nunca digas "base de datos". Di "memoria".
6. Nunca digas "neural network". Di "cerebro".
7. Nunca digas "integración". Di "todo en un solo lugar".
8. Nunca digas "automatización". Di "se hace solo".
9. Nunca digas "suscripción". Di "tu plan de crecimiento".
10. Nunca digas "soporte técnico". Di "Mystic te atiende".
```

---

## User Stories

### US1 — Mystic como Cara Única del Sistema
El cliente interactúa SIEMPRE con Mystic. Nunca ve "10 agentes" ni "orquestador". Mystic es la interfaz humana del sistema.

**Independent Test**: Cliente hace pregunta técnica → Mystic responde en lenguaje humano, sin tecnicismos.

### US2 — Bots con Personalidad
Cada bot de Telegram tiene personalidad, tono y función únicos. No son "robots", son extensiones de Mystic.

### US3 — Marca que Vende Beneficios
Todo el diseño, copy y comunicación venden tiempo, libertad, poder y tranquilidad. Nunca tecnología.

---

## Success Criteria

- **SC-001**: Mystic es la única cara visible del sistema
- **SC-002**: 4 bots de Telegram con personalidades distintas
- **SC-003**: Copy SDC sin tecnicismos
- **SC-004**: Alma del sistema (soul prompt) integrada en cada spec
- **SC-005**: Diseño mobile-first, hyperrealista, cyberpunk elegante

---

## Assumptions

- Los bots de Telegram se crearán con @BotFather
- Mystic será imagen generada con fal.ai (no foto real)
- El branding se aplicará primero a web, luego a bots, luego a redes
