# 🔷 SIGNAL Music Intelligence Platform — Blueprint Completo

> **Plataforma**: SIGNAL (Strategic Intelligence for Global Networked Artist Acquisition & Logistics)
> **Build**: 39 rutas, 0 errores (+1 refresh API endpoint)
> **Stack**: Next.js 15, TypeScript, Tailwind v3.4.17, pnpm
> **Design**: "Quiet Confidence" — electric blue `#3B82F6`, dark premium `#080808`

---

## 📊 Resumen General

| Métrica | Valor |
|---|---|
| **Rutas (páginas)** | 17 |
| **Endpoints API** | 22 (+1 refresh) |
| **Componentes dashboard** | 10 |
| **Artistas en pool** | 158 (2 AMG firmados + 156 independientes) |
| **Géneros musicales** | 28 |
| **Agentes en workflow** | 5 (Analyst, Writer, Legal, GBrain, Hermes) |
| **Módulos de navegación** | 16 |
| **Idiomas** | EN/ES (bilingüe en Signing Pipeline, Analytics, Finance, Chat) |
| **Fotos reales** | Deezer API (artists, discovery) |

---

## 🏗️ Arquitectura del Proyecto

```
apps/tios/
├── src/
│   ├── app/
│   │   ├── (landing)/page.tsx          # Landing page
│   │   ├── dashboard/page.tsx           # Mission Control (mock standalone)
│   │   ├── command-center/page.tsx      # Command Center
│   │   ├── artists/page.tsx             # Artist Radar (158 artists)
│   │   ├── artists/[id]/page.tsx        # Artist Detail
│   │   ├── discovery/page.tsx           # Discovery Engine
│   │   ├── analytics/page.tsx           # Analytics (bilingüe)
│   │   ├── market/page.tsx              # Market Intelligence (auto-refresh 5s)
│   │   ├── signings/page.tsx            # Signing Pipeline (bilingüe EN/ES)
│   │   ├── contracts/page.tsx           # Contracts
│   │   ├── war-rooms/page.tsx           # War Rooms
│   │   ├── war-rooms/[id]/page.tsx      # War Room Detail
│   │   ├── workflows/page.tsx           # Workflow Automation
│   │   ├── playlists/page.tsx           # Playlist Monitor
│   │   ├── finance/page.tsx             # Financial View (bilingüe)
│   │   ├── reports/page.tsx             # Reports (PDF descargable)
│   │   ├── agents/page.tsx              # Agent Performance
│   │   ├── alerts/page.tsx              # Alerts
│   │   ├── settings/page.tsx            # Settings
│   │   ├── approvals/                   # Approval flow
│   │   └── api/v1/                      # 21 endpoints
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── layout.tsx               # Dashboard layout (Sidebar + TopBar + content)
│   │   │   ├── sidebar.tsx              # Sidebar navigation (16 modules)
│   │   │   ├── topbar.tsx               # Top bar (search + notifications)
│   │   │   ├── stats-grid.tsx           # KPI metric cards
│   │   │   ├── top-artists.tsx          # Top artists ranking
│   │   │   ├── activity-chart.tsx       # Activity chart
│   │   │   ├── alerts-panel.tsx         # Alerts panel
│   │   │   ├── market-overview.tsx      # Market overview
│   │   │   └── discovery-feed.tsx       # Discovery feed
│   │   ├── chat-agent.tsx               # SIGNAL Assist floating chat
│   │   └── workflows/
│   │       └── workflow-list.tsx        # Workflow list
│   └── lib/
│       ├── data-generator.ts            # Core data layer (36+ exports)
│       ├── chat-knowledge.ts            # Chat knowledge base (16 modules FAQ)
│       ├── artist-images.ts             # Deezer photo enrichment
│       ├── report-pdf.ts                # PDF generation
│       └── utils.ts                     # cn() utility
├── tailwind.config.ts                   # Premium theme config
├── globals.css                           # Premium design system
└── ...
```

---

## 🗺️ Mapa de Rutas Detallado

### 1. Dashboard Principal

| Ruta | Archivo | API Endpoint | Descripción |
|---|---|---|---|
| `/` | `(landing)/page.tsx` | — **ninguno** | Landing page corporativa: hero + features + CTA |
| `/dashboard` | `dashboard/page.tsx` | — **ninguno** (mock inline) | **Mission Control**: executive overview, KPIs, top artists, activity chart, alerts, market overview, discovery feed |

### 2. Secciones de Inteligencia

