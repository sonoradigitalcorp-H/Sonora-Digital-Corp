Crea un dashboard para ABE Music (industria musical) usando Next.js 14 (App Router),
shadcn/ui, Tailwind CSS, y Hasura GraphQL como backend.

## Branding
- Colores primarios: negro (#000), dorado (#D4AF37), blanco (#FFF)
- Tipografía: Inter
- Idioma: Español
- Tono: Profesional, premium, enfocado en el artista

## Páginas

### Inicio / Resumen
Vista general con métricas clave del artista: streams totales, ingresos del mes,
próximos eventos, campañas activas. Gráficas semanales de streams.

Componentes:
- MetricCard (streams, ingresos, seguidores)
- StreamsChart (línea 7d / 30d)
- ProximosEventos (lista)
- CampaniasActivas (mini cards)

### Streams
Gráficas detalladas de reproducciones por plataforma (Spotify, Apple Music,
YouTube, TikTok). Filtro por periodo y plataforma. Comparativa mes a mes.

Componentes:
- PlataformaSelector (tabs)
- StreamsBarChart (barras por plataforma)
- TopCanciones (tabla)
- CrecimientoIndicator

### Lanzamientos
CRUD de lanzamientos programados. Calendario visual. Notificaciones y estado
de distribución.

Componentes:
- ReleaseCalendar (calendario)
- ReleaseForm (modal)
- ReleaseTable (tabla con estado)
- DistribucionStatus (badges)

### Promoción
Campañas activas y pasadas. ROI, alcance, clics, conversiones. Crear campaña.

Componentes:
- CampaignList (tabla)
- CampaignForm (modal)
- ROIMetrics (cards)
- AdSpendChart (gráfica de pastel)

### Booking
Agenda de presentaciones. Disponibilidad, cotizaciones, eventos confirmados.

Componentes:
- AvailabilityCalendar
- CotizacionesTable
- EventosTimeline

### Finanzas
Ingresos vs gastos, reportes mensuales, conciliación con Contpaqi.

Componentes:
- BalanceChart (área)
- TransaccionesTable (con filtro tipo/fecha)
- ReporteMensualCard
- ContpaqiStatus (badge de conciliación)

## Integraciones
- Hasura GraphQL en /v1/graphql
- WebSocket para streams en tiempo real
- WhatsApp para notificaciones de eventos y lanzamientos
- Exportar reportes financieros a PDF/CSV

## Deploy
- Destino: Coolify
- Variables de entorno: NEXT_PUBLIC_HASURA_URL, NEXT_PUBLIC_TENANT_ID, NEXT_PUBLIC_ABE_ARTIST_ID

## Requisitos técnicos
- Responsive (mobile-first) — el artista revisa en celular
- SSR para SEO en landing de lanzamientos
- PWA-ready para instalar en homescreen
- Tiempo de carga < 3s
- Lighthouse score > 85
- Modo oscuro por defecto (artista lifestyle)
