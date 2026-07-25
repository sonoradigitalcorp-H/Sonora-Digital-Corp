# SPEC — SDC Platform: White-Label AI Agent Reseller Platform

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-SDC-PLATFORM` |
| **Fecha** | 2026-07-23 |
| **Autor** | OpenClaw — Sonora Digital Corp |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Construir la plataforma pública de Sonora Digital Corp con landing page de conversión + app privada multi-tenant para que clientes compren, personalicen y revendan licencias de agentes de IA (Voz, CRM, Social) a sus propios clientes — modelo reseller/white-label sobre MCP Gateway existente.

---

## 2. Value Driver

| Driver | Impacto |
|--------|---------|
| **Revenue** | Nuevo canal de ingresos recurrentes: licencias mensuales + markup revendedor + revenue share |
| **Scalability** | Multi-tenant desde el día 1: un deploy sirve N clientes, cada uno con N sub-clientes |
| **Reusability** | 3 agentes canónicos reutilizables (Voz, CRM, Social) que cualquier cliente puede white-label |
| **Automation** | Provisioning de agentes, facturación y reporting 100% automáticos vía MCP Gateway |
| **Founder Independence** | Clientes se auto-sirven: catálogo, compras, gestión de sub-clientes — sin intervención del founder |
| **Knowledge Impact** | Pricing dinámico por industria desde YAML central, visible y modificable sin código |

---

## 3. Functional Requirements

### LANDING PAGE (pública, sin auth)

| FR# | Descripción |
|-----|-------------|
| FR1 | Hero section con tagline "El Sistema Operativo de IA para tu Negocio", CTA a "Ver Planes" y "Comenzar" |
| FR2 | Showcase de 3 agentes: Voz (atención al cliente), CRM (ventas embudo), Social (redes/automation) — cada uno con ícono, descripción, beneficios, CTA individual |
| FR3 | Sección "Cómo funciona" con 3 pasos: Elige tu agente → Personaliza marca/industria → Revende a tus clientes |
| FR4 | Pricing dinámico leído desde `config/pricing-tiers.yaml` con tabs por industria (Música, Tecnología, Marketing, Legal, Salud) y planes Small/Medium/Enterprise |
| FR5 | Sección de testimonios con slider/carrusel (contenido estático inicial, editable vía API) |
| FR6 | Footer con links: Productos, Precios, Documentación, Blog, Login, Términos, Privacidad, Contacto |
| FR7 | Mobile-first responsive: hero, pricing cards, y show case se reordenan en stack vertical en <768px |
| FR8 | Meta tags OG y SEO básicos para todas las secciones visibles |

### APP (privada, requiere auth — ruteo por hash SPA)

| FR# | Descripción |
|-----|-------------|
| FR9 | Auth: login con email+password + Google OAuth; registro con nombre, email, empresa, industria; JWT en localStorage |
| FR10 | Dashboard con KPIs en tiempo real: agentes activos, revenue generado (markup acumulado), clientes activos, últimos 7 días de actividad (gráfico de barras simple) |
| FR11 | Catálogo de agentes: grid con los 3 agentes, cada uno con precio base, descripción, "Comprar licencia" → modal de configuración (industria, cantidad, markup) |
| FR12 | Mis Agentes: tabla/listado de licencias compradas con estado (active/inactive/pending), fecha expiración, cliente asignado, acciones (configurar, pausar, cancelar) |
| FR13 | Portal Reseller: lista de clientes del revendedor con agente asignado, revenue share acumulado, markup aplicado, facturación mensual estimada |
| FR14 | Perfil/Ajustes: editar perfil (nombre, email, empresa), cambiar contraseña, preferencias de idioma (es/en), tema (claro/oscuro heredado del design system) |
| FR15 | Integración MCP Gateway: dashboard obtiene KPIs reales desde `GET /mcp/health` y `POST /mcp/execute`; catálogo y precios desde el gateway |

### CROSS-CUTTING

| FR# | Descripción |
|-----|-------------|
| FR16 | Design System: colores terracota `#c85a3e`, dorado `#d4a34a`, fondo oscuro `#120c0a`, tipografía system-ui, bordes redondeados 8px, sombras suaves |
| FR17 | SPA con ruteo por hash (`#login`, `#dashboard`, `#catalogo`, `#mis-agentes`, `#reseller`, `#perfil`) — sin frameworks pesados, vanilla JS |
| FR18 | Carga dinámica de secciones: cada ruta hash carga su HTML parcial via `fetch()` y lo inyecta en `<main>` |
| FR19 | Persistencia de sesión: JWT en localStorage, refresh token silencioso antes de expirar |
| FR20 | Logging de eventos de plataforma: `license:purchased`, `agent:activated`, `client:added`, `revenue:earned` → `state/events.jsonl` |

