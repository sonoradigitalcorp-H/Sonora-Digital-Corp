# ADR 0004 — Landing SPA dinámica (Vue+Vite+Tailwind) y voz/salida limpia para clientes

- **Fecha**: 2026-08-16
- **Estado**: ACEPTADA
- **Decisión**: Migrar las páginas estáticas de clientes a SPAs dinámicas (Vue 3 + Vite + Tailwind) con efectos visuales premium; backend con salida limpia y voz natural.

## Contexto
Los clientes piden "no página estática": colores cambiantes, efectos visuales, glassmorphism, estilo Netflix/Spotify/Apple, y que la página sea una landing que dirija al lead (chat, WhatsApp, redes). Además exigen respuestas sin emojis/asteriscos/admiración y voz más natural. El stack previo era un HTML estático con Three.js (`index_v6.html`).

## Decisión
1. **Frontend**: SPA Vue 3 + Vite + Tailwind por cliente. Build estático → nginx VPS (sin runtime JS pesado en el servidor). Fondo aurora animado (CSS), blobs, flip cards 3D Yu-Gi-Oh, glassmorphism, micrófono Web Speech + botón STOP, video reel integrado.
2. **Backend**: `limpiar_salida()` en el webhook (quita emojis, markdown, `!`/`?`) aplicada a toda respuesta. Voz edge-tts DaliaNeural con rate -8% + pitch +2Hz.
3. **Video**: ffmpeg LOCAL + Pillow (el VPS no tiene ffmpeg; los MP3 de voz ya son nativos edge-tts). Reels verticales 1080x1920 con marca.
4. **Contacto**: solo iconos (WhatsApp/Telegram/correo/Instagram), sin texto de número ni dirección visible. WhatsApp con servicio prefilled.

## Consecuencias
- **Positivas**: UX premium, respuestas consistentes y profesionales, lead dirigido a conversión, video listo para redes, todo testeable (27 tests) y E2E verificado.
- **Negativas**: build frontend requiere node/vite local (compila una vez, no proceso residente). VPS sin ffmpeg → video se genera local.
- **Riesgo mitigado**: nginx sirve estáticos (rápido, sin carga); SPA ligera (80KB gzip 31KB).

## Alternativas consideradas
- HTML estático + Three.js (previo): no cumple "dinámica premium".
- Nuxt/SSR: sobrecarga innecesaria para landing de cliente.
- drawtext ffmpeg: no disponible en static build → Pillow PNG overlay (más portable).

## Referencias
- SDD 0008-hermosillo-landing-vue · MEGA_PROMPT_ULTRA_SENIOR.md · Gentle-AI routing/review · espec-judge (Joaquín Ruiz)