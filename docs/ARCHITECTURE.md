# SDC Platform Architecture

## Brand System

### Colors
```css
--primary:    #7c5cfc  /* Púrpura — acción, tecnología */
--accent:     #c8a87c  /* Dorado — confianza, premium */
--success:    #22c55e  /* Verde — operacional */
--surface:    #0a0a0a  /* Casi negro — fondo */
--text:       #c9d1d9  /* Gris claro — legibilidad */
```

### Typography
- Headings: Inter 900/800/700 (black/bold)
- Body: Inter 400 (regular)
- Mono: JetBrains Mono (código, métricas)

### Spacing Scale
xs(4px) → sm(8) → md(16) → lg(24) → xl(32) → 2xl(48) → 3xl(64) → 4xl(96)

---

## 3D Pipeline

```
Three.js Scene
├── CoreGeometry (icosahedron distorsionado, púrpura)
├── OrbitingRings × 3 (partículas orbitando en colores brand)
├── ParticleField (300 partículas flotantes)
├── Stars (1000 estrellas background)
└── Environment (city HDR lighting)
```

Cada geometría reacciona al mouse. Renderizado con `@react-three/fiber` + `@react-three/drei`.
Post-processing opcional: bloom,噪点, DOF con `postprocessing` package.

---

## Anti-Bot Detection

No usamos Google Auth. Métodos de protección:

| Método | Dónde | Cómo funciona |
|--------|-------|--------------|
| **Cloudflare Turnstile** | Formulario de contacto | Widget invisible + server-side verify |
| **Rate Limiting** | API Bridge (`/api/`) | 30 req/60s por IP (hasheada) |
| **Honeypot** | Formulario (campo oculto) | Campo invisible que solo bots llenan |

Turnstile es gratis, sin CAPTCHAs para el usuario, y respeta privacidad.

## Supabase Schema (solo datos públicos)

### Tables
| Table | RLS | Realtime | Purpose |
|-------|-----|----------|---------|
| `agent_metrics` | user_id | ❌ | Métricas históricas |
| `agent_events` | user_id | ✅ INSERT | Log de eventos real-time |
| `service_status` | public | ✅ ALL | Estado de servicios |
| `user_profiles` | user_id | ❌ | Perfiles de usuario |

### Auth
- Provider: Google OAuth
- Callback: `/app/dashboard`
- Session: JWT (1h refresh)

---

## Realtime Flow

```
Hermes Agent / Ops Agent
    │
    ├─→ INSERT agent_events ──→ Supabase Realtime ──→ Dashboard UI
    │
    └─→ UPDATE service_status ──→ Supabase Realtime ──→ Dashboard UI
```

---

## Caching Strategy

### Browser Cache
| Resource | Cache | Strategy |
|----------|-------|----------|
| HTML (app) | `no-cache` | Always revalidate |
| JS/CSS bundles | `max-age=31536000, immutable` | Content-hash in filename |
| Fonts (Inter) | `max-age=86400` | 1 day |
| API responses | `max-age=60` | 1 min, stale-while-revalidate |

### Service Worker (coming)
- Cache-first for static assets
- Network-first for API calls
- Offline fallback page

### CDN (VPS nginx)
```nginx
location /app/assets/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location /app/ {
    expires -1;
    add_header Cache-Control "no-cache, must-revalidate";
}
```

### Backend Cache
- Redis (local VPS): Session store, rate limiting
- Qdrant: Vector cache for semantic search (already running)
- Neo4j: Graph query cache (bolt driver handles)

---

## Cookie Policy

### Authentication
| Cookie | Type | Duration | Purpose |
|--------|------|----------|---------|
| `sb-{project}-auth-token` | HTTP-only | 1h | Supabase session |
| `sb-{project}-auth-token-code-verifier` | HTTP-only | Session | PKCE flow |

### Analytics (opt-in)
| Cookie | Type | Duration | Purpose |
|--------|------|----------|---------|
| `_sdc_session` | Analytics | 30 min | Session tracking |
| `_sdc_user` | Analytics | 1 year | User preferences |

No third-party cookies. No tracking without consent.

---

## RabbitMQ Integration

### Purpose
- Desacoplar eventos del event bus del frontend
- Procesamiento async de llamadas, clones, contenido
- Cola de reintentos para fallos de API externa

### Architecture
```
Agents/API ──→ Publisher ──→ RabbitMQ ──→ Consumer ──→ Worker
                    │                        │
                    ▼                        ▼
              Supabase Realtime         VPS Worker
              (Dashboard UI)            (procesamiento)
```

### Queues
| Queue | Exchange | Routing | Consumer |
|-------|----------|---------|----------|
| `sdc.calls.outbound` | `sdc.direct` | `call.create` | Call Engine Worker |
| `sdc.clone.training` | `sdc.direct` | `clone.train` | LoRA Trainer |
| `sdc.events.log` | `sdc.topic` | `event.#` | Event Logger → Supabase |
| `sdc.email.send` | `sdc.direct` | `email.send` | Mail Service |

### Installation
```bash
# VPS
docker run -d --name sdc-rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=sdc \
  -e RABBITMQ_DEFAULT_PASS=$(openssl rand -hex 16) \
  rabbitmq:4-management
```

---

## Performance Optimizations

### Current
- ✅ React.lazy + Suspense for route splitting
- ✅ Vite code splitting (async chunks)
- ✅ TailwindCSS purge (no unused CSS)
- ✅ Gzip + Brotli via nginx
- ✅ Content-hash filenames for cache busting
- ✅ Three.js imports optimized (tree-shakeable)

### Planned
- 🔲 Service Worker for offline support
- 🔲 Redis session cache for API
- 🔲 Image optimization (WebP + srcset)
- 🔲 Route preloading (intersection observer)
- 🔲 Web Workers for heavy computation (3D, data processing)

---

## Template System

Templates en `frontends/app/src/templates/`:
| Template | Usage |
|----------|-------|
| `Landing` | Página principal (hero + productos) |
| `Dashboard` | Panel de usuario autenticado |
| `Pricing` | Tabla de precios |
| `Contact` | Formulario + WhatsApp |

Cada template hereda de `tokens.js` para consistencia visual.