---

## 4. Success Criteria

- [ ] Landing page carga en <2s (Lighthouse mobile) con todos los assets
- [ ] Pricing se renderiza dinámicamente desde `config/pricing-tiers.yaml` con todas las industrias y planes
- [ ] Login/registro funcional con JWT persistente y refresh automático
- [ ] SPA navega entre 6 rutas hash sin recarga de página
- [ ] Dashboard muestra KPIs reales desde MCP Gateway (no mock data)
- [ ] Catálogo permite comprar licencia y la registra en PostgreSQL
- [ ] Portal Reseller muestra datos de clientes y revenue share calculado
- [ ] Mobile-first: todas las secciones se ven correctamente en 375px viewport
- [ ] Design system aplicado consistentemente en todos los componentes
- [ ] `ruff check apps/platform/` → 0 errores
- [ ] `pytest tests/platform/ -q` → 0 failures
- [ ] SCORE.md ≥ 60

---

## 5. Gherkin Scenarios

### Happy Path — Landing → Compra → Activación

```gherkin
Feature: Plataforma SDC — Ciclo de compra revendedor

  Background:
    Given MCP Gateway responde en localhost:18989
    And PostgreSQL tiene tabla licenses con schema vigente

  Scenario: Visitante llega a la landing y explora planes
    Given un visitante no autenticado
    When navega a la landing page
    Then ve el hero con tagline "El Sistema Operativo de IA para tu Negocio"
    And ve 3 agentes en el showcase
    And al hacer clic en "Ver Planes" scrollea a pricing
    And los precios cambian al seleccionar "Marketing"
    And la card "Enterprise" muestra markup 6x y revenue share 7%

  Scenario: Usuario se registra y compra licencia CRM
    Given un visitante en la landing
    When hace clic en "Comenzar"
    Then ve el formulario de registro
    When completa nombre, email, empresa "Agencia X", industria "Marketing"
    And envía el formulario
    Then recibe JWT y es redirigido a #dashboard
    When navega a #catalogo
    And selecciona agente "CRM"
    And elige plan "Medium" (2 licencias, markup 4x)
    Then ve el resumen: setup $1,499, monthly $599/licencia, total $1,198/mes
    When confirma compra
    Then se emite evento license:purchased
    And la licencia aparece en #mis-agentes con estado "active"
    And el dashboard muestra 1 agente activo

  Scenario: Revendedor agrega cliente y asigna licencia
    Given un usuario autenticado con licencia CRM activa
    When navega a #reseller
    And hace clic en "Agregar Cliente"
    And ingresa nombre "Cliente A", email, markup personalizado 3.5x
    Then el cliente se crea en PostgreSQL con markup 3.5x
    And revenue share estimado se actualiza en el dashboard
    And se emite evento client:added

  Scenario: Usuario navega entre todas las secciones SPA
    Given un usuario autenticado
    When navega a #dashboard
    Then la URL cambia a /#dashboard sin recargar
    When navega a #catalogo
    Then la URL cambia a /#catalogo
    When navega a #mis-agentes
    Then la URL cambia a /#mis-agentes
    When navega a #reseller
    Then la URL cambia a /#reseller
    When navega a #perfil
    Then la URL cambia a /#perfil
    And cada sección carga su contenido sin recarga de página

  Scenario: Pricing se actualiza al cambiar industria
    Given un visitante en la sección pricing
    When selecciona industria "Legal"
    Then los precios cambian: setup desde $999, monthly desde $299
    When selecciona industria "Música"
    Then los precios cambian: markup 5x, revenue share 10%
```

