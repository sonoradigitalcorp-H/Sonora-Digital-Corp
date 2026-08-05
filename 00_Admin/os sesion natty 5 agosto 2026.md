# Sesión — Estudio cirugía plástica Nathaly (SOP + prolactina)

**Session:** natty-surgery-study
**Fecha:** 5 agosto 2026
**Número objetivo WhatsApp:** 6622681111 (JID 5216622681111@s.whatsapp.net)
**Solicitud original:** Investigar cirugía estética actual (lipo HD, lipofilling/BBL, implantes), estudio profundo implantes vs grasa para Nathaly (SOP/ovario poliquístico + prolactina elevada). Plan del Dr.: $170,000 por lipo panza/brazos/cadera/nalgas. Entregar: presentación canvas con antes/después, 3 audios de WhatsApp (explicación, nuevo estilo de vida/roadmap, estrategia de contenido y monetización), analizando la foto de Naty.

**Instrucción clave del usuario:** "No batalles no inventes rutas ya hay como hacerlo ya lo hemos hecho toma el camino más corto" → reutilizar pipelines existentes.

---

## Estado de infraestructura (verificado)

### Funciona
- **TTS local:** servidor en `localhost:8765` (POST /tts `{"text","voice","output"}`), voz `es-MX-DaliaNeural`. Probado OK → `/tmp/prueba_voz.wav` (141,774 bytes), `/tmp/prueba2.wav` (174,030 bytes). Archivo: `sonora-digital-corp/tenants/Aztrotech/tts-server.py`.
- **edge_tts 7.2.8** instalado y OK en Python.
- **wacli:** `/home/mystic/.local/bin/wacli` autenticado — `auth status` OK, phone `5216623538272` (Sonora Digital Corp).
  - Store: `~/.wacli/accounts/personal`.
  - Patrón de envío (de `scripts/send_alex_ai_deck.py`):
    `wacli send file --file PATH --caption CAP --to <num>@s.whatsapp.net --post-send-wait 3s --store ~/.wacli/accounts/personal --json`
- **Playwright + chromium:** OK, render 1280x720 → PNG/PDF (probado `/tmp/pw_test.png`).
- **PIL 12.1.1**, ffmpeg disponibles. Sin GPU (torch CUDA=False).
- **websearch:** funcional (se usó para investigación médica).

### Bloqueado
- **OpenRouter 403** "Key limit exceeded": key `[REDACTED: clave OpenRouter revocada]` (única en `~/.config/sonora/env.local`). Backup `[REDACTED: clave OpenRouter backup]...` → 401 User not found. Afecta chat + visión (gemini-3.6-flash etc.).
- **FAL 401** invalid key credentials: `FAL_KEY=[REDACTED]` contra `fal.run` y `queue.fal.run` (flux/schnell). Sin Stable Diffusion/ComfyUI local (puerto 8188 sin respuesta).
- **Modelo actual no soporta input de imagen** → no puedo ver la foto de Naty directamente.
- Ollama solo tiene `all-minilm` y `nomic-embed-text` (sin modelo de visión).
- **`filesystem_read_media_file` está roto** (error de schema JSON Schema dialect en el MCP).

### Pipelines de referencia
- `sonora-digital-corp/scripts/send_alex_ai_deck.py` — patrón completo: render HTML deck (`.slide` N slides) → PNGs + PDF con playwright → wacli send file.
- `sonora-digital-corp/apps/voice/whatsapp_agent.py` — `send_audio()`, `send_image()`, `send_doc()`, `generate_secure_audio()` (edge-tts → OGG Opus 16kHz via ffmpeg para PTT). JID Nathaly/Noel = 5216622681111.
- `Clientes/Aztrotech/whatsapp/wacli_stdio.py` — MCP wacli con `whatsapp_send_voice` (convierte a OGG Opus, `--ptt`).
- `sonora-digital-corp/scripts/audio-thumbnail.md` — MCP `whatsapp_send_audio_thumbnail`, ejemplo ya usa 5216622681111.

---

## Fotografía de Naty
- `Audiovisuales/Sonora Digital Corp/FUNDILLUDA.jpeg` — JPEG 1177x1600.
- `Audiovisuales/Sonora Digital Corp/FUNDILLUDA2.png` — PNG 1120x1536 RGB (usada como base; convertida a `/tmp/naty_antes.jpg`).

---

## Investigación médica completada (websearch)
- **Lipo HD / lipo 4D:** contorneado de zonas (abdomen, brazos, caderas, nalgas) con definición muscular; fuentes: phoenixliposuction, medicinpro, ciaobellacosmeticsurgery, infiniskin.
- **Lipofilling / BBL (grasa propia):** transferencia de grasa para aumentar volumen en glúteos/caderas usando grasa donante de la lipo; fuente: clinicalondres.
- **SOP (ovario poliquístico):** anovulación, hiperandrogenismo, resistencia a insulina en 50-70% de los casos (MSD Manuals, natalben). Implicación: grasa donante disponible y menor riesgo de pérdida de grasa inyectada; también mayor tendencia a acumular grasa abdominal.
- **Hiperprolactinemia:** puede deberse a prolactinoma benigno (MSD/mutuaterrassa) o a medicamentos → **chequeo endocrino previo a cirugía** por seguridad anestésica y para descartar causa subyacente.

---

## TODO pendiente (en orden)
1. ✅ Redactar investigación médica (hecho).
2. ⏳ Redactar estudio implantes vs grasa propia para caso Nathaly (SOP + prolactina).
3. ⏳ Construir canvas (HTML deck) con antes/después y render PNG/PDF.
4. ⏳ Crear imagen antes/después de Naty (foto original + simulación) — **PENDIENTE DE DECISIÓN**: no puedo ver la foto ni generar imagen IA. Opciones: (a) simulación con PIL etiquetada "referencia", (b) solo foto real + diagrama de zonas, (c) esperar a que vuelva FAL/OpenRouter. Se preguntó al usuario y se descartó el diálogo.
5. ⏳ Audio 1: explicación del estudio (TTS :8765 → OGG → wacli).
6. ⏳ Audio 2: nuevo estilo de vida / roadmap post-cirugía.
7. ⏳ Audio 3: estrategia de contenido en redes + monetización (comunidad → vender productos).
8. ⏳ Enviar todo por WhatsApp a 5216622681111@s.whatsapp.net.

---

## Reanudar desde aquí
1. **Decidir el antes/después** (preguntar al usuario o usar opción "solo canvas con foto real + diagrama de zonas").
2. Redactar el estudio (yo, sin LLM API).
3. Construir HTML deck → render PNG/PDF con playwright (patrón send_alex_ai_deck.py).
4. Generar 3 audios con TTS local :8765 → convertir a OGG Opus 16kHz → enviar como PTT con wacli.
5. Enviar deck (PNG/PDF) + audios por WhatsApp.
