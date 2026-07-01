# Tasks — Mystika

| Campo | Valor |
|-------|-------|
| **Spec** | `SPEC-20260630-012` |
| **Total tareas** | 46 |
| **Fases** | 4 |
| **Duración estimada** | 30 días |

---

## Fase 1 — Fundación (Días 1-3)

### Brand + Diseño

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 1.1 | Definir identidad visual completa (logo, paleta, tipografía) | — | 4h |
| 1.2 | Crear assets gráficos: logo SVG, favicon, social cards | 1.1 | 3h |
| 1.3 | Redactar BRAND-GUIDE.md completo | 1.1 | 2h |
| 1.4 | Redactar perfil de personalidad de Lilith para AI chat | — | 2h |

### Infraestructura

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 1.5 | Configurar subdominio mystika.app en nginx | — | 1h |
| 1.6 | Obtener certificado SSL para mystika.app (certbot) | 1.5 | 0.5h |
| 1.7 | Crear DB `mystika` en PostgreSQL + ejecutar schema.sql | — | 0.5h |
| 1.8 | Configurar directorio /data/videos/mystika/ (fuera de root) | — | 0.5h |
| 1.9 | Configurar nginx X-Accel para /protected/ con validación JWT | 1.8 | 2h |
| 1.10 | Configurar Stripe webhook endpoint (preparar) | — | 1h |
| 1.11 | Configurar Mercado Pago webhook endpoint (preparar) | — | 1h |

### Código base

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 1.12 | Scaffold Next.js app (landing + layout base) | — | 1h |
| 1.13 | Scaffold Express API (server.js, rutas base, middleware JWT) | — | 2h |
| 1.14 | Scaffold React Native app (Expo, navegación base) | — | 2h |
| 1.15 | Configurar variables de entorno (.env) para todos los servicios | 1.5 | 0.5h |
| 1.16 | Escribir tests unitarios iniciales (API health, auth) | 1.13 | 2h |

---

## Fase 2 — Web MVP (Días 4-10)

### Landing + Autenticación

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 2.1 | Landing page (hero, pricing, about Lilith, newsletter) | 1.12 | 4h |
| 2.2 | Sistema de registro/login (email + password, JWT) | 1.13 | 4h |
| 2.3 | Integrar login vía Telegram (opcional) | 2.2 | 3h |
| 2.4 | Selector de idioma (ES/EN) persistente en sesión | 2.2 | 2h |

### Catálogo + Player

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 2.5 | API CRUD de lecciones (admin) | 1.13 | 3h |
| 2.6 | Página de catálogo (grid de lecciones por instrumento) | 2.5, 2.2 | 4h |
| 2.7 | Página de detalle de lección (descripción, preview) | 2.6 | 2h |
| 2.8 | Video player protegido (con token JWT) | 2.7 | 4h |
| 2.9 | API de generación de token de video | 1.13 | 2h |

### Contenido efímero

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 2.8b | Implementar lógica de max_views / view_count en access_tokens | 2.8 | 2h |
| 2.8c | Sistema de invalidación automática de token al completar vista | 2.8b | 1h |
| 2.8d | Pantalla post-consumo ("Ritual consumido" con opciones retener/descargar) | 2.8c | 3h |
| 2.8e | API de retención (comprar retención → nuevo token perpetuo) | 2.8b, 2.10 | 3h |
| 2.8f | API de descarga (pago → generar video con watermark via FFmpeg) | 2.8b, 2.10 | 4h |
| 2.8g | Sistema de watermark dinámico en descargas | 2.8f | 3h |
| 2.8h | Enlace de descarga temporario (JWT, 7 días, 1 solo uso) | 2.8f | 2h |

### Pagos

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 2.10 | Stripe checkout session para compra individual | 1.10 | 3h |
| 2.11 | Stripe subscription (Mysteria + Ritual) | 1.10 | 4h |
| 2.12 | Mercado Pago preference para compra individual | 1.11 | 3h |
| 2.13 | Mercado Pago preapproval para suscripciones | 1.11 | 4h |
| 2.14 | Webhook handler Stripe (pago exitoso → activar acceso) | 2.10 | 3h |
| 2.15 | Webhook handler Mercado Pago (pago exitoso → activar acceso) | 2.12 | 3h |
| 2.16 | Página de "mi cuenta" (lecciones compradas, suscripción activa) | 2.2, 2.10 | 4h |
| 2.16b | Sección "Mi Altar" (contenido retenido/descargado) | 2.16, 2.8d | 2h |
| 2.16c | Precios dinámicos de retención/descarga según plan del usuario | 2.16, 2.10 | 2h |