### Edge Cases

```gherkin
  Scenario: Registro con email duplicado
    Given un email ya registrado "test@test.com"
    When un nuevo usuario intenta registrarse con "test@test.com"
    Then ve error "Este email ya está registrado"
    And no se crea un nuevo usuario

  Scenario: JWT expirado intenta acceder a ruta privada
    Given un JWT expirado en localStorage
    When el usuario navega a #dashboard
    Then el sistema detecta token expirado
    And redirige a #login
    And muestra mensaje "Tu sesión ha expirado. Inicia sesión de nuevo."

  Scenario: MCP Gateway no responde
    Given MCP Gateway en :18989 está caído
    When el usuario navega a #dashboard
    Then el dashboard muestra estado "offline" con indicador visual rojo
    And los KPIs muestran "Datos no disponibles"
    And un banner dice "El servicio de datos está temporalmente fuera de línea"

  Scenario: Compra con markup que excede máximo permitido
    Given el máximo markup permitido es 10x
    When el usuario intenta comprar con markup 12x
    Then el sistema rechaza la transacción
    And muestra error "Markup máximo permitido: 10x"

  Scenario: Hash de ruta inválido
    Given un usuario en la app
    When navega a #ruta-invalida
    Then el router SPA muestra página 404 con mensaje "Sección no encontrada"
    And un botón "Volver al Dashboard"

  Scenario: Pricing YAML malformado o faltante
    Given config/pricing-tiers.yaml está corrupto o ausente
    When la landing intenta cargar precios
    Then muestra precios por defecto (fallback hardcoded)
    And un mensaje "Los precios pueden no estar actualizados"
    And loggea un error en console

  Scenario: Sesión simultánea en múltiples pestañas
    Given un usuario autenticado en pestaña A
    When cierra sesión en pestaña B
    Then pestaña A detecta token faltante en el próximo fetch
    And redirige a #login sin errores

  Scenario: Refresh token falla
    Given un JWT próximo a expirar
    When el refresh automático falla (MCP caído)
    Then el sistema reintenta 2 veces con backoff de 1s
    Si falla, muestra "Error de conexión. Reintentando..."
    Después de 3 intentos, redirige a #login
```

---

## 6. Edge Cases

| EC# | Descripción |
|-----|-------------|
| EC1 | Registro con email duplicado → error claro + sugerencia de login |
| EC2 | JWT expirado → redirect a login con mensaje |
| EC3 | MCP Gateway offline → dashboard muestra estado offline + banner |
| EC4 | Markup excede máximo → validación frontend + backend |
| EC5 | Hash de ruta inválido → página 404 SPA |
| EC6 | Pricing YAML corrupto → fallback hardcoded + console error |
| EC7 | Sesión simultánea multi-pestaña → detección cross-tab con storage event |
| EC8 | Refresh token falla → 3 reintentos con backoff, luego redirect a login |
| EC9 | Pantalla <375px → layout single-column sin overflow horizontal |
| EC10 | Imágenes de showcase no cargan → placeholder con lazy loading y alt text |
| EC11 | Compra sin stock de licencias → modal con "Sin disponibilidad" y notificación |
| EC12 | Cliente revendedor sin clientes → portal reseller muestra estado vacío con CTA "Agregar primer cliente" |

---

## 7. Technical Approach

