# PLAN MAESTRO — Tu Bandera A.C. v2 (Agentificación total)

**ID**: PLAN-TUBANDERA-2026
**Fecha**: 2026-08-23
**Autor**: MYSTIC / SDC
**Estado**: PLANEACIÓN (no ejecutado — nada tocado)

---

## 0. Visión

Convertir Tu Bandera A.C. en una **plataforma agentificada de rehabilitación integral**:
- Un ecosistema de agentes IA especializados (recuperación, seguimiento, comunidad, educación) sobre UNA base de conocimiento de adicciones.
- Identidad y trazabilidad por usuario (tenant_id) + familiares/responsables con sus contactos.
- Canal de Telegram comunitario (grupo) + canal educativo "Aprende sobre adicciones".
- Roberto consulta TODO sobre su empresa en tiempo real (app/backoffice).
- Legal 100% donatario (archivo maestro).
- Monetización: licenciar el stack a otros centros.

---

## 1. Fundación Técnica (infra a asegurar)

| Componente | Estado | Acción |
|---|---|---|
| **wacli auth** | ❌ Not authenticated | `wacli auth` (pairing por phone-code) + `wacli-session.service` persistente (keepalive). Base para notificar familiares/responsables por WhatsApp |
| **Voz bot** | ⚠️ arreglado PATH | Verificado edge-tts en venv. Sigue |
| **Obsidian (vault)** | ❌ no existe | Crear vault `tubandera/` en el repo: conocimiento de adicciones (12 pasos, alanon, sustancias) |
| **Engram** | ✅ 524 mem | Conectar a Obsidian (RAG) |
| **Qdrant + Nomic** | ✅ corriendo | Conectar como vector store de la base de conocimiento |
| **n8n** | ✅ on-demand | Orquestador de automatizaciones (leads, seguimiento, notificaciones) |
| **Composio** | ✅ MCP config | Gmail, Calendar, WhatsApp para correos/citas/notificaciones |

---

## 2. El Agente Tu Bandera v2 — Multi-agente (UN solo bot, AGENTES diferentes)

**Arquitectura**: 1 bot de Telegram (`@TBasistente_bot`) que enruta a **agentes especializados** según la intención (routing determinista + LLM).

| Agente | Rol | Conocimiento |
|---|---|---|
| **A1. Recepción/Admisión** | Diagnóstico gratuito, captura datos, deriva | Protocolos de ingreso |
| **A2. Rehabilitación** (SOUL experto) | Tratamiento, 12 pasos NA, alanon, sustancias | TO-DO el espectro: alcohol, opioides, estimulantes, cannabis, benzos, fentanilo, conductas |
| **A3. Seguimiento** | Prevención recaídas, recordatorios, avance | Plan de vida, reinserción |
| **A4. Familia/Responsable** | Informar avance al familiar (con permiso) | Dinámica familiar |
| **A5. Comunidad/Educación** | Grupo, "Aprende sobre adicciones", ofertas laborales | Contenido educativo |
| **A6. Admin (Roberto)** | Consulta en tiempo real de la empresa | App/backoffice |
| **A7. Entrenador digital** | Enseñar web/apps/música-IA para preparar al usuario | Currículo educativo |

**Cómo se enruta**: regex determinista (precio/cita/urgencia) → agente; converse → A1/A2 según tono. Triaje de urgencia (ya existe `tubandera_scoring`).

---

## 3. SOUL Tu Bandera v2 (experto en adicciones)

El `persona: tubandera` se expande a un **knowledge base** (RAG con Qdrant):
- **Todas las sustancias**: alcohol, marihuana, cocaína/crack, opiáceos (heroína/fentanyl), metanfetaminas, benzodiacepinas, alucinógenos, inhalantes, anabólicos, juego/conductual.
- **12 pasos NA**, **Alanon** (familiar), **motivacional**, **recaídas**.
- **Enseña al hablar**: lenguaje natural, hermetismo (discreto), empoderamiento del espíritu, libertad, comunidad.
- **Siempre sin diagnosticar** ni dar consejo médico; deriva a humano/911 en crisis.

---

## 4. Identidad y trazabilidad (tenant_id)

- Cada usuario de Tu Bandera recibe un **`tenant_id`** al ingresar (chat_id + registro).
- **Usuario** y **familiares/responsables** vinculados con sus números de contacto.
- **DB**: `usuarios` (id, chat_id, nombre, tenant), `familiares` (id, usuario_id, nombre, telefono, parentesco, permiso).
- **Permisos**: el familiar SOLO ve avance del usuario al que está vinculado (privacidad).
- Roberto sube foto → notifica al **grupo** o al **familiar específico** (wacli/Composio).

---

## 5. Comunidad y educación