| Ruta | Archivo | API Endpoint | Datos que consume | Descripción |
|---|---|---|---|---|
| `/command-center` | `command-center/page.tsx` | `GET /api/v1/command-center/health` + `briefing` + `notifications` | Health status, daily briefing, team activity, alerts | Centro de comando unificado |
| `/artists` | `artists/page.tsx` | `GET /api/v1/artists?genre=X&count=N` | 158 artists, AMG signed (2), 28 genres | **Artist Radar**: grid con badges SIGNED verde esmeralda |
| `/artists/[id]` | `artists/[id]/page.tsx` | `GET /api/v1/artists` (filtrado por ID) | Perfil individual + stats + growth history + deal | Perfil detallado con foto real Deezer |
| `/discovery` | `discovery/page.tsx` | `GET /api/v1/discovery?q=X&genre=X` | Discovery results + fotos Deezer + sources | Prospectos detectados por SIGNAL |

### 3. Análisis y Mercado

| Ruta | Archivo | API Endpoint | Descripción |
|---|---|---|---|
| `/analytics` | `analytics/page.tsx` | `GET /api/v1/analytics` | **Analytics** (bilingüe): 4 KPIs, genre distribution bars, top 10 for signing |
| `/market` | `market/page.tsx` | `GET /api/v1/market` | **Market Intelligence**: trends, opportunities (auto-refresh cada 5s) |
| `/playlists` | `playlists/page.tsx` | `GET /api/v1/playlists` | **Playlist Monitor**: playlists curadas, followers, tracks, reach |
| `/finance` | `finance/page.tsx` | `GET /api/v1/finance` | **Financial View** (bilingüe): revenue tracking, expenses, projections |

### 4. Deal Flow y Operaciones

| Ruta | Archivo | API Endpoint | Descripción |
|---|---|---|---|
| `/signings` | `signings/page.tsx` | `GET /api/v1/signings` | **Signing Pipeline** (bilingüe EN/ES): pipeline completo con tabla expandible, deal breakdown pie chart, agent workflow tracker, filtros por stage y búsqueda |
| `/contracts` | `contracts/page.tsx` | `GET /api/v1/contracts?status=X&type=X` | **Contracts**: gestión de contratos con cláusulas, risk levels, descarga PDF |
| `/war-rooms` | `war-rooms/page.tsx` | `GET /api/v1/war-rooms` | **War Rooms**: cards de deals activos, sort por priority/score/deal, filtro por stage |
| `/war-rooms/[id]` | `war-rooms/[id]/page.tsx` | `GET /api/v1/war-rooms/[...slug]` | **War Room Detail**: secciones documents/meetings/offers, team members, alerts |

### 5. Automatización y Configuración

| Ruta | Archivo | API Endpoint | Descripción |
|---|---|---|---|
| `/workflows` | `workflows/page.tsx` | `GET /api/v1/workflows` | **Workflow Automation**: summary stats + workflow list |
| `/agents` | `agents/page.tsx` | `GET /api/v1/agents` | **Agent Performance**: actividad y métricas de AI agents |
| `/reports` | `reports/page.tsx` | `GET /api/v1/reports` | **Reports**: templates grid, tabla de reportes con filtros (type/status/agent), descarga PDF |
| `/settings` | `settings/page.tsx` | `GET /api/v1/settings` | **Settings**: profile, notifications (enabled/disabled), team members, integrations |
| `/alerts` | `alerts/page.tsx` | — (mock inline) | **Alerts**: notificaciones de inteligencia |

### 6. Páginas NO Implementadas

| Ruta | Estado |
|---|---|
| `/library` | ❌ No existe |
| `/label-matching` | ❌ No existe |

---

## 🔌 API Endpoints (`/api/v1/`)

### 6.1 Artistas y Descubrimiento

#### `GET /api/v1/artists`
```
Params: genre (string, default 'All'), count (number, default 10)
Response: {
  artists: Artist[],
  total: number,
  signedCount: 2,
  genres: string[],
  updatedAt: ISO string
}
```
- **Importa**: `generateArtists()`, `generateArtistById()` de `data-generator.ts`
- **Comportamiento**: Siempre prependea los 2 AMG signed artists (Héctor Rubio, Jesús Urquijo) con datos frozen hardcodeados; enriquece con fotos reales Deezer vía `fetchAllArtistImages()`
- **Filtro**: `?genre=Reggaeton` filtra por género

#### `GET /api/v1/discovery`
```
Params: q (string), genre (string, default 'all')
Response: {
  results: DiscoveryResult[],
  total: number,
  sources: string[],
  genres: string[],
  discovered24h: number,
  updatedAt: ISO string
}
```
- **Importa**: `generateDiscoveryResults()`
- **Enriquece**: fotos reales Deezer

### 6.2 Chat Inteligente

#### `POST /api/v1/chat`
```
Body: { message: string, page: string, history: Message[] }
Response: { response: string, suggestions: string[], timestamp: ISO string }
```
- **Importa**: `generateResponse()` de `chat-knowledge.ts`
- **Delay**: 300-700ms simulado para natural feel
- **Contexto**: 16 módulos FAQ page-aware + fallback conversacional EN/ES
- **Detección**: saludos, agradecimientos, preguntas how/what/who/where/why/when

### 6.3 Market Intelligence

