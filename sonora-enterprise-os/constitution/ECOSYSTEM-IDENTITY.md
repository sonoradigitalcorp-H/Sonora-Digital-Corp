# 🧠 Mapa Mental: ¿Cuándo usar JARVIS, Hermes u OpenClaw?

## Los 3 Sistemas (y sus personalidades)

```
         ╔═══════════════════════════════════════════════╗
         ║            TÚ (El Operador)                   ║
         ║   Hablas · Escribes · Decides                 ║
         ╚═══════════════════════════════════════════════╝
                      │           │           │
        ┌─────────────┘           │           └─────────────┐
        ▼                         ▼                         ▼
┌───────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   JARVIS      │    │     HERMES       │    │    OPENCLAW      │
│  "El Cerebro" │    │  "La Voz"       │    │  "Las Manos"     │
│  Piensa       │    │  Conversa        │    │  Ejecuta         │
│  Recuerda     │    │  Escucha         │    │  Integra         │
│  Analiza      │    │  Notifica        │    │  Automatiza      │
└───────────────┘    └──────────────────┘    └──────────────────┘
```

---

## 📍 CUÁNDO USAR CADA UNO

### 🧠 JARVIS — "El Cerebro" (Puerto 5174 / API)

**Personalidad**: Ingeniero meticuloso que todo lo recuerda y analiza.

| Circunstancia | Comando | Ejemplo |
|--------------|---------|---------|
| Investigación profunda | `/research: <tema>` | "investiga cómo funciona GPT-4V" |
| Análisis de código | `/code: <archivo>` | "analiza el archivo orchestrator.py" |
| Buscar en mi memoria | `/memory: <consulta>` | "cuándo configuré Mercado Pago" |
| Generar código | "escribe un script que..." | "escribe un scraper para precios" |
| Revisar calidad | "revisa este código" | "revisa el archivo payments.py" |
| Crear spec SDD | "crea spec para..." | "crea spec para autenticación biométrica" |
| **NO usar** | Tareas de voz rápidas o mensajería | "dile a X que..." (usa Hermes) |

**Acceso**: Web UI `http://localhost:5174` · Terminal · Hermes Desktop (vía bridge)

---

### 🗣️ HERMES — "La Voz" (Puerto 8000 / Desktop / Telegram)

**Personalidad**: Recepcionista multilingüe que te escucha y responde donde sea.

| Circunstancia | Comando | Ejemplo |
|--------------|---------|---------|
| **Voz rápida** | `Ctrl+B + hablar` | "Hermes, ¿qué hora es?" |
| Mensajería | Enviar mensaje | "dile a Juan que llegaré tarde" |
| Notificaciones | Automático | "avísame cuando termine el deploy" |
| Automatización n8n | "ejecuta workflow X" | "ejecuta el backup nocturno" |
| Multi-plataforma | Telegram/WhatsApp | "por Telegram, pregúntale a JARVIS..." |
| **NO usar** | Análisis de código complejo | (pasa a JARVIS via bridge) |

**Acceso**: Desktop App (Ctrl+B) · `https://t.me/<tu_bot>` · WhatsApp

---

### 🛠️ OPENCLAW — "Las Manos" (Puerto 18789)

**Personalidad**: Artesano con 55 herramientas especializadas que hace de todo.

| Circunstancia | Comando | Ejemplo |
|--------------|---------|---------|
| Navegación web | `browser` | "abre Chrome y navega a..." |
| Pagos/Stripe | `stripe` | "crea un checkout de $50" |
| Redes sociales | `social-media` | "publica en Twitter que..." |
| GitHub | `github` | "crea un PR con estos cambios" |
| Imágenes (Fal.ai) | `fal-ai` | "genera una imagen de..." |
| Base de datos | `supabase` | "consulta la tabla usuarios" |
| **NO usar** | Tareas que requieren contexto histórico | (pasa a JARVIS vía bridge) |

**Acceso**: JARVIS vía `unified_bridge.py` · OpenClaw CLI · MCP tools

---

## 🔄 FLUJO RECOMENDADO: La Cadena de Oro

```
TÚ (hablas) 
    → HERMES (escucha, decide quién ejecuta)
        → JARVIS (investiga, analiza, recuerda) 
            → OPENCLAW (ejecuta skills) 
                → HERMES (te responde en voz)
```

### Ejemplo real:

1. **Tú**: "Hermes, necesito saber cómo configuré Mercado Pago y crear un nuevo checkout"
2. **Hermes**: Recibe voz → pregunta a JARVIS vía MCP
3. **JARVIS**: Busca en Engram/Neo4j → encuentra spec de Mercado Pago
4. **JARVIS**: Delega a OpenClaw → ejecuta skill `stripe` + `paymentsdb`
5. **Hermes**: Toma resultado → te responde en voz

---

## 📊 RESUMEN VISUAL

```
┌───────────────────────────────────────────────────────────────┐
│               MATRIZ DE DECISIÓN RÁPIDA                       │
├──────────────┬───────────┬──────────┬──────────┬──────────────┤
│ NECESITAS... │ JARVIS    │ HERMES   │ OPENCLAW │ EJEMPLO      │
├──────────────┼───────────┼──────────┼──────────┼──────────────┤
│ Investigar   │ ✅ MEJOR  │ ❌       │ ❌       │ research agent│
│ Recordar     │ ✅ MEJOR  │ ❌       │ ❌       │ engram store  │
│ Hablar       │ ❌        │ ✅ MEJOR │ ❌       │ Ctrl+B       │
│ Mensajear    │ ❌        │ ✅ MEJOR │ ❌       │ Telegram     │
│ Pagar        │ ❌        │ ❌       │ ✅ MEJOR │ Stripe skill │
│ Navegar web  │ ❌        │ ❌       │ ✅ MEJOR │ browser-use  │
│ Codificar    │ ✅ MEJOR  │ ❌       │ ❌       │ code agent   │
│ Automatizar  │ ❌        │ ✅       │ ✅ MEJOR │ n8n+OpenClaw │
│ Redes soc.   │ ❌        │ ❌       │ ✅ MEJOR │ social-media │
│ Crear spec   │ ✅ MEJOR  │ ❌       │ ❌       │ SDD Harness  │
└──────────────┴───────────┴──────────┴──────────┴──────────────┘
```