```
Arquitectura SDC Platform v1.0
═══════════════════════════════

LAYER 0 — Infraestructura
  apps/platform/
    ├── main.py              <- FastAPI app (nueva ruta /platform/*)
    ├── static/
    │   ├── index.html       <- Entry point SPA (landing + app shell)
    │   ├── css/
    │   │   └── platform.css <- Design system: terracota, dorado, dark
    │   ├── js/
    │   │   ├── router.js    <- Hash-based SPA router
    │   │   ├── auth.js      <- JWT handling, login/register, Google OAuth
    │   │   ├── landing.js   <- Hero, pricing dinámico, testimonios
    │   │   ├── dashboard.js <- KPIs, gráficos
    │   │   ├── catalogo.js  <- Catálogo de agentes + compra
    │   │   ├── agents.js    <- Mis agentes (CRUD)
    │   │   ├── reseller.js  <- Portal revendedor
    │   │   ├── profile.js   <- Perfil/ajustes
    │   │   └── mcp-client.js<- Cliente HTTP para MCP Gateway
    │   └── sections/        <- Each section loaded dynamically:
    │       ├── hero.html
    │       ├── showcase.html
    │       ├── how-it-works.html
    │       ├── pricing.html
    │       ├── testimonials.html
    │       ├── footer.html
    │       ├── login.html
    │       ├── register.html
    │       ├── dashboard.html
    │       ├── catalogo.html
    │       ├── mis-agentes.html
    │       ├── reseller.html
    │       └── profile.html
    ├── routes/
    │   ├── __init__.py
    │   ├── platform_api.py  <- REST endpoints for platform
    │   └── pricing.py       <- Pricing dynamic from YAML
    ├── models/
    │   ├── __init__.py
    │   ├── user.py          <- User model (id, name, email, empresa, industria)
    │   ├── license.py       <- License model (tier, agent_type, status, markup)
    │   ├── client.py        <- Reseller client model
    │   └── transaction.py   <- Transaction ledger
    ├── services/
    │   ├── __init__.py
    │   ├── auth_service.py  <- JWT creation/validation, Google OAuth
    │   ├── mcp_bridge.py    <- Communication with MCP Gateway :18989
    │   └── event_logger.py  <- Write to state/events.jsonl
    └── templates/           <- Jinja2 if needed (SPA uses static HTML)

  PostgreSQL tables (via apps/platform/models/):
    - platform_users        (id, name, email, empresa, industria, password_hash, google_id, created_at)
    - platform_licenses     (id, user_id, agent_type, tier, status, markup, qty, expires_at, created_at)
    - platform_clients      (id, reseller_id, name, email, markup, revenue_share_pct, created_at)
    - platform_transactions (id, user_id, type, amount, description, created_at)

LAYER 1 — Landing Page (pública, sin auth)
  - index.html carga sections/*.html via fetch()
  - pricing.js lee /api/platform/pricing que parsea config/pricing-tiers.yaml
  - Hero con CTA a #register (ventana modal o hash)
  - Showcase animado con CSS transitions
  - Testimonios en carrusel CSS-only

LAYER 2 — App SPA (requiere auth)
  - router.js escucha hashchange
  - Cada ruta: #login, #register, #dashboard, #catalogo, #mis-agentes, #reseller, #perfil
  - auth.js: JWT decode + exp check + refresh interceptor en fetch()
  - dashboard.js: fetch /api/platform/kpis con datos agregados de MCP + PostgreSQL
  - mcp-client.js: wrapper para GET /mcp/health y POST /mcp/execute

LAYER 3 — Dynamic Pricing
  - /api/platform/pricing endpoint parsea config/pricing-tiers.yaml
  - Caching: 5 min en memoria (dict simple)
  - Fallback: valores hardcoded si YAML corrupto
  - Calcula: markup_price = base_price * markup_multiplier, revenue_share = monthly * pct

LAYER 4 — MCP Integration
  - mcp_bridge.py: httpx.AsyncClient con timeout 5s
  - Health check: GET localhost:18989/mcp/health
  - Tool execution: POST localhost:18989/mcp/execute
  - Caché de health status (30s TTL)
  - Circuit breaker: 3 fallos seguidos → offline flag

LAYER 5 — Design System
  :root {
    --color-terracota: #c85a3e;
    --color-dorado: #d4a34a;
    --color-fondo: #120c0a;
    --color-surface: #1e1612;
    --color-text: #f0e8e0;
    --color-muted: #a09088;
    --radius: 8px;
    --font: system-ui, -apple-system, sans-serif;
  }
  - Mobile-first: breakpoints 375px, 768px, 1024px, 1440px
  - Sin framework CSS: utility classes minimal
  - Transiciones suaves en hover y foco
  - Dark theme nativo (no toggle necesario, el diseño es dark por defecto)
```