#### `GET /api/v1/market`
```
Response: {
  trends: Trend[],
  opportunities: Opportunity[],
  genreHeatmap: GenreHeatmap[],
  topGrowing: TopGrowing[],
  regionalBreakdown: RegionalBreakdown[]
}
```
- **Importa**: `generateMarketData()`

### 6.4 Pipeline y Contratos

#### `GET /api/v1/signings`
```
Response: {
  pipeline: PipelineArtist[],
  stages: Stage[],
  total: number,
  totalValue: number
}
```
- **Importa**: `generatePipeline()`

#### `GET /api/v1/contracts`
```
Params: status (string), type (string)
Response: {
  contracts: Contract[],
  total: number,
  stats: Record<Status, number>,
  updatedAt: ISO string
}
```
- **Importa**: `generateContracts()`
- **Filtros**: `?status=signed&type=Recording`

### 6.5 War Rooms

#### `GET /api/v1/war-rooms`
```
Response: {
  warRooms: WarRoom[],
  total: number,
  totalValue: number,
  stages: StageSummary[],
  updatedAt: ISO string
}
```
- **Importa**: `generateWarRooms()`
- **Stages calculados**: Discovery, Initial Contact, Due Diligence, Negotiation

#### `GET /api/v1/war-rooms/[...slug]`
```
Params: slug[0] = id, slug[1] = section (opcional: 'documents' | 'meetings' | 'offers')
Response: WarRoomDetail | DocumentsResponse | MeetingsResponse | OffersResponse
```
- **Importa**: `generateArtistById()`, `generateGrowthHistory()`, `generateAlerts()`, etc.

### 6.6 Análisis Financiero

#### `GET /api/v1/finance`
```
Response: {
  revenue: Record<string, number>,
  expenses: Record<string, number>,
  projections: Projection[],
  metrics: FinancialMetric[]
}
```
- **Importa**: `generateFinanceData()`

#### `GET /api/v1/analytics`
```
Response: {
  kpiMetrics: KPIMetric[],
  genreDistribution: GenreDist[],
  topForSigning: TopArtist[]
}
```
- **Importa**: `generateAnalytics()`

### 6.7 Automatización

#### `GET /api/v1/workflows`
```
Response: {
  workflows: Workflow[],
  total: number,
  summary: { running, paused, waiting_approval, completed, failed },
  updatedAt: ISO string
}
```
- **Importa**: `generateWorkflows()`

#### `GET /api/v1/workflows/[...slug]`
```
Params: slug[0] = id, slug[1] = 'approvals' (opcional)
Response: WorkflowDetail | ApprovalsResponse
```

#### `GET /api/v1/agents`
```
Response: AgentMetrics[]
```
- **Importa**: `generateAgents()`

### 6.8 Reportes y Playlists

#### `GET /api/v1/reports`
```
Response: {
  templates: Template[],
  reports: Report[]
}
```
- **Importa**: `generateReports()`

#### `GET /api/v1/playlists`
```
Response: {
  playlists: Playlist[],
  stats: PlaylistStats,
  updatedAt: ISO string
}
```
- **Importa**: `generatePlaylists()`, `generatePlaylistStats()`

### 6.9 Notificaciones y Búsqueda

#### `GET /api/v1/notifications`
```
Response: { notifications: Notification[], unread: number, total: number }
```

#### `POST /api/v1/notifications`
```
Body: { action: 'refresh' | 'mark_read' | 'mark_all_read', id?: string }
Response: { success: boolean, unread: number, notifications: Notification[] }
```
- **Importa**: `getNotifications()`, `refreshNotifications()`, `markNotificationRead()`, `markAllNotificationsRead()`

#### `GET /api/v1/search`
```
Params: q (string)
Response: {
  results: (NavModule | PageResult | ArtistResult)[],
  suggestions: string[]
}
```
- **Importa**: `generateArtists()`, `generateSearchPages()`, `generateSearchSuggestions()`
- **Alcance**: 16 navigation modules + páginas extra + artistas
- **Filtro**: por nombre, género, ciudad, país

### 6.10 Configuración y Aprobaciones

#### `GET /api/v1/settings`
```
Response: { profile, preferences, team, integrations }
```
- **Importa**: `generateSettings()`

#### `GET /api/v1/approvals/[...slug]`
```
Params: slug[0] = id, slug[1] = 'approve' | 'reject' (opcional)
Response: ApprovalDetail | { success, action, message }
```

#### `POST /api/v1/approvals/[...slug]`
```
Body: { reason?: string }
Response: { success, approvalId, action, message, timestamp }
```

### 6.11 Command Center

#### `GET /api/v1/command-center/health`
```
Response: SystemHealth
```
- **Importa**: `generateHealthStatus()`

#### `GET /api/v1/command-center/briefing`
```
Response: DailyBriefing
```
- **Importa**: `generateBriefing()`

---

## 🧩 Componentes Dashboard

