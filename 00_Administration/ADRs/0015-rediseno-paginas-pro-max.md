# SPEC-0015: Descontaminación + Rediseño páginas Pro Max

**Fecha**: 2026-08-26
**Estado**: IMPLEMENTADO ✅ (verificado con tests TDD 5/5 PASS + evidencia real VPS)
**Metodología**: SDD (Joaquín Ruiz / SpecJudge + Gentleman) — SPEC → Gherkin → TDD → eval → SPEC JUDGE

## Contexto

Auditoría de las 3 páginas de producción reveló errores reales:

1. **nathaly.html** (contabilidad): CONTAMINADA con 12 fragmentos de Tu Bandera A.C.
   (adicciones, 12 Pasos, Modelo de Tratamiento, Instalaciones Dignas, "Bandera").
2. **index.html** (agencia IA): bug JS `c.n.lowerCase()` (debe ser `toLowerCase()`),
   orbe 3D + glassmorphism 24px + gradientes + emojis = "slop" visual.
3. **tubandera.html** (adicciones/donataria): fotos IA vendidas como "reales".

## Criterios de aceptación

### nathaly.html
- [ ] 0 ocurrencias de palabras de Tu Bandera en el HTML (adicciones, 12 Pasos, tratamiento, bandera, fentanilo, narcóticos)
- [ ] HTML válido (sin tags rotos ni contenido mal anidado)
- [ ] Diseño coherente contabilidad (verde/esmeralda, NO navy/rojo)
- [ ] Nav, hero, servicios, CTA conservan funcionalidad original (chatbot IA, mic, TTS)
- [ ] Chatbot embebido con `person:nathaly` responde correctamente

### index.html
- [ ] `c.n.lowerCase()` → `c.n.toLowerCase()` (bug JS corregido)
- [ ] Diseño sistema `linear.app` (minimalista, profesional, no "slop" AI)
- [ ] Conserva funcionalidad: chatbot IA, catálogo nichos, agenda, mic, TTS
- [ ] 0 emojis en copy de venta

### tubandera.html
- [ ] Fotos IA no se presentan como "reales" (cambiar copy: "fotos" → "imágenes representativas")
- [ ] Diseño sistema `notion` (blanco limpio, tipografía serif para texto, sans-serif para UI)
- [ ] Conserva funcionalidad: chatbot IA con `person:tubandera`, mic, TTS, CTAs a Roberto
- [ ] `id="servicios"` no duplicado (solo 1)

## Reglas duras (Spec Judge)
- 0 exclamaciones en copy de venta
- 0 tecnicismos (IA/bot/modelo/LLM/RAG/embedding/chatbot)
- Stack audio/voz IDÉNTICO en las 3 páginas (mic getUserMedia + MediaRecorder + auto-stop por silencio + POST /api/stt + TTS speechSynthesis)
- Chatbot IA común: botón flotante → panel chat + mic auto-stop silencio + TTS + POST /api/v1/chat/completions con `person`
- Modelo: deepseek/deepseek-v4-flash-0731 PRIMARY, max_tokens>=800