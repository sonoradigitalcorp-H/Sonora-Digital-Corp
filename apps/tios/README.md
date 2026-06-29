# SIGNAL — Music Intelligence Platform

> **Plataforma de inteligencia musical para Abe Music Group**
> Descubrimiento de artistas, evaluación multi-agente, y gestión ejecutiva de signings.

---

## Estado Actual

| Componente | Estado |
|------------|--------|
| Frontend (Vercel) | ✅ `signal-music.vercel.app` — 31 rutas, 0 errores |
| Backend (15 Docker servicios) | ⏳ Esperando VPS |
| CI/CD (GitHub Actions) | ✅ 3 workflows configurados |
| SSL/TLS | ⏳ Let's Encrypt pendiente |
| Org GitHub | ⏳ `Abe-Music-Group` por crear |

## Stack

```
Frontend:  Next.js 15 + Tailwind v3 + SWR + Recharts
Backend:   NestJS + Drizzle ORM + PostgreSQL 17 (pgvector)
Workers:   BullMQ (AI, Discovery, Metrics, Alerts)
Infra:     Docker Compose + Prometheus + Grafana + Nginx
CI/CD:     GitHub Actions → DockerHub → VPS SSH
```

## 15 Servicios Docker

```
postgres (pgvector)   → Base de datos vectorial
redis                 → Colas y caché
api-gateway (:4000)   → API NestJS
web (:3000)           → Frontend Next.js
worker-discovery      → 10 conectores musicales
worker-metrics        → Métricas de artistas
worker-ai             → Scoring y forecasting
worker-alerts         → Alertas inteligentes
notification-service  → Email, SMS, push
label-copilot (:4002) → Multi-agente A&R
workflow-engine (:4003) → Workflows autónomos
integration (:4001)   → Orquestador pipeline
prometheus (:9090)    → Métricas
grafana (:3001)       → Dashboards
nginx (:80/:443)      → Reverse proxy + SSL
```

## Rutas del Frontend

```
/dashboard            → Mission Control
/command-center       → Command Center
/artists              → Artist Radar
/artists/[id]         → Artist Intelligence Dossier
/war-rooms            → War Rooms
/war-rooms/[id]       → War Room Detail
/workflows            → Workflows
/workflows/[id]       → Workflow Detail
/analytics            → Analytics
/market               → Market Intelligence
/reports              → Executive Reports
/signings             → Signing Pipeline
/playlists            → Playlist Monitor
/finance              → Financial View
/alerts               → Intelligence Alerts
/settings             → Settings
```

## Próximos Pasos

1. Crear org `Abe-Music-Group` en GitHub
2. Migrar repo a la org
3. Provisionar VPS (Hetzner CX22 recomendado — €4/mes)
4. `docker compose up` con 15 servicios
5. SSL con Let's Encrypt
6. Conectar frontend Vercel → backend VPS
7. Full stack live

---

**Abe Music Group** — *Sonora Digital Corp*
