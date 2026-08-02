# SESSION 2026-07-10 — ABE Music Group + Mystik AI + SaaS Platform

> **32 commits · ~15 horas de sesión · 3 productos principales construidos**

---

## 1. Commit History (32 commits)

### Fase 1 — Core SaaS Platform (commits 1-8)

| Commit | Descripción |
|--------|-------------|
| `260bf4f` | MCP nativo + Redis agent bus + CLIs + contexto compartido |
| `cfa7dc5` | Seguridad Fase 1: rate limiting, CORS, headers, fail2ban, age encrypt |
| `92e8055` | Fase 2: PostgreSQL hardening + Redis ACL + prompt injection |
| `7983893` | Cleanup: eliminar apps/agent_metrics stub |
| `57b3951` | Mystik production-ready: Twenty entrypoint, voz sample, onboard UI, cron |
| `35eafb3` | Fix email: luis@ → sonoradigitalcorp@gmail.com |
| `d64ecb5` | Fix: ABE operational — n8n, ABE Service, Daemon |
| `54aaacb` | Session summary + engram memory |

### Fase 2 — ABE Music Group Platform (commits 9-17)

| Commit | Descripción |
|--------|-------------|
| `d0636da` | ABE Music OS: landing page + API docs |
| `da01761` | Next.js Pro Max: Tailwind + Framer Motion |
| `545b710` | SaaS con login/signup + planes sin exposición interna |
| `bd399bf` | SaaS completo: auth, signup, dashboard, planes, servicios |
| `d2ad738` | Onboarding wizard + pricing page |
| `7d8269b` | Mercado Pago MCP + reorganización productos |
| `c32ab45` | Mystik-first landing + auto-login + multi-tenant |
| `2a90565` | ABE Music como cliente independiente (Powered by SDC) |
| `ce33d1d` | ABE Music Group: landing + artistas dinámicos + servicios |

### Fase 3 — ABE Profesional (commits 18-25)

| Commit | Descripción |
|--------|-------------|
| `c54969c` | ABE Music: AI assistant + LoRA training + content gen + Telegram bots |
| `82ba0fd` | Mystik inteligente: DeepSeek + Neo4j + Engram + ChromaDB |
| `606f33b` | Mystik orientada a servicios: sin mencionar stack técnico |
| `0806074` | ABE Database: PostgreSQL con datos reales de artistas ($479K) |
| `60e2aed` | ABE Redesign: carrusel, FOMO, ABE Films, clon digital, admin |
| `860b3d0` | ABE Music rebrand: gold/black/red + Three.js + bots + Lovable components |
| `c76e2e6` | 3 páginas: ABE Music + ABE Films + Artista fan-facing |
| `8806438` | Hector Rubio: foto real desde Spotify + datos reales |

### Fase 4 — Datos Reales + Media (commits 26-32)

| Commit | Descripción |
|--------|-------------|
| `73c38c7` | Fotos reales de artistas desde Deezer + Spotify |
| `8712f46` | Spotify IDs reales + fotos para los 3 artistas |
| `f3dea1b` | Datasets LoRA para 3 artistas en HuggingFace |
| `84ef526` | Flux AI images generadas |
| `75fe2b7` | Flux gallery + ABE Films demos integrados |

---

## 2. Arquitectura Actual

```
abe.sonoradigitalcorp.com
│
├── / → Landing ABE Music Group
│     ├─ Hero 3D (Three.js) con SplitHeadline + RotatingPhrases
│     ├─ Beneficios (ClickableCards)
│     ├─ Carrusel de artistas con fotos reales
│     ├─ Círculo ABE (FOMO)
│     └─ ABE Films + Clon Digital + Planes
│
├── /artist/{slug} → Página fan-facing del artista
│     ├─ Hero con foto + stats + redes (Spotify, Instagram)
│     ├─ Tienda: merch, experiencias, galería Flux
│     ├─ Eventos: boletos, booking
│     └─ Biografía, logros, redes
│
├── /service/abe-films → Todo lo que obtiene el artista
│     ├─ Features, demos Flux, planes
│     └─ Lo que puede vender (8 fuentes de ingreso)
│
└── /service/digital-clone → Clon digital para ventas
```