- **Canal de Telegram** (grupo): comunidad de recuperación. El A5 publica contenido educativo diario.
- **Aprende sobre adicciones**: canal/serie educativa (qué es cada sustancia, riesgos, mitos).
- **Ofertas laborales**: bolsa de trabajo para miembros recuperados.
- **Área educativa técnica** (roadmap): el A7 entrena al usuario en **crear páginas web, apps, e integrar IA en música** → salen con herramientas digitales. Proyecto social: egresados con competencias digitales.

---

## 6. Memoria y conocimiento (Obsidian + Engram + Qdrant)

- **Vault Obsidian** `tubandera/` = fuente de verdad del conocimiento (12 pasos, sustancias, protocolos, FAQ, legal).
- **Engram** = memoria de interacciones por usuario (memoria persistente cross-sesión).
- **Qdrant + Nomic** = embeddings del vault → **búsqueda semántica** del agente (responde del conocimiento, no alucina).
- Conectar: Obsidian (archivos md) → chunking → embeddings → Qdrant → el agente hace RAG.

---

## 7. Legal 100% donatario (archivo maestro)

Entregable a Roberto: **dossier legal** con:
- Constitución AC (acta, RFC, escrituras).
- Registro ante la ASJ (Asociaciones) / bienes inmuebles.
- **CLUNI** y alta en la **Ley Federal de Fomento a las Actividades de las OSCs**.
- Donataria autorizada (SAT): trámite SAT para ser **donataria** (constancia, requisitos, contabilidad).
- **Condonaciones/beneficios**: facturación, exenciones, transparencia.
- Leyes relevantes: Ley de Centros de Tratamiento (NOM-028), Ley General de Salud (adicciones), Ley de Asistencia, Ley de Fomento OSCs.
- Manuales operativos, reglamento interior, consentimientos informados, protección de datos.

---

## 8. Producto: App/backoffice "Roberto consulta en tiempo real"

- **Un solo bot** (el de Roberto, que ya existe como `sonora_digital_bot` / o el mismo gateway Hermes) — **NO hace falta otro bot**. El gateway Hermes ya enruta por tenant.
- Roberto pregunta en lenguaje natural: "¿cuántos usuarios activos?", "dame el avance de Juan", "¿quién debe pagar este mes?" → Hermes consulta la DB (SQLite/vector) → responde.
- **No otro bot**: se usa el mismo Hermes con rutas por tenant (Roberto = tenant admin).

---

## 9. Monetización (licenciar a otros centros)

- El stack Tu Bandera (agentes + RAG + bot) es **replicable** → ofrecer "Tu Bandera OS" a otros centros de rehabilitación (white-label) vía n8n/composio.
- Modelo: licencia mensual por centro (setup + mensualidad) + soporte.
- El A7 (educación digital) se ofrece como servicio premium.

---

## 10. Roadmap Anual (fases + inversión tech)

### Fase 1 — Fundación y delimitación (Mes 1-2)
- [ ] wacli auth + persistente
- [ ] SOUL v2 + knowledge base adicciones (vault Obsidian)
- [ ] Qdrant + Nomic como vector store (RAG)
- [ ] tenant_id + usuarios/familiares DB
- [ ] Bot Tu Bandera multi-agente (A1/A2/A4)

### Fase 2 — Comunidad y seguimiento (Mes 3-5)
- [ ] Canal Telegram grupo + "Aprende sobre adicciones" (A5)
- [ ] Seguimiento/recaídas (A3), notificación a familiares
- [ ] Roberto sube fotos → grupo/familiar
- [ ] Backoffice consulta en tiempo real (A6)

### Fase 3 — Educación y expansión (Mes 6-9)
- [ ] A7 entrenador digital (web/apps/música-IA)
- [ ] Bolsa laboral
- [ ] Legal: dossier 100% donataria
- [ ] Proyectos sociales con IA

### Fase 4 — Monetización (Mes 10-12)
- [ ] "Tu Bandera OS" white-label a otros centros
- [ ] Campamentos + servicios adicionales
- [ ] Roadmap de expansión

### Inversión tech estimada (recursos ya en VPS, mínima):
- RAG + vectores: **$0** (Qdrant/Nomic/Ollama ya corren).
- Voz clonada (opcional): ElevenLabs **~$22/mes** (voz real de marca).
- Automatización (n8n/composio): **$0** (ya configurado).
- Lo esencial es **tiempo de construcción** + QA, no infra.

---

## Resumen ejecutivo

**UN mismo bot** (gateway Hermes) enruta a **agentes distintos** por función. **Identidad por tenant_id** con familiares vinculados y permisos. **Conocimiento de adicciones** (12 pasos, sustancias, alanon) en **Obsidian+Qdrant (RAG)**. **Roberto consulta Todo en tiempo real** (sin otro bot — el mismo Hermes por tenant). **Legal 100% donataria** como dossier. **Monetización** licenciando "Tu Bandera OS". **Educación técnica** como proyecto social de alto impacto.

**No toqué nada** — es plan. Cuando apruebes, arranco por Fase 1 (wacli auth + SOUL v2 + RAG).