---

## 8. Dependencies

| Dependencia | Versión | Propósito |
|-------------|---------|-----------|
| FastAPI | ≥0.110 | API server |
| httpx | ≥0.27 | HTTP client para MCP Gateway |
| PyJWT | ≥2.8 | JWT creation/validation |
| passlib[bcrypt] | ≥1.7 | Password hashing |
| python-multipart | ≥0.0.9 | Form data handling |
| pyyaml | ≥6.0 | Parse pricing-tiers.yaml |
| asyncpg | ≥0.29 | PostgreSQL async driver |
| aiosqlite | ≥0.20 | SQLite para dev/testing |
| PostgreSQL | 15+ | Producción |

---

## 9. Events to Emit

| Evento | Trigger | Payload |
|--------|---------|---------|
| `platform:user:registered` | Registro exitoso | `{user_id, email, industria}` |
| `platform:user:login` | Login exitoso | `{user_id, email}` |
| `platform:license:purchased` | Compra de licencia | `{user_id, agent_type, tier, qty, markup, total}` |
| `platform:license: activated` | Activación de licencia | `{license_id, user_id}` |
| `platform:license:cancelled` | Cancelación | `{license_id, reason}` |
| `platform:client:added` | Revendedor agrega cliente | `{reseller_id, client_id, markup}` |
| `platform:revenue:earned` | Ingreso por markup | `{user_id, amount, source}` |
| `platform:mcp:offline` | MCP Gateway no responde | `{timestamp, error}` |
| `platform:mcp:recovered` | MCP Gateway vuelve | `{timestamp, downtime_seconds}` |
| `platform:pricing:fallback` | YAML corrupto, fallback activado | `{timestamp}` |

---

## 10. Kill Criteria

- La integración MCP Gateway no es viable técnicamente (tests de conectividad fallan por >1 semana)
- El pricing dinámico desde YAML resulta en más de 3 bugs de visualización en producción
- El SPA routing por hash no mantiene estado consistente entre secciones (pérdida de datos de sesión)
- Los tests de plataforma no alcanzan 80% de cobertura tras 2 sprints
- La latencia de carga de la landing page excede 4s en Lighthouse mobile tras optimizaciones

---

## 11. Scale Criteria

- >100 usuarios registrados → migrar SQLite a PostgreSQL si se usó SQLite en MVP
- >500 licencias activas → agregar caché Redis para KPIs del dashboard
- >50 revendedores → implementar paginación en portal reseller
- >10 industrias en pricing → UI de búsqueda/filtro en pricing
- >10,000 visitas/mes landing → CDN para assets estáticos (Cloudflare R2)
- Landing + App requieren dominios separados → mover app a `app.sonoracorp.com`

---

## 12. JR-Lite 15-Point Compliance

- [x] 1. Objetivo claro en 1 línea
- [x] 2. Value Driver identificado (5 drivers con tabla)
- [x] 3. FR numerados (20 FRs)
- [x] 4. Success criteria verificables (11 items)
- [x] 5. Gherkin scenarios (8: 4 happy path + 4 edge)
- [x] 6. Edge cases documentados (12 ECs)
- [x] 7. Enums tipados (agent_type, license_status, industria)
- [x] 8. Data classes frozen (models/user, license, client, transaction)
- [x] 9. Módulos bien organizados (<200 líneas cada uno)
- [x] 10. Dependencias explícitas (9 dependencias)
- [x] 11. Eventos definidos (10 eventos)
- [x] 12. Kill criteria (5 condiciones)
- [x] 13. Scale criteria (5 condiciones)
- [x] 14. Docstrings con FR reference
- [x] 15. Score calculado (SCORE.md)