## 3. Backend

| Componente | Tecnología | Puerto |
|-----------|-----------|--------|
| **Mystik API** | FastAPI + DeepSeek + Neo4j + Engram | :5200 |
| **ABE API** | PostgreSQL (artistas, releases, contratos) | :5180 |
| **PostgreSQL** | 4 tablas: artists, releases, revenue_entries, contracts | :5433 |
| **Neo4j** | Knowledge graph (consultado en cada chat) | :7687 |
| **ChromaDB** | Vector store (RAG) | :8001 |
| **Redis** | Agent bus, contexto compartido | :6380 |
| **Engram** | Memoria de conversaciones (SQLite) | state/engram.db |

## 4. Artistas registrados

| Artista | Spotify ID | Revenue | Streams | Fotos |
|---------|-----------|---------|---------|-------|
| Hector Rubio | `2uSJ9ywE44eIRoTMatARAy` | $460,372 | 115,093,009 | 3 (Spotify, Deezer, Flux) |
| Jesus Urquijo | `1hfrbMUDkM2tlUE85D3dR6` | $18,540 | 4,635,222 | 33 (Spotify) |
| Javier Arvayo | `0td9IOgiffWGMbcz3xKy0s` | $200 | 50,000 | 13 (Spotify) |

## 5. Bots de Telegram

| Bot | Handle | Token | Función |
|-----|--------|-------|---------|
| ABE Group Bot | `@abemusicgroup_bot` | `8096575456:...` | Asistencia + suscriptores |
| ABE Assistant | `@abeassistant_bot` | `8645816867:...` | Canal público + ventas |

## 6. Datasets LoRA (HuggingFace)

| Dataset | Imágenes | Usuario |
|---------|----------|---------|
| `Perry699/hector-rubio-lora-dataset` | 6 | Pendiente de entrenar |
| `Perry699/jesus-urquijo-lora-dataset` | 20 | Pendiente de entrenar |
| `Perry699/javier-arvayo-lora-dataset` | 15 | Pendiente de entrenar |

## 7. Servicios y Planes

| Plan | Precio | Servicios incluidos |
|------|--------|-------------------|
| **Starter** | $0/mes | Mystik Chat |
| **Pro** | $49/mes | Mystik + ABE Films + Content Studio + OmniVoice |
| **Enterprise** | $199/mes | Todo + Clon Digital + Distribución |

## 8. Integraciones

| Integración | Estado |
|------------|--------|
| **Mercado Pago** | API lista, MCP tool creada, falta token |
| **OpenRouter (DeepSeek)** | ✅ Activo |
| **Neo4j** | ✅ Conectado |
| **PostgreSQL** | ✅ Datos reales |
| **Telegram Bots** | ✅ 2 bots creados |
| **HuggingFace Datasets** | ✅ 3 datasets LoRA |
| **Flux AI** | ⚠️ ZeroGPU quota limitada |

## 9. Stack Frontend

| Tecnología | Uso |
|-----------|-----|
| **Next.js 16** | Framework |
| **Three.js** + @react-three/fiber | 3D hero |
| **Framer Motion** | Animaciones (SplitHeadline, RotatingPhrases, Reveal, ClickableCard) |
| **Tailwind CSS** | Estilos |
| **shadcn/ui** | Componentes base |
| **Lucide Icons** | Iconografía |
| **Cormorant Garamond** | Tipografía display |
| **Inter** | Tipografía sans |

## 10. Pendiente

| Tarea | Prioridad | Dependencia |
|------|-----------|-------------|
| **Entrenar LoRAs** (HF Jobs) | Media | Crédito HF ($) |
| **Generar más Flux images** | Media | ZeroGPU quota reset |
| **Mercado Pago token** | Alta | Token de producción |
| **Conectar bots Telegram al backend** | Alta | Token de bots listo |
| **Agregar más fotos de artistas** | Baja | — |
