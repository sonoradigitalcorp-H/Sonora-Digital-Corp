# SDD 0006 — Plataforma de Venta Guiada del Ecosistema SDC

> **Spec principal** para el sistema que convierte prospectos en clientes mostrando "cómo se vería su ecosistema" con SDC, y en ~15 min levanta su página/app/bot de prueba.
> **Estado:** PLANEADO · **Versión:** 0.1 · **Fecha:** 2026-08-13 · **Autor:** HERMES (bajo dirección de Luis Daniel)
> **Seguimiento BDD/ODD/TDD:** ver `gherkin/`, `eval/`, `tests/` en esta carpeta (a crear).

---

## 1. Goal (una frase)

Un **asistente multi-canal** (web/Telegram/WhatsApp/voz) que conduce a cada prospecto a entregar su **nombre, empresa (o nombre personal) y red social/WhatsApp**, dispara su **investigación web + registro en Sheet/CRM**, le muestra **cómo se vería su ecosistema** con los 6 productos SDC, y **levanta en ~15 min un subdominio Hostinger + web + bot de Telegram de prueba** con acceso de 1 día.

## 2. Current Context / Assumptions (lo que ya existe — NO reinventar)

Verificado hoy en monorepo `~/Documentos/Sonora Digital Corp Nuevo/` y skills `~/.hermes/skills/`:

| Componente | Ubicación | Estado |
|---|---|---|
| Onboarding engine v2 (dual CRM + scoring + feedback) | `01_Core_Platform/.../onboarding_engine.py` (spec SDD 0004) | ✅ Código + 28 tests TDD |
| Lead scoring determinista cold/warm/hot | `lead_scoring.py` | ✅ |
| Lead intelligence (resumen+objeciones+next_action) | `lead_intelligence.py` | ✅ |
| Asset generation (imagen/video/mockup/audio) | `asset_generation.py` | ✅ 13 prompts evaluados |
| Company research (web_search → perfil propuesta) | Skill `sdc-company-research` | ✅ |
| Onboarding con propuesta visual fal.ai | Skill `sdc-onboarding` | ✅ |
| Multi-tenant routing (bot→tenant→agente) | `~/.hermes/tenants/tenant_router.py` + `tenants.json` | ✅ |
| Agents factory (persona.md + reglas.md por nicho) | `hermes_agents_factory.py` + `~/.hermes/agents/` | ✅ |
| Composio (tools terceros: gmail, sheets, telegram, whatsapp, crm) | `~/.composio/agent.json` (cuenta happy-lantern-hare) | ✅ MCP remoto |
| CRM demo (leads, scoring, pipeline) | Skill `cesar-crm-demo` | ✅ |
| Paquete ventas web + API `/api/v1/` → gateway 8643 | nginx + `streamlit`/landing | ✅ |
| Web SDC + chatbot | `sonoradigitalcorp.com` → 8643 | ✅ (Aug 13) |
| Voice assistant (formal, offering options, audio) | `~/.hermes/scripts/voice_assistant.py` | ✅ (re-afinado hoy) |
| **NO existe aún:** provisionador Hostinger subdominio | — | ❌ A crear |

### Assumptions críticas
- **Todo proceso pesado corre en VPS OVH 149.56.46.173** (regla canónica PC 3.3GB RAM). El agente de producción vive en VPS; aquí se planea y se versiona el código.
- **Hermes = único orquestador** (gateway 8643). No crear procesos paralelos que compitan por tokens de bot/CRM.
- **Composio = cimiento de tools** (google_sheets para el Sheet, telegram, whatsapp, crm). Ver estado real de conexiones ANTES de codear.
- **Hostinger subdominio**: requiere credenciales de API Hostinger (hPanel/API v2 token). Bloqueante a gestionar.
- Precios/pipeline de pago ya definidos en `sdc-shop`/OKF (no se tocan aquí).

## 3. Proposed Approach

**Pipeline de 5 actos** (un acto = una etapa del flujo con su propio agente/estado):

```
PROSPECTO ──> [1 CAPTURA] ──> [2 INVESTIGA+REGISTRA] ──> [3 MUESTRA ECOSISTEMA]
   ──> [4 PROVISIÓN 15MIN] ──> [5 PRUEBA 24H] ──> (cobro/conversión)
```

- **Orquestador único**: agente SDC en gateway 8643 con router multi-tenant. No bots paralelos.
- **Cada acto es un módulo** (reutilizando onboarding_engine/lead_scoring/company_research existentes).
- **Persistencia**: Google Sheet vía Composio `google_sheets` (fuente viva del cliente) + CRM `leads.db` + Engram tenant.
- **Provisioner**: servicio web revierte DNS wildcard de Hostinger y genera subdominio `cliente.sonoradigitalcorp.com` con: (a) landing, (b) webhook del bot Telegram dedicado, (c) QR/links de acceso. Timebox 15 min.

