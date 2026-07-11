# EMP-001 — Ephemeral Content Model (Modelo de Contenido Efímero)

| Campo | Valor |
|-------|-------|
| **ID** | `EMP-001` |
| **Spec** | `SPEC-20260630-012` |
| **Fecha** | 2026-06-30 |
| **Estado** | aceptado |

---

## 1. The Core Idea

> **"Watch once, then it's gone — unless you pay to keep it."**

Mystika no vende acceso perpetuo. Vende **momentos**. Cada video, cada foto, cada lección es una experiencia que se consume. Como un ritual que ocurre una vez y luego desaparece.

Esto genera:
- **Escasez artificial** → el usuario valora más lo que va a perder
- **Mayor LTV** → cada contenido puede monetizarse múltiples veces
- **Protección natural** → menos contenido filtrado (no hay archivos que acumular)
- **Engagement diario** → el usuario vuelve porque sabe que pierde el acceso
- **Diferenciación** → no es "otro OnlyFans", es una experiencia efímera

---

## 2. Matriz de Acceso por Nivel

| Tipo de contenido | Free | Mysteria ($14.99/mes) | Ritual ($49.99/mes) |
|---|---|---|---|
| **Preview lección (30s)** | ✅ Ilimitado | ✅ Ilimitado | ✅ Ilimitado |
| **Lección completa** | ❌ | 🔥 1 vista | 🌟 Ilimitado (retención incluida) |
| **Foto NSFW** | ❌ (borroso) | 🔥 1 vista (24h) | 🔥 1 vista (7 días) |
| **Video NSFW** | ❌ | 🔥 1 vista (24h) | 🔥 1 vista (48h) |
| **Streaming en vivo** | ❌ | ✅ Ver en vivo | ✅ Ver en vivo + grabación (1 vista) |
| **Chat con Lilith** | ❌ | 20 msg/día | Ilimitado |
| **Retener contenido** | ❌ | Pago extra | Pago extra (descuento) |
| **Descargar contenido** | ❌ | Pago extra | Pago extra (descuento) |

**Leyenda:**
- ❌ = Sin acceso
- ✅ = Acceso normal
- 🔥 = Acceso efímero (se consume)
- 🌟 = Acceso perpetuo / rewatch ilimitado

---

## 3. Flujo de usuario: Compra → Vista → Consumo

```
COMPRA / SUSCRIPCIÓN
    │
    ▼
USUARIO ABRE VIDEO
    │
    ├──► Si es suscriptor Ritual → token con max_views = -1 (ilimitado)
    │
    └──► Si es compra individual o Mysteria
            → token con max_views = 1 (efímero)
            → expires_at = now + 48h (tiene 48h para usar su 1 vista)
    │
    ▼
USUARIO VE EL VIDEO
    │
    ├──► Reproductor reporta:
    │      video_started → view_count++
    │      video_completed → token.invalidate() [excepto Ritual]
    │
    ▼
VIDEO CONSUMIDO
    │
    ├──► UI cambia a "Consumido 🔥"
    │      Muestra opciones:
    │      • Retener por $X.XX → rewatch ilimitado
    │      • Descargar por $X.XX → archivo con watermark
    │      • "Volver al catálogo"
    │
    └──► Notificación push opcional:
           "Tu ritual con [lección] ha terminado.
            ¿Quieres conservarlo en tu altar?"
```

---

## 4. Modelo de precios de retención/descarga

### Precios base (por defecto)

| Contenido | Retener | Descargar |
|-----------|---------|-----------|
| Lección individual ($14.99) | +$7.49 | +$14.99 |
| Lección comprada por Mysteria | +$4.99 | +$9.99 |
| Foto NSFW suelta | +$2.99 | +$5.99 |
| Pack de fotos (5-10) | +$9.99 | +$19.99 |
| Video NSFW suelto | +$4.99 | +$9.99 |
| Video NSFW premium | +$9.99 | +$19.99 |
| Curso completo ($49.99) | +$19.99 | +$39.99 |
| Grabación de live | +$5.99 | +$11.99 |

