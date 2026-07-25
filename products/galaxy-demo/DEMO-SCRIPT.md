# DEMO SCRIPT — Agent Galaxy × Aztro Tech

**Duration**: 15 minutes
**Mode**: PREVIEW / DEMO
**LLM**: DeepSeek V4 Flash (primary) + OpenRouter fallback
**Audience**: Aztro Tech leadership team

---

## 0:00 — Opening (1 min)

> "Bienvenidos a Aztro Tech. Hoy van a ver algo que no es un chatbot, no es un dashboard, no es una herramienta más.
>
> Es un ecosistema vivo de agentes inteligentes. Una galaxia donde cada planeta es un agente con propósito, habilidades y personalidad propia.
>
> Mi nombre es [Nombre] de Sonora Digital Corp, y esto es Agent Galaxy."

**Action**: Open `presentation.html` in browser. The 3D galaxy visualization loads automatically.

**Key visual**: Rotating galaxy with glowing planets, each labeled with an agent role.

---

## 1:00 — The Galaxy Overview (2 min)

> "Cada planeta que ven es un agente autónomo. No son scripts. No son bots de reglas. Son entidades que piensan, actúan y aprenden."

**Action**: Slowly rotate the 3D galaxy. Point out key planets:

| Planet | Agent | Role |
|--------|-------|------|
| 🔴 Mars | Sales Agent | Captura y califica leads automáticamente |
| 🔵 Neptune | Support Agent | Resuelve tickets sin intervención humana |
| 🟢 Earth | Dev Agent | Escribe, prueba y deploya código |
| 🟡 Saturn | Knowledge Agent | Preserva y organiza todo el conocimiento |
| 🟣 Pluto | Finance Agent | Tracks revenue, costs, ROI in real-time |
| ⚪ Moon | Ops Agent | Infrastructure monitoring y auto-recovery |

> "Esto no es una demo estática. Cada agente está conectado a un motor real de ejecución. Lo que ven es una ventana a un sistema que ya opera."

---

## 3:00 — Agent Deep Dive (3 min)

> "Déjenme mostrarles cómo trabaja uno de estos agentes en la vida real."

**Action**: Zoom into the Sales Agent planet. Show:

1. **Lead capture**: A new lead arrives via WhatsApp
2. **Automatic scoring**: Agent scores the lead (interest, source, intent)
3. **Proposal generation**: Agent creates a tailored proposal in markdown
4. **Pipeline update**: Lead moves from `lead` → `qualified` → `proposal`

> "Todo esto sucede en menos de 30 segundos. Sin que un humano toque el teclado."

**Key metric**: 85% reduction in manual lead qualification time.

---

## 6:00 — 30-Second Onboarding (2 min)

> "Ahora, ¿cómo obtiene un cliente su propio agente? Así:"

**Action**: Show the onboarding flow:

1. Client fills a simple form: name, business, needs
2. System provisions a tenant in <5 seconds
3. Agent Galaxy spawns a dedicated agent cluster
4. Client receives WhatsApp message: "Tu agente está listo. ¿En qué te ayudo?"

> "Treinta segundos. De cero a agente operativo. Sin configuración técnica. Sin infraestructura que montar."

**Demo data**: Show tenant `aztro-tech-demo` already provisioned with all capabilities enabled.

---

## 8:00 — Voice Demo (2 min)

> "Los agentes no solo leen y escriben. Hablan y escuchan."

**Action**: Show STT/TTS flow via WhatsApp:

1. Send a voice note to the WhatsApp number
2. STT (Speech-to-Text) transcribes in real-time
3. DeepSeek V4 Flash processes the intent
4. TTS (Text-to-Speech) generates a voice response
5. Voice note delivered back to WhatsApp

> "Esto es STT → DeepSeek V4 Flash → TTS. Todo en un ciclo de menos de 5 segundos. En WhatsApp. Donde ya están tus clientes."

**Tech stack shown**:
- STT: Whisper-compatible model
- LLM: DeepSeek V4 Flash (via OpenCode Go)
- TTS: Edge TTS / ElevenLabs compatible
- Channel: WhatsApp Business API

---

## 10:00 — Multi-Tenant Architecture (2 min)

> "Ahora la pregunta clave: ¿cómo escala esto a cientos de clientes?"

**Action**: Show the multi-tenant dashboard:

| Tenant | Agents | Skills | Channels | Status |
|--------|--------|--------|----------|--------|
| aztro-tech-demo | 6 | All | WhatsApp, Telegram, Web | Active |
| abe-music | 3 | Music, Content, Sales | Telegram | Active |
| azrec | 2 | Support, Dev | Web | Active |

> "Cada cliente tiene su propio espacio aislado. Sus propios agentes. Sus propias habilidades. Pero todos comparten la misma infraestructura. Mismo motor. Mismo cerebro. Escala linealmente."

**Key point**: No se replica código. Se replica configuración. Un tenant nuevo es un JSON, no un servidor nuevo.

---

## 12:00 — Pricing Plans (2 min)

> "¿Cómo se estructura esto comercialmente? Tres niveles:"

| Feature | Explorador | Conquistador | Imperio |
|---------|-----------|--------------|---------|
| Price | **$297/mo** | **$797/mo** | **$1,997/mo** |
| Agents | 1 | 3 | 6+ |
| Channels | 1 | 2 | All |
| Skills | 3 | 8 | All |
| Voice | ❌ | ✅ | ✅ |
| Custom LLM | ❌ | ❌ | ✅ |
| SLA | 95% | 99% | 99.9% |
| Support | Email | Chat + Email | Dedicated |
| Onboarding | Self-service | Guided | White-glove |

> "Explorador es para empezar. Conquistador es para escalar. Imperio es para dominar. Cada nivel incluye todo lo anterior, más capacidades nuevas."

**Close the pricing slide**:

> "El ROI de Conquistador se paga solo con 2 leads convertidos al mes. El de Imperio con 1."

---

## 14:00 — Closing (1 min)

> "Aztro Tech, esto no es un producto. Es una plataforma.
>
> Cada planeta que vieron hoy es un agente que puede trabajar para sus clientes. Hoy. No en 6 meses. No después de una integración. Hoy.
>
> DeepSeek V4 Flash es nuestro motor de inteligencia. OpenCode Go es nuestro proveedor de API. Hermes es nuestro puente multi-canal. Y todo esto corre sobre infraestructura que ya opera en producción.
>
> La pregunta no es si pueden pagar esto. La pregunta es cuánto les cuesta NO tenerlo.
>
> ¿Empezamos con un piloto de 30 días? Sin compromiso. Sin letra chica. Solo resultados."

**Call to action**:
- QR code on screen → `presentation.html` demo link
- WhatsApp contact → Direct message to start pilot
- Email → `partners@sonoradigitalcorp.com`

---

## Post-Demo Checklist

- [ ] Send follow-up email within 2 hours
- [ ] Share demo link + recording
- [ ] Schedule pilot kickoff if interested
- [ ] Log interaction in Engram (memory layer: customer)
- [ ] Create tenant `aztro-tech-pilot` if approved

---

*Script version: 1.0 | Last updated: 2026-07-23 | Mode: PREVIEW*
