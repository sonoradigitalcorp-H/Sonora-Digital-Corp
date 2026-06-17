# Company Operating System — Sonora Digital Corp

## 1. Sales Pipeline

### Trigger
Lead inbound (web, referral, social, WhatsApp)

### Workflow
1. Capture lead → `sdc-crm` (source, contact info, interest)
2. Qualify lead → Lead Qualification (below)
3. Create proposal → Proposal Generation (below)
4. Send proposal → track open/read
5. Follow up → Day 1, 3, 7 cadence
6. Close → agreement signed + payment setup
7. Onboard → Client Onboarding (below)

### Success Criteria
- Lead → qualified: < 24h
- Qualified → proposal sent: < 48h
- Proposal → close: < 7 days
- Close rate: > 30%

### Revenue Impact
- Cada lead cerrado = MRR recurrente
- Tiempo de ciclo afecta cash flow

---

## 2. Lead Qualification

### Trigger
Lead captured in Sales Pipeline

### Questions
1. ¿Qué producto/servicio le interesa?
2. ¿Presupuesto? (range)
3. ¿Timeline? (inmediato, 1 mes, 3 meses)
4. ¿Decisor? (solo o en equipo)
5. ¿Dolor específico? (qué problema quiere resolver)

### Classification
| Tipo | Acción |
|------|--------|
| Hot (responde todo, presupuesto alto, inmediato) | Proposal inmediata |
| Warm (responde parcial, interesado) | Nurture sequence |
| Cold (no responde, baja intención) | Drip campaign |

### Output
- Lead score (1-10)
- Next action + due date

---

## 3. Proposal Generation

### Trigger
Lead qualified as Hot/Warm

### Template
1. **Problema** (su dolor, en sus palabras)
2. **Solución** (nuestro producto, ALINEADO a su problema)
3. **Propuesta de valor** (qué cambia para ellos)
4. **Entregables** (qué reciben exactamente)
5. **Timeline** (cuándo)
6. **Precio** (claro, sin letra chica)
7. **Siguientes pasos** (call to action)

### Rules
- NEVER enviar proposal sin entender el problema
- Pricing: 3 tiers (basic, pro, enterprise) o custom
- Incluir caso de éxito similar si existe

### Approval
- Proposals > $X requiere approval de CEO
- Proposals < $X pueden enviarse directo

---

## 4. Client Onboarding

### Trigger
Agreement signed + payment received

### Steps
1. **Welcome** — Email/WhatsApp de bienvenida + qué esperar
2. **Setup** — Configurar producto/servicio (crear clone, landing, etc.)
3. **Credentials** — Entregar accesos
4. **Training** — Sesión de 30min de uso
5. **First value** — Asegurar que el cliente vea valor en primeros 7 días
6. **Feedback** — Check-in a los 7 días

### Success Criteria
- Cliente activo en plataforma en < 48h
- Primera interacción con valor en < 7 días
- NPS > 8 al día 14

### Automation
- `sdc-cron` tasks para cada paso
- Recordatorios automáticos si se atrasa

---

## 5. Delivery Workflow

### Trigger
Cliente onboarded

### Principle
**El cliente no debería tener que hacer nada. Nosotros operamos.**

### For SoulClone clients
1. Content generation pipeline (text, image, video, audio)
2. Daily/weekly content calendar
3. Engagement monitoring
4. Monthly performance report
5. Optimization loop

### For White Label clients
1. Infra setup (whitelabel domain, branding)
2. Agent configuration
3. Testing + QA
4. Launch
5. Ongoing monitoring

### Delivery Cadence
| Type | Frequency |
|------|-----------|
| Content delivery | Diario / semanal |
| Performance report | Mensual |
| Strategy review | Trimestral |
| Health check | Semanal (automático) |

---

## 6. Support Workflow

### Trigger
Client issue or question

### Tiers
| Tier | Who | Response time | Scope |
|------|-----|---------------|-------|
| T1 | Bot / AI agent | < 5 min | FAQ, config, basic issues |
| T2 | Human agent | < 2 h | Technical issues, complex |
| T3 | Engineering | < 24 h | Bugs, infrastructure |

### SLA
- T1: respuesta inmediata (automático)
- T2: primera respuesta < 2h
- T3: fix < 48h (o workaround en < 24h)

### Escalation Path
T1 → T2 → T3 → CEO (si no se resuelve en 48h)

### Documentation
- Cada ticket deja registro en CRM
- Issues recurrentes → DOCUMENTO_DE_ERRORES.md → fix permanente

---

## 7. Upsell Workflow

### Trigger
Cliente satisfecho + oportunidad identificada

### Signals
- Cliente pide algo fuera de su plan actual
- Cliente supera métricas de uso (engagement, contenido)
- Renovación próxima (30 días antes)
- Cliente pide feature que ya existe en plan superior

### Process
1. Identificar señal
2. Preparar propuesta de upgrade (valor incremental)
3. Presentar en momento adecuado (post-success, pre-renovación)
4. Cerrar upgrade

### Offers
| Current Plan | Upsell To | Value Prop |
|-------------|-----------|------------|
| Basic | Pro | Más contenido, más canales |
| Pro | Enterprise | White label, equipo dedicado |
| Enterprise | Custom | Infra dedicada, SLA premium |

---

## 8. Referral Workflow

### Trigger
Cliente satisfecho (NPS > 8, feedback positivo)

### Process
1. Detectar momento óptimo (post-success, post-positive feedback)
2. Pedir referral (email personalizado)
3. Ofrecer incentivo (1 mes gratis por referral cerrado)
4. Trackear referral en CRM
5. Cuando referral se cierra: activar incentivo + agradecer

### Referral Loop
```
Cliente feliz → pide referral → referral se cierra → 
→ incentivo activado → cliente más feliz → pide otro referral
```

### Metrics
- Referral rate: % de clientes que refieren
- Conversion rate: % de referidos que cierran
- Cost per acquisition (referral): incentivo / closed referrals

---

*Este sistema operativo es parte de la Constitución v2 (Nivel 2: Negocio).*
*Toda desviación requiere justificación documentada.*
