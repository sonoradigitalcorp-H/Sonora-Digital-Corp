# SDD 0008 — Hermosillo: Landing dinámica + voz natural + salida limpia

- **ID**: 0008-hermosillo-landing-vue
- **Versión**: 1.0
- **Estado**: IMPLEMENTADA (2026-08-16)
- **Cliente**: Hermosillo Contabilidad (Nathaly)
- **Fuente**: espec-judge (SDD Joaquín Ruiz) + Gentle-AI routing

## Resumen
Migrar la página estática del orbe a una **landing dinámica SPA (Vue 3 + Vite + Tailwind)** estilo Netflix/Spotify/Apple: fondo aurora animado que cambia de color, glassmorphism, flip cards Yu-Gi-Oh, video reel con marca, chat IA en vivo, FAQ, aviso de privacidad y contacto por iconos. En backend: voz más natural (edge-tts rate -8% + pitch +2Hz) y salida limpia (sin emojis, asteriscos ni signos de admiración) vía `limpiar_salida`.

## Objetivo
- Landing dinámica con efectos visuales, colores cambiantes y navegación que dirija al lead al chat/WhatsApp.
- Respuestas al cliente SIEMPRE limpias: sin emojis, sin `*`, sin `!`/`?`.
- Voz más natural para notas de voz (DaliaNeural, prosodia ajustada).
- Video reel vertical con marca listo para redes sociales (ffmpeg local + Pillow).
- Verificado con BDD (Gherkin) + tests unitarios. Todo desplegado y E2E verificado en VPS.

## Contexto
- Reusa: webhook `telegram_webhook_hermosillo.py` (RAG, paquetes, memoria nombre, notificaciones), agent `nathaly`, VPS nginx, `knowledge_store.json`.
- No duplica: usa el mismo `/chat` endpoint, mismos assets, misma marca.
- Skills usadas: `spec-judge`, `plantilla-cliente-ia`, `estilo-mystic`. Referencias: Gentle-AI (routing/review), Joaquín Ruiz (SDD/OKF).

## Especificación (contrato)

### Backend (webhook)
- `limpiar_salida(texto) -> str`: quita emojis (rangos Unicode), `*`/backtick/markdown, `!¡`/`?¿`, normaliza espacios, termina en punto. Aplicado a toda respuesta de texto antes de enviar (Telegram) y antes de devolver en `/chat`.
- `EDGE_TTS_RATE = "-8%"`, `EDGE_TTS_PITCH = "+2Hz"` — prosodia natural (DaliaNeural).
- Endpoints intactos: `/webhook/<token>`, `/chat`, `/chat/audio` (MP3).

### Frontend (landing)
- **Stack**: Vue 3 + Vite + Tailwind. Build → `dist/` → VPS `/mnt/vps-data/html/`.
- **Dinámica**: fondo aurora (`background-position` animado), blobs de color flotantes, glassmorphism, flip cards 3D (Yu-Gi-Oh) con beneficios ("nos ocupamos de tus dolores de cabeza").
- **Secciones**: nav fija glass, hero con demo chat, servicios (6 flip cards), video reel, asistente IA (chat + mic + stop), FAQ, contacto por iconos (WhatsApp con servicio prefilled, Telegram, correo icono, Instagram), aviso de privacidad.
- **WhatsApp**: link `wa.me` con mensaje prefilled por servicio (`waLink(servicio)`).
- **Sin texto de correo visible**: solo icono email → `mailto:cp.nathalyhermosillo@gmail.com`. Solo iconos WhatsApp/Telegram (sin números).
- **Voz web**: speechSynthesis es-MX rate .93 pitch 1.02 + botón STOP (■) visible al hablar.
- **Sin emojis en respuestas**: el frontend también filtra (`clean()`) por seguridad.

### Video (reel)
- `gen_reel_hermosillo.py`: ffmpeg local + Pillow (sin drawtext), 5 cortes de 5s con zoompan, texto overlay PNG, marca esquina. Salida `reel_hermosillo.mp4` (1080x1920) servido en la landing.

## Escenarios BDD (Gherkin)

```gherkin
# tests/features/landing_vue.feature
Feature: Landing dinámica Hermosillo

  Scenario: La landing carga como SPA dinámica
    Given el usuario abre https://sonoradigitalcorp.com/hermosillo.html
    Then ve el título "Nathaly · Contabilidad en Hermosillo · Asistente IA 24/7"
    And ve 6 tarjetas de servicio con botón "TOCA PARA VER"
    And ve la sección FAQ con 5 preguntas
    And ve el aviso de privacidad

  Scenario: El chat responde con texto limpio
    When el usuario escribe "qué me ofrecen de contabilidad" en el asistente
    Then la respuesta no contiene emojis, asteriscos ni signos de admiración

  Scenario: Contacto por iconos sin texto
    Given el usuario ve la sección de contacto
    Then hay iconos de WhatsApp, Telegram, correo e Instagram
    And el correo no muestra la dirección como texto (solo icono)
    And el enlace WhatsApp incluye el servicio prefilled
```

## Tests
- `tests/test_limpiar_salida.py` — 7 casos (emojis, markdown, signos, espacios, punto final, vacío, colapso doble).
- `tests/test_webhook_hermosillo.py` — actualizados al formato `{ok,res,accion,respuesta}` + `tg()`.
- `tests/test_hermosillo_cont.py` — lead persistencia vía `registrar_lead`.
- Suite completa: **27 passed**.

## Verificación
- Build Vite exitoso (80KB JS gzip 31KB). Deploy VPS: hermosillo.html 200, assets 200, reel 200.
- E2E Playwright: landing renderiza todas las secciones, chat responde en vivo con texto limpio.
- Suite 27/27 verde ANTES del commit.

## Archivos
- `04_Deployment/orbe/vue-landing/` (package.json, vite.config.js, src/)
- `04_Deployment/orbe/index_v6.html` (versión estática previa, mantenida como backup)
- `02_Source_Code/gen_reel_hermosillo.py` + `gen_reel_hermosillo.sh` (video)
- `03_Media_Assets/photos/reel_hermosillo.mp4`
- `00_Administration/MEGA_PROMPT_ULTRA_SENIOR.md`
- `00_Administration/ADRs/0004-*` (ver ADR)