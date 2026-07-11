# ADR-20260630-002 — Arquitectura Técnica de Mystika

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260630-002` |
| **Fecha** | 2026-06-30 |
| **Spec** | `SPEC-20260630-012` |
| **Estado** | aceptado |

---

## Context

Mystika requiere una plataforma multicanal (web, mobile, Telegram) con contenido protegido, pagos, suscripciones, e-commerce, streaming, y AI chat. El stack debe ser mantenible, económico para empezar, y escalable. Se reutilizan patrones existentes de Sonora Digital Corp donde tenga sentido, pero Mystika es independiente.

---

## Decision

### Stack tecnológico

| Capa | Tecnología | Justificación |
|------|-----------|---------------|
| Web frontend | Next.js 14 | SSR, SEO, App Router, fácil deploy |
| Mobile | React Native + Expo | Código único iOS + Android, hot reload |
| Backend API | Node.js + Express | Mismo patrón que bots existentes en SDC |
| Base de datos | PostgreSQL | Misma instancia OVH que SDC, DB separada `mystika` |
| Pagos globales | Stripe | Checkout Sessions + Subscriptions |
| Pagos LATAM | Mercado Pago | Preference + Preapproval |
| Crypto | Web3 + wallet addresses | USDT/BTC manual verification inicial |
| Streaming | nginx X-Accel-Redirect | Archivos fuera de root, tokens JWT |
| Push notifications | Firebase Cloud Messaging | Gratuito, soporta iOS y Android |
| AI Chat | OpenRouter (Llama 3.3 70B) | API key existente, prompt personalizado |
| Bot Telegram | Telegraf | Mismo patrón que `platforms/telegram/` |
| Automatización | n8n | Workflows existentes, Docker |
| Host | OVH VPS (149.56.46.173) | Mismo servidor, nuevo subdominio |
| CDN (futuro) | Cloudflare Stream | Cuando escale |

### Arquitectura de red

```
                         ┌──────────────┐
                         │   nginx :443  │
                         │  mystika.app  │
                         └──────┬───────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                   │
        ┌─────▼─────┐   ┌──────▼──────┐   ┌───────▼──────┐
        │ Next.js    │   │ Express API │   │  nginx media │
        │ :3000      │   │ :4000       │   │  /protected  │
        │ Web App    │   │ REST API    │   │ X-Accel      │
        └────────────┘   └──────┬──────┘   └──────────────┘
                                │                    │
                                │            ┌───────▼──────┐
                                │            │  /data/videos │
                                │            │  (fuera root) │
                                │            └──────────────┘
                          ┌─────┴─────┐
                          │ PostgreSQL │
                          │  mystika   │
                          └───────────┘
```

### Base de datos

Ver `db/schema.sql` para el schema completo.

Estrategia:
- Misma instancia PostgreSQL que SDC, DB separada `mystika`
- Migraciones con archivos SQL versionados
- Backups diarios incluidos en el backup general de SDC

### Flujo de streaming protegido

```
1. Usuario solicita /api/video/123
2. Express verifica en DB: ¿tiene acceso? (suscripción activa OR compra individual)
3. Si tiene acceso → genera JWT con:
   - sub: telegram_id
   - video: 123
   - exp: now + 1 hour
4. Express responde con redirect a:
   /protected/videos/lesson-123.mp4?token=JWT
5. nginx valida JWT (lua o auth_request)
   - Válido → sirve archivo con X-Accel-Redirect
   - Inválido → 403 Forbidden
6. El archivo físico está en /data/videos/mystika/
   ¡NUNCA accesible directamente desde la web!
```

### Flujo de pagos (Stripe + MP)

```
USUARIO                    BOT/API              PAYMENT GATEWAY         DB
   │                         │                       │                  │
   ├─ "Comprar lección 3" ──►│                       │                  │
   │                         ├── createCheckout() ──►│                  │
   │                         │◄── checkout_url ──────┤                  │
   │◄── "Link de pago" ─────┤                       │                  │
   ├─ Abre link ────────────────────────────────────►│                  │
   ├─ Paga ─────────────────────────────────────────►│                  │
   │                         │                       │                  │
   │                         │◄── webhook ───────────┤                  │
   │                         ├── verifyPayment() ───►│                  │
   │                         ├── INSERT purchase ─────────────────────►│
   │                         ├── generateToken() ────┤                  │
   │◄── "✅ Acceso activado" ─┤                       │                  │
   │                         │                       │                  │
