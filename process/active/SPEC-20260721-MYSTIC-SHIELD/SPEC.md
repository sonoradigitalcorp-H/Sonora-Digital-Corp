# SPEC-20260721-MYSTIC-SHIELD — Mystic Shield

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260721-MYSTIC-SHIELD` |
| **Fecha** | 2026-07-21 |
| **Autor** | Mystic (Sonora Digital Corp) |
| **Tier** | 3 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Crear un servicio SaaS de diagnóstico y monitoreo de ciberseguridad para PyMEs mexicanas. Un agente IA (Mystic) escanea la red del cliente, analiza los resultados con un LLM, genera PDF profesional + audio resumen, y envía todo al CEO por WhatsApp y Email. El CEO puede interactuar con el agente en lenguaje natural.

---

## 2. Value Driver

- **Revenue**: $6k-20k/mes por cliente recurrente
- **Automation**: diagnóstico 100% automático, sin intervención humana
- **Founder-independence**: el agente opera solo, el fundador solo cierra ventas
- **Scalability**: same infra atiende N clientes (multi-tenant)
- **Customer Value**: el CEO recibe inteligencia accionable sin ser técnico

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Escanear red del cliente (ping sweep + puertos comunes) |
| FR2 | Analizar resultados con LLM (deepseek-v4-flash via OpenRouter) |
| FR3 | Generar PDF profesional con hallazgos, riesgos, recomendaciones |
| FR4 | Generar audio resumen (edge-tts es-MX-DaliaNeural) |
| FR5 | Enviar WhatsApp al CEO con PDF + audio + texto |
| FR6 | Enviar Email con PDF adjunto |
| FR7 | Landing pública con formulario de solicitud de diagnóstico |
| FR8 | Capturar leads y notificar al admin por WhatsApp + Email |
| FR9 | Almacenar reportes en state/reports/ con metadatos |
| FR10 | Re-enviar reporte existente por WhatsApp o Email |

---

## 4. Success Criteria

- [ ] Escaneo de /24 completo en <5 min
- [ ] PDF generado en <30s
- [ ] Audio generado en <15s
- [ ] WhatsApp enviado con PDF + audio + texto
- [ ] Email enviado con PDF adjunto
- [ ] Landing carga en <3s
- [ ] Formulario de lead guarda en state/mystic-shield/requests/
- [ ] Admin notificado en <1min del lead

---

## 5. Gherkin Scenarios

Ver `gherkin/diagnose.feature`, `gherkin/report.feature`, `gherkin/billing.feature`

---

## 6. Edge Cases

- [EC1] Red sin hosts activos → reporta "no se detectaron dispositivos"
- [EC2] OpenRouter sin API key → fallback a análisis template
- [EC3] edge-tts no instalado → skip audio, reporta sin audio
- [EC4] wacli no disponible → skip WhatsApp, solo Email
- [EC5] SMTP no configurado → skip Email, solo WhatsApp
- [EC6] Puerto 8931 ocupado → fallback automático al siguiente disponible
- [EC7] Escaneo de 127.0.0.1 → detectar y preguntar IP real

---

## 7. Technical Approach

```
Landing (Next.js/static) → FastAPI → MCP Shield Server → wacli + SMTP
                            │
                            └── state/reports/ + state/mystic-shield/requests/
```

**Componentes:**
- `mcp/servers/shield_mcp.py`: Core. Escanea con ping+socket, analiza con LLM via httpx, genera PDF con fpdf2, audio con edge-tts, envía WhatsApp con wacli subprocess, envía Email con smtplib
- `apps/mystic-shield/api/main.py`: FastAPI. Sirve landing estática, expone 6 endpoints REST
- `apps/mystic-shield/api/request_handler.py`: Guarda leads en JSON, notifica admin
- `frontends/mystic-shield/index.html`: Landing estática dark-mode con planes

**Pipeline sync** (por ahora): scan → analyze → PDF → audio → WhatsApp → Email → response
**Escalable a async** (futuro): n8n + Redis queue para diagnostico sin bloqueo

---

## 8. Dependencies

- Python: fpdf2, edge-tts, httpx, fastapi, uvicorn
- Sistema: wacli (WhatsApp CLI), ffmpeg (audio conversion), ping
- API: OpenRouter (deepseek-v4-flash), SMTP server
- Opcional: fpdf2 DejaVu Sans font

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `shield:diagnosis:started` | Al iniciar diagnóstico |
| `shield:scan:completed` | Escaneo de red terminado |
| `shield:analysis:completed` | LLM analysis terminado |
| `shield:pdf:generated` | PDF generado |
| `shield:audio:generated` | Audio generado |
| `shield:whatsapp:sent` | WhatsApp enviado |
| `shield:email:sent` | Email enviado |
| `shield:lead:captured` | Nuevo lead del formulario |
| `shield:diagnosis:completed` | Pipeline completo |

---

## 10. Kill Criteria

- No hay clientes interesados después de 5 diagnósticos gratuitos
- Costo de API OpenRouter supera $200/mes sin ingresos
- El pipeline sync no escala más allá de 10 clientes

---

## 11. Scale Criteria

- 3+ clientes pagando → migrar a async con n8n
- 10+ clientes → separar MCP server en proceso dedicado
- 20+ clientes → Wazuh server por cliente