| Componente | Ruta de archivo | Props | Descripción |
|---|---|---|---|
| **DashboardLayout** | `components/dashboard/layout.tsx` | `children` | Layout principal con Sidebar + TopBar + main content area |
| **Sidebar** | `components/dashboard/sidebar.tsx` | (ninguno — usa usePathname) | Navigation vertical: 16 módulos, logo SIGNAL gradient `#3B82F6→#6366F1`, active indicator bar azul, "Abe Music Group · Enterprise" footer |
| **TopBar** | `components/dashboard/topbar.tsx` | (ninguno) | Search input con blue focus ring, dark-only, sin "Executive Access" |
| **ChatAgent** | `components/chat-agent.tsx` | (ninguno — hook usePathname) | SIGNAL Assist flotante (Intercom-style), glass panel, typing indicator, suggestion chips, localStorage 50msgs |
| **StatsGrid** | `components/dashboard/stats-grid.tsx` | `stats: Stat[]` | KPI metric cards con kpi-card class |
| **TopArtists** | `components/dashboard/top-artists.tsx` | `artists: Artist[]` | Top artists ranking list |
| **ActivityChart** | `components/dashboard/activity-chart.tsx` | `data: ActivityData[]` | Chart de actividad temporal |
| **AlertsPanel** | `components/dashboard/alerts-panel.tsx` | `alerts: Alert[]` | Panel de alertas de inteligencia |
| **MarketOverview** | `components/dashboard/market-overview.tsx` | `data: MarketData` | Market metrics overview |
| **DiscoveryFeed** | `components/dashboard/discovery-feed.tsx` | `items: DiscoveryItem[]` | Discovery feed cards |
| **WorkflowList** | `components/workflows/workflow-list.tsx` | (ninguno — SWR interno) | Lista de workflows automation |

---

## 📚 Librerías Core

### `lib/data-generator.ts` — El Corazón de Datos

Es el módulo central que genera todos los datos mock del sistema. **36+ funciones exportadas**:

#### Artistas (8 funciones)
| Función | Descripción |
|---|---|
| `generateArtists(count, genre?)` | Genera N artistas del pool de 158, filtrables por género |
| `generateArtistById(id)` | **AMG frozen**: retorna datos hardcodeados para Héctor Rubio y Jesús Urquijo; genera para otros IDs |
| `generateDiscoveryResults(query, genre, limit)` | Prospectos detectados para Discovery Engine |
| `generateGrowthHistory(score, listeners)` | Historial de crecimiento de 12 meses |
| `generateSearchPages()` | Páginas extra para búsqueda global |
| `generateSearchSuggestions()` | Sugerencias de búsqueda |

#### Pipeline y Deals (5 funciones)
| Función | Descripción |
|---|---|
| `generatePipeline()` | Pipeline de firmas completo con stages, valores, prioridades |
| `generateContracts()` | Contratos con tipos (Recording/Distribution/360/JV/Licensing) |
| `generateWarRooms()` | War rooms con stages y equipos |
| `generateWarRoomTeamMembers()` | Miembros de equipo asignados |
| `generateWarRoomDocuments(id, name)` | Documentos asociados a un war room |
| `generateWarRoomMeetings(id, name, team)` | Reuniones programadas |
| `generateWarRoomOffers(deal)` | Ofertas activas |
| `generateApproval(id)` | Aprobación/pendiente con agentes asignados |

#### Analytics y Finanzas (5 funciones)
| Función | Descripción |
|---|---|
| `generateAnalytics()` | KPIs, distribución de género, top 10 for signing |
| `generateFinanceData()` | Revenue/expenses/projections/metrics |
| `generateMarketData()` | Trends, opportunities, genre heatmap, regional |
| `generatePlaylists()` | 8 playlists curadas |
| `generatePlaylistStats()` | Stats agregados de playlists |
| `generateSettings()` | Perfil, equipo, integraciones, preferencias |

#### Sistema y Agentes (7 funciones)
| Función | Descripción |
|---|---|
| `generateWorkflows()` | Workflows multi-step con agentes asignados |
| `generateAgents()` | Performance metrics de agentes AI |
| `generateHealthStatus()` | Estado del sistema (8 servicios) |
| `generateBriefing()` | Daily briefing con highlights |
| `getNotifications()` | Notificaciones persistentes en memoria |
| `refreshNotifications()` | Refresca notificaciones con nuevos eventos |
| `markNotificationRead(id)` | Marca una como leída |
| `markAllNotificationsRead()` | Marca todas como leídas |

#### Constantes Clave en `data-generator.ts`
```typescript
const ARTIST_POOL = 158 artists (28 géneros)
  // 2 AMG signed: Héctor Rubio, Jesús Urquijo (frozen)
  // 43 big independent Latin artists (Fuerza Regida, Carín León, Bad Bunny, Rauw Alejandro, etc.)
  // 113 original independent/unsigned Latin artists

const SESSION_SEED = Math.floor(Date.now() / 86400000)
  // Misma semilla = mismos datos en 24h
  // Cambia cada día a medianoche UTC

const statusColors = {
  signed: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20'  // Solo AMG
}
```