### Telegram Bot

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 2.17 | Setup Telegraf bot (comandos base: /start, /menu) | — | 2h |
| 2.18 | Handler de catálogo (/catalogo → inline keyboard) | 2.17, 2.5 | 2h |
| 2.19 | Handler de compra (/comprar N → link MP/Stripe) | 2.17, 2.10 | 3h |
| 2.20 | Handler de suscripción (/suscriptores → planes) | 2.17, 2.11 | 2h |
| 2.21 | Notificaciones post-pago (push desde webhook) | 2.14, 2.17 | 2h |

---

## Fase 3 — Contenido + E-commerce (Días 11-18)

### Contenido NSFW

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 3.1 | API de galería de fotos (CRUD, acceso por plan) | 1.13 | 3h |
| 3.2 | API de videos NSFW (CRUD, acceso por plan) | 1.13 | 3h |
| 3.3 | Galería web (grid + lightbox, condicional por plan) | 3.1, 2.2 | 4h |
| 3.4 | Control de acceso: qué ve cada plan (free/Mysteria/Ritual) | 3.3 | 2h |

### E-commerce

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 3.5 | API de productos Mystika Apparel | 1.13 | 2h |
| 3.6 | Tienda web (listado + detalle + carrito) | 3.5 | 6h |
| 3.7 | Checkout de tienda (Stripe) + confirmación | 3.6, 2.10 | 4h |
| 3.8 | Notificaciones de venta de merch (admin) | 3.7 | 1h |

### Tips / Donaciones

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 3.9 | API de tips (crear, historial) | 1.13 | 2h |
| 3.10 | UI de "Ofrendas" (monto único + mensaje a Lilith) | 3.9, 2.2 | 3h |
| 3.11 | Agradecimiento automático de Lilith (AI) tras tip | 3.10, 4.1 | 2h |

### Streaming en vivo

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 3.12 | API de eventos en vivo (crear, listar, notificar) | 1.13 | 2h |
| 3.13 | Integración con OBS o servicio de streaming | 3.12 | 3h |
| 3.14 | Reproductor de live en web + app | 3.13 | 4h |
| 3.15 | Notificaciones push de "Lilith está en vivo" | 3.13, 4.4 | 2h |

---

## Fase 4 — Mobile App + AI + Premium (Días 19-30)

### AI Chat

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 4.1 | Prompt de personalidad de Lilith para OpenRouter | — | 3h |
| 4.2 | API de chat (historial, contexto del usuario, plan) | 4.1, 1.13 | 4h |
| 4.3 | UI de chat en web y mobile | 4.2 | 4h |

### Push Notifications

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 4.4 | Configurar Firebase Cloud Messaging | — | 2h |
| 4.5 | API de suscripción a notificaciones (web + mobile) | 4.4 | 2h |
| 4.6 | Sistema de "Susurros" (notificaciones programadas y contextuales) | 4.5 | 3h |

### Mobile App (React Native)

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 4.7 | Pantalla de login/registro | 1.14 | 3h |
| 4.8 | Pantalla de catálogo + detalle de lección | 4.7, 2.5 | 4h |
| 4.9 | Video player nativo (AVPlayer / ExoPlayer) | 4.8 | 4h |
| 4.10 | Pantalla de galería NSFW | 4.7, 3.1 | 3h |
| 4.11 | Pantalla de tienda | 4.7, 3.5 | 4h |
| 4.12 | Pantalla de chat con Lilith | 4.7, 4.2 | 3h |
| 4.13 | Pantalla de "mi progreso" (lecciones completadas, tareas) | 4.7 | 3h |
| 4.14 | Pantalla de ofrendas (tips) | 4.7, 3.9 | 2h |
| 4.15 | Suscripciones a notificaciones push | 4.6 | 2h |
| 4.16 | Gestión de suscripción (cancelar, cambiar plan) | 4.7, 2.11 | 3h |
| 4.17 | Build + firma iOS (TestFlight) | todas | 4h |
| 4.18 | Build + firma Android (Play Store internal track) | todas | 3h |

### Admin Panel

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 4.19 | Admin web: subir lección con video | 2.5 | 3h |
| 4.20 | Admin web: galería de contenido (fotos/videos NSFW) | 3.1 | 3h |
| 4.21 | Admin web: dashboard de ingresos (MRR, suscriptores, tops) | 2.14 | 4h |
| 4.22 | Admin Telegram: subir video → bot pide metadata | 2.17 | 4h |

### Deploy + CI/CD

| # | Tarea | Depende | Esfuerzo |
|---|-------|---------|----------|
| 4.23 | Dockerizar API + web | 1.12, 1.13 | 3h |
| 4.24 | Systemd service para API + bot | 4.23 | 1h |
| 4.25 | GitHub Actions: test → build → rsync a OVH | 4.23 | 3h |
| 4.26 | Backup automático de DB + videos | — | 1h |
| 4.27 | Prueba de carga + optimización de streaming | 4.24 | 3h |