### Descuentos por plan

| Plan | Retener | Descargar |
|------|---------|-----------|
| Free | Precio completo | Precio completo |
| Mysteria | -20% | -20% |
| Ritual | -40% | -40% |

### Ejemplo de upsell real

```
Usuario compra lección "Ritmos Fundamentales" por $14.99
    → La ve una vez
    → Ve pantalla post-consumo:
      
      ┌──────────────────────────────┐
      │   🔥 Ritual consumido        │
      │                               │
      │   "Ritmos Fundamentales"      │
      │                               │
      │   ¿Quieres conservarlo?       │
      │                               │
      │   [💾 Retener - $7.49]       │
      │   [⬇️ Descargar - $14.99]   │
      │   [← Volver al catálogo]     │
      │                               │
      │   (como suscriptor Ritual     │
      │    tendrías retención gratis) │
      │   [🔮 Ver planes]            │
      └──────────────────────────────┘
      
    → Si elige retener: paga $7.49 → token se vuelve perpetuo
    → Si elige descargar: paga $14.99 → se genera enlace de descarga
      con watermark + expiry 7 días
    → Si elige suscribirse a Ritual ($49.99):
      obtiene retención gratis + todo el contenido del plan
```

---

## 5. Watermark en descargas

Todo archivo descargable lleva watermark visible para trazabilidad:

```
Formato: @{username} · mystika.app · {email}
Ejemplo: @mystic_drummer · mystika.app · m****@gmail.com
```

**Implementación técnica:**
- FFmpeg overlay text en el video
- 3 posiciones rotativas (esquina superior derecha, inferior izquierda, centro)
- Cambia de posición cada 30 segundos
- Opacidad 12-15% — visible al buscar pero no arruina la experiencia
- Para fotos: texto en diagonal cruzando la imagen

---

## 6. Efectos en el negocio

| Métrica | Sin efímero | Con efímero | Diferencia estimada |
|---------|-------------|-------------|---------------------|
| ARPU (ingreso por usuario) | $14.99/mes | $22-28/mes | +50-80% |
| LTV a 6 meses | $89.94 | $150-170 | +70-90% |
| Tasa de re-compra | 10% | 30-40% | +200-300% |
| Contenido filtrado | Alto | Muy bajo | -90% |
| Engagement semanal | 1-2 visits | 4-7 visits | +200% |

**Por qué funciona para NSFW:**
- El contenido adulto tiene valor justo en el momento de consumo, no como archivo
- La escasez genera deseo — saber que se va a perder hace que quieran verlo más
- La retención/descarga es un "lujo" que pocos pagan, pero los que pagan generan alto margen
- Diferencia la plataforma de OnlyFans, ManyVids, etc.

---

## 7. Consideraciones técnicas

- **Invalidez de token:** Cuando `view_count >= max_views` y `max_views > 0`, el token expira automáticamente
- **Rewatch parcial:** Si el usuario ve 70% y cierra, cuenta como vista consumida (puede debatirse)
- **Descargas:** Enlace temporal firmado con JWT, expires en 7 días, un solo uso
- **Reembolsos:** Si el usuario pide reembolso de retención/descarga, se revoca el token/URL
- **Backup:** Aunque el contenido se "borra" para el usuario, Lilith siempre tiene el original

---

## 8. Naming Mystika

| Concepto | Nombre | UX Copy |
|----------|--------|---------|
| Consumir vista | El ritual se cumplió | "Tu ritual ha terminado. La música se llevó el momento." |
| Retener | Consagrar en tu altar | "Consagra este ritual en tu altar personal." |
| Descargar | Llevar el talismán | "Lleva este talismán contigo donde vayas." |
| Contenido consumido | Recuerdo | "Un recuerdo de tu ritual con Lilith." |
| Biblioteca personal | El Altar | "Tu altar. Los rituales que has consagrado." |