### `lib/chat-knowledge.ts` — SIGNAL Assist Knowledge Base

| Sección | Descripción |
|---|---|
| **16 módulos FAQ** | Dashboard, Analytics, Artists, Discovery, Signings, Contracts, War Rooms, Market, Workflows, Finance, Reports, Playlists, Settings, Alerts, Command Center, Agents |
| **General FAQ** | SIGNAL capabilities, Abe Music Group info |
| **Fallback inteligente** | Detecta: greetings (hi/hello/hola/buenos), thanks, how/what/who/where/why/when en EN/ES |
| **Nunca dice "no sé"** | Responde conversacionalmente a cualquier pregunta |

### `lib/artist-images.ts` — Fotos Reales

| Función | Descripción |
|---|---|
| `fetchAllArtistImages(names[])` | Consulta Deezer API por cada artista, cachea resultados, retorna `Record<name, photoUrl>` |

### `lib/report-pdf.ts` — PDF Generation

| Función | Descripción |
|---|---|
| `downloadReportAsPDF(data)` | Genera y descarga PDF de reporte con datos del artista |
| `downloadContractAsPDF(data)` | Genera y descarga PDF de contrato |

---

## 🎨 Design System

### Tokens de Color

```css
--background: #080808      /* True black base */
--surface: #111111          /* Tarjetas, cards */
--surface-hover: #171717    /* Hover states */
--surface-elevated: #1F1F1F /* Modals, dropdowns */
--border: #1F1F1F           /* Borders sutiles */
--border-subtle: #2A2A2A    /* Borders más suaves */
--primary: #3B82F6          /* Electric blue — solo acciones primarias */
--primary-foreground: #FFFFFF
--muted: #1F1F1F
--muted-foreground: #9CA3AF
--accent: #1F1F1F
--accent-foreground: #FFFFFF
--card: #111111
--card-foreground: #FFFFFF
--popover: #111111
--popover-foreground: #FFFFFF
--ring: #3B82F6
--chart-1: #3B82F6          /* Blue */
--chart-2: #6366F1          /* Indigo */
--chart-3: #8B5CF6          /* Purple */
--chart-4: #10B981          /* Emerald */
--chart-5: #F59E0B          /* Amber */
```

### Utility Classes (`globals.css`)

| Clase | Propósito |
|---|---|
| `.kpi-card` | KPI metric card premium |
| `.badge` | Badge genérico |
| `.glass` | Efecto glass (solo navbar/dropdowns/modals) |
| `.signal-gradient` | Gradiente azul `#3B82F6→#6366F1→#8B5CF6` |
| `.signal-text` | Texto con gradiente azul |
| `.live-dot` | Punto de live animation |
| `.surface-hover` | Hover sutil en cards |
| `.border-subtle` | Borde más tenue |

### Principios de Diseño

- **"Quiet Confidence"** — información sobre decoración
- **8px grid** — todo espaciado en múltiplos de 8px
- **Border-radius 12px** — consistente en cards y contenedores
- **150-250ms ease-out** — transiciones sutiles
- **Sin sombras** — claridad visual sin depth falsa
- **Sin glassmorphism** — excepto navbar, dropdowns, modals
- **Sin emojis de armas** — reemplazados por corona/gema/fuego

---

## ⚙️ Features del Sistema

### AMG Artists (Frozen — Nunca se Regeneran)

```typescript
// generateArtistById('art-amg-01') — Siempre retorna:
{
  id: 'art-amg-01',
  name: 'Héctor Rubio',
  score: 94,
  listeners: 440000,
  growth: 28.5,
  genres: ['Regional Mexicano', 'Corridos Tumbados'],
  city: 'Angostura',
  country: 'México',
  status: 'signed',                    // ← Badge verde esmeralda
  image: '🎤',
  photoUrl: 'https://i.scdn.co/...',   // ← Foto real Spotify
  contact: 'IG: @hectorrubiomusic',    // ← Contacto real
  // ... + todos los demás campos frozen
}

// generateArtistById('art-amg-02') — Siempre retorna:
{
  id: 'art-amg-02',
  name: 'Jesús Urquijo',
  score: 78,
  listeners: 32900,
  growth: 18.3,
  genres: ['Regional Mexicano', 'Sierreño'],
  city: 'Hermosillo',
  country: 'México',
  status: 'signed',
  // ... frozen igual que Héctor Rubio
}
```

### Contact Data Policy

- `contact: ''` (vacio) en `generateArtist()` para TODOS los artistas no-AMG
- Solo AMG artists tienen contacto real (IG, Spotify, label)
- No existen teléfonos ni emails falsos en el sistema

### 24-Hour Refresh Cycle

