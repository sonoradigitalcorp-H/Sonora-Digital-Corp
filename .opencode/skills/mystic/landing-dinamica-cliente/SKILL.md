# Skill: Plantilla Landing Dinámica + Campaña Social (cliente IA)

Reutilizable para cada cliente de Sonora Digital Corp. Captura el pipeline completo:
landing SPA multi-ruta + widget voz-first + filtro de salida + campaña social con marca.

## Cuándo usar
- Nuevo cliente con página web + bot + redes sociales
- Mejorar una página estática a dinámica premium
- Crear campaña de contenido social automatizada

## Stack (REUSAR, no duplicar)
- **Frontend**: Vue 3 + Vite + Tailwind (plantilla en `04_Deployment/orbe/vue-landing/`)
  - Rutas: `/` home, `/servicios`, `/asistente`, `/video`, `/faq`, `/contacto`
  - Vue Router con `createWebHashHistory` (funciona en nginx sin config extra)
  - Fondo aurora animado (colores cambiantes), blobs, glassmorphism
  - Flip cards 3D estilo Yu-Gi-Oh (front = servicio, back = beneficios)
  - **Widget voz-first**: micrófono grande "Toca para hablar" + botón ■ STOP al hablar
  - A/B testing: `abVariant()` en composable (localStorage + `?ab=a|b`)
- **Backend**: webhook existente (`telegram_webhook_hermosillo.py`)
  - `limpiar_salida()`: sin emojis, `*`, `!`, `?` en toda respuesta (obligatorio)
  - Voz edge-tts DaliaNeural, rate **+4%** (ágil, no lenta), pitch +2Hz
  - Endpoints: `/webhook/<token>` (Telegram), `/chat` (JSON), `/chat/audio` (MP3)
- **Imágenes**: `gen_canva_images.py` — gráficos planos estilo Canva **SIN personas**
  (el cliente pidió: sin caras, ilustraciones que den a entender el servicio)
- **Video**: `gen_reel_hermosillo.py` — reel vertical 1080x1920, ffmpeg local + Pillow
  (VPS no tiene ffmpeg; drawtext no existe en static → PNG overlay)
- **Redes**: `social_pipeline_nathaly.py` — calendario 6 pubs/día cada ~3h,
  publica vía Composio Instagram (`~/.composio/agent.json` → composio.api_key)

## Pasos de implementación
1. Copiar `04_Deployment/orbe/vue-landing/` → `orbe/vue-landing-<cliente>/`
2. Cambiar marca, servicios (SVC), FAQ, WA number, caption del reel
3. `npm install && npm run build` → `dist/` → scp a VPS `/mnt/vps-data/html/`
4. Verificar: `curl` 200 en html/js/css/canva + Playwright snapshot de cada ruta
5. Backend: copiar webhook, cambiar tenant/bot/DB, aplicar `limpiar_salida` + voz Dalia +4%
6. Campaña: ajustar DIARIO en `social_pipeline_*.py`, dry-run primero, luego --live con OK

## Patrones aprendidos (no repetir errores)
- **ffprobe rompe en esta laptop** (libva symbol error) → validar video con ffmpeg -i
- **ffmpeg static sin drawtext** → usar Pillow PNG overlay
- **VPS sin ffmpeg** → voz edge-tts MP3 nativo (no ogg), video se genera local
- **Rate -8% = lento** (cliente se quejó) → usar +4% (ágil natural)
- **Enojis/asteriscos/admiración PROHIBIDOS** en texto al cliente → `limpiar_salida`
- **Carrusel sin personas** → gráficos canva planos (contabilidad/citas/declaraciones/importaciones/dashboard)
- **npm build cambia hash de assets** → subir el archivo que el HTML nuevo referencia
- **Playwright MCP cachea HTML** → verificar con curl/grep del JS servido
- **waLink duplicaba "Hola Nathaly..."** → pasar solo el servicio, no el mensaje completo

## Verificación final
- Suite tests: `python3 -m pytest tests/ -q` (esperado: todo verde)
- E2E: curl a /health, /chat (RAG), /chat/audio, paquetes + Playwright en cada ruta
- Campaña: `python3 social_pipeline_*.py` (dry-run) muestra 6 pubs/día