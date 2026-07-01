# SPEC — Mystika: Plataforma Premium de Educación Musical + Contenido NSFW

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260630-012` |
| **Fecha** | 2026-06-30 |
| **Autor** | Mystic / Sonora Digital Corp |
| **Tier** | 3 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Lanzar **Mystika**, una plataforma independiente de Sonora Digital Corp, donde una creadora de contenido NSFW con imagen de sacerdotiza wiccan (Lilith Mystika) ofrece educación musical (instrumentos + producción), contenido exclusivo, e-commerce, y suscripciones a eventos. La plataforma es amorosa, misteriosa, y construye una comunidad alrededor de la música como ritual.

---

## 2. Value Driver

**Revenue.** Nuevo producto directo al consumidor con monetización multicapa:
- Suscripciones mensuales (Mysteria $14.99/mes, Ritual $49.99/mes)
- Compras individuales de lecciones
- Tips / donaciones ("Ofrendas")
- E-commerce (Mystika Apparel)
- Suscripciones a eventos en vivo

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Usuario puede registrarse con email + contraseña o Telegram |
| FR2 | Usuario puede navegar catálogo de lecciones por instrumento |
| FR3 | Usuario puede comprar lección individual (Stripe / MP / Crypto) |
| FR4 | Usuario puede suscribirse a plan "Mysteria" ($14.99/mes) |
| FR5 | Usuario puede suscribirse a plan "Ritual" ($49.99/mes) |
| FR6 | Usuario puede ver video de lección si tiene acceso (individual o subscripción activa) |
| FR7 | Usuario puede acceder a galería de fotos/videos NSFW según su plan |
| FR8 | Usuario puede enviar tips/donaciones a Lilith |
| FR9 | Usuario puede comprar productos en Mystika Apparel |
| FR10 | Usuario recibe notificaciones push (nuevas lecciones, lives, promos) |
| FR11 | Usuario puede chatear con Lilith (AI chatbot con su personalidad) |
| FR12 | Admin (Lilith) puede subir videos/lecciones desde Telegram o web |
| FR13 | Los videos se streamean protegidos con token JWT temporal |
| FR13b | Por defecto, el acceso al video se consume al verlo (1 vista = se acaba el acceso) |
| FR13c | Usuario puede pagar extra para "retener" el video en su biblioteca (vistas ilimitadas) |
| FR13d | Usuario puede pagar extra para descargar el video (watermark con su user ID) |
| FR14 | Sistema bilingüe (ES/EN) — el usuario escoge idioma |
| FR15 | App mobile disponible (iOS + Android) |

---

## 4. Success Criteria

- [ ] Usuario completa registro y ve catálogo en < 60s
- [ ] Usuario compra lección y ve video en < 3 pasos
- [ ] Usuario se suscribe y recibe acceso inmediato a contenido premium
- [ ] Admin sube lección + video en 3 interacciones desde Telegram
- [ ] Usuario envía donación y Lilith lo agradece en tiempo real
- [ ] Usuario compra producto en tienda y recibe confirmación
- [ ] Video no puede ser descargado ni compartido fuera de la plataforma
- [ ] App mobile lanza en iOS y Android simultáneamente

---

## 5. Gherkin Scenarios

Ver `gherkin/features.feature`

---

## 6. Edge Cases

- [EC1] Pago aprobado en MP pero webhook no llegó → polling + fallback manual
- [EC2] Usuario compra lección mientras está en período de prueba gratis → prioriza compra
- [EC3] Video subido con formato no soportado → conversión automática a HLS
- [EC4] Suscripción falla al renovar → degradación automática a free + notificación
- [EC5] Token de video expira mientras ve → renovación silenciosa si aún tiene acceso
- [EC6] Usuario paga "memoria" después de haber consumido el video → reactivar acceso con nuevo token
- [EC7] Usuario descarga video y luego pide reembolso → revocar license de descarga
- [EC8] Usuario compra retención de video que ya fue removido por la creadora → reembolso automático

---

## 7. Technical Approach

**Arquitectura general:**
- **Web:** Next.js (landing, player, shop, portal de usuario)
- **Mobile:** React Native + Expo (iOS + Android)
- **API:** Node.js + Express (mismo patrón que bots SDC existentes)
- **DB:** PostgreSQL en servidor OVH
- **Pagos:** Stripe (global) + Mercado Pago (LATAM) + Crypto (USDT)
- **Streaming:** nginx X-Accel-Redirect con tokens JWT temporales
- **Push:** Firebase Cloud Messaging
- **AI Chat:** OpenRouter (Llama 3.3 70B) con prompt de personalidad de Lilith
- **Bot Telegram:** Telegraf (ventas + subida admin + notificaciones)
- **Automatización:** n8n (emails, recordatorios, seguimiento)
- **Host:** Servidor OVH 149.56.46.173

**Patrones:**
- Mismo patrón de skill-loading y multi-tenancy que `platforms/telegram/`
- Express API con middleware JWT para autenticación
- Video siempre servido con token, nunca accesible directamente
- El frontend web y mobile consumen la misma API REST

---

## 8. Dependencies

| Dependencia | Propósito |
|---|---|
| Stripe SDK | Pagos globales |
| Mercado Pago SDK | Pagos LATAM |
| Telegraf | Telegram bot |
| Express | API backend |
| Next.js | Web frontend |
| React Native + Expo | App mobile |
| Firebase Admin | Push notifications |
| nginx | Streaming + reverse proxy |
| PostgreSQL | Base de datos |
| OpenRouter | AI chat (Llama 3.3 70B) |

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `mystika.user.registered` | Nuevo usuario registrado |
| `mystika.lesson.purchased` | Compra individual completada |
| `mystika.subscription.started` | Nueva suscripción activa |
| `mystika.subscription.cancelled` | Suscripción cancelada |
| `mystika.subscription.expired` | Suscripción expiró |
| `mystika.tip.received` | Donación recibida |
| `mystika.lesson.uploaded` | Nueva lección subida por admin |
| `mystika.stream.started` | Live stream iniciado |

---

## 10. Kill Criteria

- Costo de infraestructura supera $200/mes antes de alcanzar 100 suscriptores de pago
- Tasa de conversión de visita a pago < 0.5% después de 30 días
- Problemas legales con plataformas de pago por contenido NSFW
- Violación de términos de servicio de Stripe/MP por contenido adulto

---

## 11. Scale Criteria

- 500+ suscriptores de pago → migrar contenido a CDN (Cloudflare Stream o Bunny)
- 2000+ usuarios activos → separar API en microservicios
- $10k+ MRR → contratar moderación y soporte dedicados
- Demanda internacional → traducción a más idiomas + métodos de pago regionales