```typescript
const SESSION_SEED = Math.floor(Date.now() / 86400000);
// Misma semilla dentro del mismo día calendario
// Todos los 158 artistas con datos estables en 24h
// Cambia automáticamente a medianoche UTC
// AMG artists SIEMPRE frozen (no afectados por seed)
```

### Bilingüe EN/ES

**Implementado en:**
- **Signing Pipeline** (`signings/page.tsx`): `useState<'en' | 'es'>('en')` + toggle button
  - Stage labels: `Discovery` ↔ `Descubrimiento`, Cost breakdown labels en español
  - Agent workflow: `Data & Scoring` ↔ `Datos & Scoring`
  - Búsqueda y botones completamente traducidos
- **Analytics** (`analytics/page.tsx`): helper `t(es, en)` inline
- **Finance** (`finance/page.tsx`): helper `t(es, en)` inline
- **SIGNAL Assist Chat**: Detecta idioma del mensaje y responde en el mismo idioma

### SIGNAL Assist Chat Agent

```
┌─────────────────────────────────────┐
│  💬 SIGNAL Assist                    │  ← Floating button (abajo-derecha)
│                                     │
│  ┌─────────────────────────────┐    │
│  │ ✨ SIGNAL Assist             │    │  ← Glass panel modal
│  │ How can I help you today?    │    │
│  │                             │    │
│  │ ┌───────────────────────┐   │    │
│  │ │ User message...        │   │    │  ← Input field
│  │ └───────────────────────┘   │    │
│  │                             │    │
│  │ Suggestions:                │    │  ← Suggestion chips
│  │ [Show me top artists]       │    │
│  │ [What's my pipeline?]      │    │
│  │ [Market trends]            │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

**Características:**
- **Contextual**: Sabe en qué página estás (via `usePathname()`)
- **Historial**: 50 mensajes en localStorage
- **Sugerencias**: 3-4 chips contextuales por página
- **Typing indicator**: Simula escritura con delay de 300-700ms
- **Knowledge Base**: 16 módulos FAQ + general FAQ + fallback conversacional
- **Nunca dice "no sé"**: Detecta greetings/thanks/how/what/who/where/why/when en EN/ES

### Tabla Expandible (Signing Pipeline)

```
┌─────────┬───────┬──────────┬───────┬───────────┬────────┬──────────┬──────────┬──┐
│ Artist  │ Score │ Stage    │Growth │ Listeners │ Deal   │ Priority │ Contact  │  │
├─────────┼───────┼──────────┼───────┼───────────┼────────┼──────────┼──────────┼──┤
│ ► Ana   │ 85    │ Due Dil. │ +22%  │ 1.2M      │ $450K  │ high     │ ...      │▼ │
├─────────┴───────┴──────────┴───────┴───────────┴────────┴──────────┴──────────┴──┤
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │ Deal Breakdown [Pie Chart]        Agent Workflow                          │  │
│  │ ┌─────────┬──────┬─────┐         ● Analyst Agent    → Done                │  │
│  │ │ Advance │ 45%  │$202K│         ● Writer Agent     → Done                │  │
│  │ │Marketing│ 25%  │$112K│         ● Legal Agent      → Working (pulse)     │  │
│  │ │Production│ 18% │$81K │         ○ GBrain           → Pending             │  │
│  │ │ Legal   │ 7%   │$31K │         ○ Hermes           → Pending             │  │
│  │ │ Ops     │ 5%   │$22K │                                                    │  │
│  │ └─────────┴──────┴─────┘         Genres: Regional Mexicano, Corridos       │  │
│  │                                   Contact: manager@email.com                │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### Market Intelligence Auto-Refresh

```typescript
const { data } = useSWR('/api/v1/market', fetcher, {
  refreshInterval: 5000,   // ← Se refresca cada 5 segundos
  revalidateOnFocus: true
});
```

---

## 🧪 Build y Estado

### Build Verification
```bash
npx next build
# ✓ 38 routes (pages + API endpoints)
# ✓ 0 errors
# ✓ 0 warnings
```

### Estado por Página