## 4. Step-by-Step Plan (tareas bite-sized, TDD cada una)

### FASE 0 — Cimentar terreno (previo, sin código)
- [ ] 0.1 Verificar conexiones Composio reales: `composio connections list` (google_sheets, telegram, whatsapp) — registrar estado en `ESTADO.md`.
- [ ] 0.2 Verificar credenciales: `~/.composio/agent.json`, `~/.hermes/.env` keys, Hostinger API token (BLOQUEANTE — pedir a Jefe).
- [ ] 0.3 Confirmar gateway 8643 activo y webhook multi-tenant funcionando.
- [ ] 0.4 Definir wildcard DNS en Hostinger para `*.sonoradigitalcorp.com`.

### FASE 1 — Acto 1: Captura guiada (presentación + recolección de datos)
- [ ] 1.1 Escribir test BDD (Gherkin) del flujo "primer contacto" → presentación + petición de nombre/empresa/red.
- [ ] 1.2 Implementar presentación no-brusca: NUNCA "¿cuál es tu nombre?"; abre con "Soy MYSTIC de SDC, te ayudo a ver tu ecosistema." + lista los 6 productos.
- [ ] 1.3 Captura estructurada: `nombre`, `empresa|nombre_personal`, `red_social|whatsapp` (validación por tipo de canal).
- [ ] 1.4 Si no da red social, pedirla explícitamente (dato obligatorio para registrar).
- (Reusa: patrón sdc-onboarding captura inicial.)

### FASE 2 — Acto 2: Investigar + Registrar (web search → Sheet → CRM)
- [ ] 2.1 Al recibir nombre/empresa/red → disparar `web_search` (skill sdc-company-research) en background.
- [ ] 2.2 Escribir fila en Google Sheet vía Composio `google_sheets` (nombre, empresa, red, industria, score, timestamp). Test de integración con conexión real.
- [ ] 2.3 Insertar/update CRM `leads.db` + Engram tenant (aislar memoria por tenant). Test.
- [ ] 2.4 Feed back al prospecto: "Ya te registré, déjame ver cómo se vería tu ecosistema."

### FASE 3 — Acto 3: Mostrar el ecosistema (visual + 6 productos)
- [ ] 3.1 Construir mock visual del ecosistema por industria (fal.ai, patrones sdc-onboarding/asset_generation).
- [ ] 3.2 Presentar los 6 productos encajados a SU caso: páginas web IA, asistente texto, asistente voz, agente recepcionista, agente ventas, agente marketing.
- [ ] 3.3 Score del lead (cold/warm/hot) con datos reales + next_action (lead_scoring.py). Test.
- [ ] 3.4 Narrativa: "Así se vería [EMPRESA] con nosotros" + pregunta de acción.

### FASE 4 — Acto 4: Provisión 15 min (Hostinger + app + bot)
- [ ] 4.1 Módulo `provisioner.py`: llama a API Hostinger, crea subdominio `cliente.sonoradigitalcorp.com`.
- [ ] 4.2 Genera (a) landing web del ecosistema del cliente, (b) webhook de bot Telegram dedicado, (c) app simple de prueba.
- [ ] 4.3 Empaqueta: QR de acceso + link + instrucciones. Test e2e de la ruta completa (subdominio desplegado + responde 200).
- [ ] 4.4 Timebox: medir y acotar a <15 min (stopwatch en test e2e).

### FASE 5 — Acto 5: Prueba 24H + conversión
- [ ] 5.1 Otorgar acceso de 1 día (token temporal / tenant con expiración).
- [ ] 5.2 Cron de expiración a las 24h (desactivar tenant, notificar).
- [ ] 5.3 Cierre de venta: ofrecer plan Starter/Business/Enterprise (sdc-shop/OKF) + follow-up.

### FASE 6 — Calidad (transversal)
- [ ] 6.1 Suite de tests: unit (cada módulo), integration (Composio real), e2e (ruta completa), BDD (Gherkin), eval de prompts (spec-judge/spec-kit).
- [ ] 6.2 Dashboard de métricas: leads capturados, %con dato red, %provisión exitosa en <15min, conversión tras prueba 24H, tiempo medio.
- [ ] 6.3 Documentar en `ESTADO.md` + crear/actualizar skills.

## 5. Files likely to change / to create