```

### Planes y precios

| Plan | Precio | Stripe Product ID | MP Preapproval |
|------|--------|-------------------|----------------|
| Mysteria | $14.99/mes | `prod_mysteria` | Crear al setup |
| Ritual | $49.99/mes | `prod_ritual` | Crear al setup |

### Modelo de contenido efímero (Ephemeral Access)

Por defecto, todo contenido visual en Mystika sigue el modelo **"watch once, then it's gone"**:

| Nivel | Acceso por defecto | Retener (pago extra) | Descargar (pago extra) |
|-------|-------------------|---------------------|----------------------|
| Lección comprada individual | 1 vista completa + preview perpetuo | +50% del precio | +100% del precio |
| Suscriptor Mysteria | 1 vista por lección nueva | +$4.99/lección | +$9.99/lección |
| Suscriptor Ritual | **Retención incluida** (rewatch ilimitado) | Incluido | +$4.99/lección |
| Contenido NSFW (foto/video) | 1 vista (24h para rewatch) | +$2.99/item | +$5.99/item |

**Cómo funciona técnicamente:**

1. Cuando el usuario ve un video, el frontend reporta `video_completed` a la API
2. La API marca la lección como "consumida" para ese usuario
3. El token de acceso se invalida permanentemente
4. En la UI, la lección aparece como "Consumida — ¿Quieres retenerla?"
5. Si paga retención → nuevo token perpetuo para rewatch
6. Si paga descarga → archivo con watermark visible (user_id + email) + enlace de descarga con expiry de 7 días

**Precios de retención/descarga (configurables por Lilith desde admin):**

| Acción | Precio sugerido |
|--------|----------------|
| Retener lección individual | +$7.49 (50% de $14.99) |
| Descargar lección individual | +$14.99 (100%) |
| Retener foto NSFW | +$2.99 |
| Descargar foto NSFW | +$5.99 |
| Retener video NSFW | +$4.99 |
| Descargar video NSFW | +$9.99 |
| Retener lección completa (suscriptor Mysteria) | +$4.99 |
| Descargar lección completa (suscriptor Mysteria) | +$9.99 |

**Watermark en descargas:**
- Texto superpuesto: `@usuario · Mystika · user@email.com`
- Posición: rotando entre 3 posiciones aleatorias cada 30s
- Opacidad: 15% (visible pero no arruina la experiencia)

### Contenido NSFW — Política técnica

- Todo el contenido adulto está detrás de autenticación
- Stripe permite contenido adulto CONSENSUADO (ver ToS Section 5 Prohibited Businesses — contenido sexualmente sugestivo está permitido, prostitución/escorts no)
- Mercado Pago permite contenido adulto si no viola leyes locales
- Crypto (USDT/BTC) para usuarios que prefieren anonimato total
- Implementar verificación de edad (18+) al registro

### AI Chat — Personalidad de Lilith

El chat con Lilith usa OpenRouter con prompt de sistema que define:
- Personalidad: cálida, misteriosa, juguetona, sabia
- Conocimiento: teoría musical, técnica instrumental (guitarra, batería, piano, bajo, canto, producción)
- Límites: nunca sexualmente explícita en texto, sugestiva pero elegante
- Contexto: recuerda el progreso del alumno, sus lecciones compradas, su plan

---

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| **A: Node.js + Express + Next.js (ELEGIDA)** | Consistente con SDC, mismo host, mínimo costo nuevo | JS overhead a escala |
| B: Python + FastAPI + React | Mejor para ML/IA futura | Rompe consistencia con stack existente |
| C: Firebase + Flutter | Zero infra, rápido prototipo | Vendor lock-in, caro a escala, difícil migrar |
| D: Vercel + Neon DB | Serverless, zero ops | Caro con video streaming, límites de ancho de banda |

---

## Consequences

- El servidor OVH necesita espacio en disco para videos (presupuestar 50-100GB inicial)
- nginx necesita módulo lua o auth_request para validar JWT
- Stripe conecta más rápido pero MP es mejor para LATAM → mantener ambos
- React Native permite código compartido pero requiere调试 en ambas plataformas

---

## Lessons

Separar la API del frontend desde el día 1 permite que web y mobile consuman los mismos endpoints. No hacer monolith.

---

## Related

- Spec: `SPEC-20260630-012`
- ADR-001: Identidad de marca