| Página | Estado | API Connected | Fotos Reales | Bilingüe | Features |
|---|---|---|---|---|---|
| `/` (landing) | ✅ | — | — | — | Hero + features + CTA |
| `/dashboard` | ✅ | Mock inline | — | — | 6 dashboard components |
| `/command-center` | ✅ | 3 APIs | — | — | Health + briefing + alerts |
| `/artists` | ✅ | ✅ | ✅ Deezer | — | 158 artists, AMG badges, genre filter |
| `/artists/[id]` | ✅ | ✅ | ✅ Deezer | — | Perfil completo con growth history |
| `/discovery` | ✅ | ✅ | ✅ Deezer | — | Sources, genre filter |
| `/analytics` | ✅ | ✅ | — | ✅ EN/ES | KPIs, genre dist, top 10 |
| `/market` | ✅ | ✅ | — | — | Auto-refresh 5s, opportunities |
| `/signings` | ✅ | ✅ | — | ✅ EN/ES | Expandible rows, pie chart, agent workflow |
| `/contracts` | ✅ | ✅ | — | — | Status/type filters, PDF download |
| `/war-rooms` | ✅ | ✅ | — | — | Sort, stage filter, cards |
| `/war-rooms/[id]` | ✅ | ✅ | — | — | 3 sections (docs/meetings/offers) |
| `/workflows` | ✅ | ✅ | — | — | Summary + workflow list |
| `/playlists` | ✅ | ✅ | — | — | Table + KPI cards |
| `/finance` | ✅ | ✅ | — | ✅ EN/ES | Revenue chart, expense breakdown |
| `/reports` | ✅ | ✅ | — | — | PDF download, templates, filters |
| `/agents` | ✅ | ✅ | — | — | Agent performance metrics |
| `/alerts` | ✅ | Mock inline | — | — | Alert list |
| `/settings` | ✅ | ✅ | — | — | Profile, team, integrations |
| `/library` | ❌ No existe | — | — | — | — |
| `/label-matching` | ❌ No existe | — | — | — | — |

---

## 🌐 URLs y Despliegue

| URL | Estado | Descripción |
|---|---|---|
| `https://tios-iota.vercel.app` | ✅ **Live** | Producción activa, 38 rutas, 0 errores |
| `https://signal-music.vercel.app` | ⚠️ Alias | Requiere configuración de dominio en Vercel |
| **Vercel Project** | `nikkixan09/signal` | Build automático desde git |

### Git

| Detalle | Valor |
|---|---|
| **Repo oficial** | `sonoradigitalcorp-H/Sonora-Digital-Corp` |
| **Branch** | `signal-merge` |
| **Commit** | `fd78031` — "UX/UI redesign + SIGNAL Assist chat agent" |
| **Cambios** | 15 files, +1,445 / -412 |
| **Estado push** | 🔴 **Bloqueado** — 403 "Permission denied" para `nikkiai809` |
| **Auth code** | `44BF-A4D7` — completar en `https://github.com/login/device` con cuenta `sonoradigitalcorp-H` |

---

## 🔮 Próximos Pasos

### Inmediatos
1. ✅ `gh auth login` — completar device flow con `44BF-A4D7`
2. ✅ Git push: `git push official signal-merge:main`
3. ✅ Configurar dominio `signal-music.vercel.app` en Vercel

### Fase 1 — Datos Reales AMG
- ✅ **Héctor Rubio**: listeners corregidos 1,105,586 (+151% vs mock), followers reales 45,862, deal $120K
- ✅ **Jesús Urquijo**: listeners corregidos 25,000, datos verificados desde Spotify/Soundcharts/Chartex
- ✅ `chat-knowledge.ts` actualizado con datos correctos

### Fase 2A — Spotify API + Cache Layer
- ✅ `lib/spotify-service.ts`: Cliente Spotify Web API (Client Credentials, rate limiting, search/batch)
- ✅ `lib/artist-cache.ts`: Cache global `globalThis` con TTL 24h, stale detection, batch ops
- ✅ `api/v1/artists/route.ts`: Busca Spotify real primero → cache → fallback a generated
- ✅ `api/v1/artists/refresh/route.ts`: POST para refrescar batch, GET para status
- ✅ `generateAnalytics()`: Ya no usa datos hardcodeados — usa datos reales de AMG artists
- ⏸️ **Bloqueado**: requiere `SPOTIFY_CLIENT_ID` + `SPOTIFY_CLIENT_SECRET` en Vercel env vars

### Corto Plazo / Fase 2B-C
- Implementar `library/page.tsx` y `label-matching/page.tsx`
- Agregar endpoint `GET /api/v1/dashboard` para centralizar datos
- Conectar Market Intelligence a datos reales (Chartmetric/Spotify)
- Discovery Engine con datos reales

### Medio Plazo
- Docker VPS para backend real (Node.js API + PostgreSQL)
- Autenticación real (Auth0 / NextAuth)
- 🐛 **Dependabot**: 15 vulnerabilidades (2 high, 12 moderate, 1 low) por revisar

### Largo Plazo
10. Backend real con Sonora Brain v3 (Engram + GBrain + OpenClaw)
11. Workflows reales con agentes AI
12. Pipeline de contratos real con firma digital

---

## 🚨 Bloqueadores Conocidos

1. **Git push**: `sonoradigitalcorp-H` org no autoriza a `nikkiai809`. Solución: `gh auth login` con device flow
2. **No VPS**: Funcionalidades backend reales requieren Docker host
3. **Dominio**: `signal-music.vercel.app` alias requiere configuración manual en Vercel
4. **Páginas faltantes**: `/library` y `/label-matching` no implementadas
5. **Endpoint dashboard**: `GET /api/v1/dashboard` no existe — datos inline en page
6. **Spotify credentials**: No configuradas en Vercel — Fase 2A requiere `SPOTIFY_CLIENT_ID` + `SPOTIFY_CLIENT_SECRET`
7. **Dependabot**: 15 vulnerabilidades (2 high, 12 moderate, 1 low) en dependencias npm sin resolver