```
00_Administration/Prompt_Registry/Specs/Ecosystem_Selling/
├── SDD-0006-ecosistema-venta-guiada.md      ← este spec
├── gherkin/                                 ← escenarios BDD por acto
│   ├── acto1-captura.feature
│   ├── acto2-registro.feature
│   ├── acto3-ecosistema.feature
│   ├── acto4-provision.feature
│   └── acto5-prueba.feature
├── eval/
│   ├── prompts/                             ← prompts por personalidad de agente
│   └── spec-judge-criteria.md               ← criterios de evaluación de respuestas
└── tests/
    ├── unit/                                ← por módulo (TDD)
    ├── integration/                         ← Composio real + CRM + Sheet
    └── e2e/provision_e2e.py                 ← ruta completa <15min

02_Client_Projects/_nuevos_clientes/<NICHO>/__tree__.md   ← árbol por nicho (plantilla)
01_Core_Platform/03_Agentic_Infrastructure/
    ├── provisioner.py          (nuevo)
    ├── ecosystem_showcase.py   (nuevo)
    └── register_lead.py        (nuevo, envuelve Sheet+CRM vía Composio)
~/.hermes/agents/<cliente_id>/ persona.md + reglas.md + skills/  (factory)
~/.hermes/skills/sdc/ sdc-ecosystem-selling/SKILL.md             (skill umbrella)
ESTADO.md                                      (actualizar)
```

## 6. Tree por nicho / cliente (plantilla)

Cada cliente nuevo genera su árbol bajo `02_Client_Projects/_nuevos_clientes/<NICHO>/`:

```
<CLIENTE>/
├── __tree__.md              ← índice, fecha, estado de convertibilidad
├── data/
│   └── lead.json            ← nombre, empresa, red, industria, score
├── research/
│   └── perfil.md            ← salida de company_research (fuente real)
├── mock/
│   └── ecosistema.png       ← visual fal.ai
├── provision/
│   ├── subdominio.txt       ← cliente.sonoradigitalcorp.com
│   ├── creds.txt            ← acceso temporal (SCRUB_personal)
│   └── expira.txt           ← 24h timestamp
└── followup/
    └── next_action.md
```

Nichos iniciales (reusar tablas de sdc-onboarding): consultorio/salud, restaurante, constructor/ingeniero, abogado, ecommerce, manufactura, marca personal/influencer, genérico.

## 7. Personalidades de agentes (eval prompts)

Un agente por rol, cada uno con persona.md + habilidades (factory) y Prompt evaluado:

| Agente | Rol en el flujo | Personalidad | Prompt clave (eval) |
|---|---|---|---|
| `mystic-orquestador` | Router/CEO | Formal, rapport, no brusco, ofrece opciones | Presentación, derivación |
| `mystic-captura` | Acto 1 | Empático, guía sin interrogar | Pedir nombre/empresa/red |
| `mystic-consultor` | Acto 3 | Consultor, propone no pregunta | Mostrar ecosistema + 6 productos |
| `mystic-concierge` | Acto 4-5 | Eficiente, generoso | Entregar acceso 24h + cierre |

Criterios de evaluación (spec-judge): (1) nunca empieza con "¿cuál es tu nombre?", (2) presentación ≤2 frases + lista de productos, (3) obtiene red social sí o sí, (4) ofrece opciones al cerrar, (5) texto 100% español voz-friendly, (6) tono formal/cálido (no brusco). Escrito en `eval/spec-judge-criteria.md`.

## 8. Métricas (todo debe poder medirse)

| Métrica | Fuente | Meta |
|---|---|---|
| Leads capturados/acto | Sheet + CRM | Rastrear funnel |
| % con dato red social | Captura | ≥90% |
| % provisión exitosa | provisioner.log | 100% |
| Tiempo provisión | e2e stopwatch | <15 min |
| Conversión tras prueba 24H | CRM | ≥25% |
| Tiempo medio respuesta | gateway | <30s |

## 9. Tests / Validation

- **TDD:** cada módulo con test que falle primero, pase después.
- **BDD:** Gherkin por acto (features + steps), runner `behave` o pytest-bdd.
- **Integration:** Composio real (Sheet fila escrita, CRM insertado) — no mocks.
- **E2E:** `provision_e2e.py` crea subdominio real y valida HTTP 200 + bot responde.
- **Eval prompts:** spec-judge sobre respuestas del agente en escenarios de prueba.

## 10. Risks / Tradeoffs / Open Questions

- **[BLOQUEANTE] Credenciales Hostinger API** — no tengo token; pedir a Jefe. Sin esto no hay provisioner.
- **[BLOQUEANTE] Conexión Composio google_sheets + telegram activa** en cuenta del agente (verificar 0.1).
- **Wildcard DNS**: requiere configurar `*.sonoradigitalcorp.com` en Hostinger.
- **RAM local**: todo provisioner/proceso pesado corre en VPS, nunca local.
- **Botias paralelas**: NO crear bots que compitan con gateway; usar router multi-tenant.
- **Coste fal.ai por mock visual** — definir presupuesto por lead.
- **Open question**: ¿el bot de prueba es Telegram (mencionado) o también WhatsApp? Confirmar alcance Acto 4.
- **Open question**: ¿cobro único por demo o sólo al convertir? Definir con sdc-shop.

## 11. Estado de adopción

Este spec es la **versión autorizada**. Progreso de tareas se refleja en `ESTADO.md`. Regla: una tarea = un commit, testeado antes de marcar ✅.