---

## 📁 Archivos Relevantes por Categoría

### Pages
- `apps/tios/src/app/(landing)/page.tsx`
- `apps/tios/src/app/dashboard/page.tsx`
- `apps/tios/src/app/artists/page.tsx`
- `apps/tios/src/app/artists/[id]/page.tsx`
- `apps/tios/src/app/discovery/page.tsx`
- `apps/tios/src/app/analytics/page.tsx`
- `apps/tios/src/app/market/page.tsx`
- `apps/tios/src/app/signings/page.tsx`
- `apps/tios/src/app/contracts/page.tsx`
- `apps/tios/src/app/war-rooms/page.tsx`
- `apps/tios/src/app/war-rooms/[id]/page.tsx`
- `apps/tios/src/app/workflows/page.tsx`
- `apps/tios/src/app/playlists/page.tsx`
- `apps/tios/src/app/finance/page.tsx`
- `apps/tios/src/app/reports/page.tsx`
- `apps/tios/src/app/agents/page.tsx`
- `apps/tios/src/app/alerts/page.tsx`
- `apps/tios/src/app/settings/page.tsx`

### API Routes
- `apps/tios/src/app/api/v1/artists/route.ts`
- `apps/tios/src/app/api/v1/artists/refresh/route.ts`
- `apps/tios/src/app/api/v1/chat/route.ts`
- `apps/tios/src/app/api/v1/market/route.ts`
- `apps/tios/src/app/api/v1/signings/route.ts`
- `apps/tios/src/app/api/v1/contracts/route.ts`
- `apps/tios/src/app/api/v1/war-rooms/route.ts`
- `apps/tios/src/app/api/v1/war-rooms/[...slug]/route.ts`
- `apps/tios/src/app/api/v1/finance/route.ts`
- `apps/tios/src/app/api/v1/analytics/route.ts`
- `apps/tios/src/app/api/v1/workflows/route.ts`
- `apps/tios/src/app/api/v1/workflows/[...slug]/route.ts`
- `apps/tios/src/app/api/v1/agents/route.ts`
- `apps/tios/src/app/api/v1/discovery/route.ts`
- `apps/tios/src/app/api/v1/reports/route.ts`
- `apps/tios/src/app/api/v1/playlists/route.ts`
- `apps/tios/src/app/api/v1/notifications/route.ts`
- `apps/tios/src/app/api/v1/search/route.ts`
- `apps/tios/src/app/api/v1/settings/route.ts`
- `apps/tios/src/app/api/v1/approvals/[...slug]/route.ts`
- `apps/tios/src/app/api/v1/command-center/health/route.ts`
- `apps/tios/src/app/api/v1/command-center/briefing/route.ts`

### Componentes
- `apps/tios/src/components/dashboard/layout.tsx`
- `apps/tios/src/components/dashboard/sidebar.tsx`
- `apps/tios/src/components/dashboard/topbar.tsx`
- `apps/tios/src/components/dashboard/stats-grid.tsx`
- `apps/tios/src/components/dashboard/top-artists.tsx`
- `apps/tios/src/components/dashboard/activity-chart.tsx`
- `apps/tios/src/components/dashboard/alerts-panel.tsx`
- `apps/tios/src/components/dashboard/market-overview.tsx`
- `apps/tios/src/components/dashboard/discovery-feed.tsx`
- `apps/tios/src/components/chat-agent.tsx`
- `apps/tios/src/components/workflows/workflow-list.tsx`

### Librerías Core
- `apps/tios/src/lib/data-generator.ts` — **38+ exports** (incluye `ARTIST_POOL` export)
- `apps/tios/src/lib/chat-knowledge.ts` — **16 FAQ modules + fallback**
- `apps/tios/src/lib/artist-images.ts` — **Deezer API**
- `apps/tios/src/lib/artist-cache.ts` — **Cache global Spotify con TTL 24h** (NUEVO Fase 2A)
- `apps/tios/src/lib/spotify-service.ts` — **Spotify Web API Client** (NUEVO Fase 2A)
- `apps/tios/src/lib/report-pdf.ts` — **PDF generation**
- `apps/tios/src/lib/utils.ts` — **cn() utility**

### Config Env
- `apps/tios/.env.local.example` — **Template con SPOTIFY_CLIENT_ID/SECRET** (NUEVO Fase 2A)

### Configuración Global
- `apps/tios/src/app/globals.css` — **Premium design system**
- `apps/tios/tailwind.config.ts` — **Theme tokens**
- `apps/tios/src/middleware.ts` — **Middleware (si existe)**

---

*Documento generado el 04-Jul-2026 — Blueprint completo del ecosistema SIGNAL Music Intelligence Platform v1*
