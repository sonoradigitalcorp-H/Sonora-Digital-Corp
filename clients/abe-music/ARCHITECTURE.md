# ABE Music — Architecture

**Version:** 1.0.0
**Last updated:** 2026-06-24
**Owner:** Sonora Digital Corp

---

## Overview

ABE Music is a label management platform for Abraham's record label. It provides:
- Artist & release data management via REST API
- Real-time dashboard for streaming KPIs
- Telegram bot for on-demand reports and automated notifications

---

## Infrastructure

### Production Server

| Property | Value |
|---|---|
| Provider | OVH (VPS) |
| IP | 149.56.46.173 |
| Domain | sonoradigitalcorp.com |
| OS | Ubuntu 26.04 |
| RAM | 11 GB |
| Storage | 96 GB SSD |

### Services

| Service | Type | Port | Status |
|---|---|---|---|
| Nginx | Reverse proxy | 80/443 | System service |
| ABE API | FastAPI (Python) | 8080 | System service (abe-server) |
| Telegram Bot | Python long-poll | — | System service (abe-telegram-bot) |
| PostgreSQL 15 | Database | 5432 | Docker (sdc-postgres) |
| Redis 7 | Cache | 6379 | Docker (sdc-redis) |
| Neo4j 5 | Graph DB | 7474/7687 | Docker (sdc-neo4j) |
| Qdrant | Vector DB | 6333/6334 | Docker (sdc-qdrant) |

### Network Flow

```
User Browser
    │
    ▼
https://sonoradigitalcorp.com/
    │
    ▼
Nginx (port 443, SSL)
    ├── / → /home/ubuntu/sdc/static/abe-command-center.html (dashboard)
    ├── /static/ → static files
    ├── /api/ → proxy to ABE API (localhost:8080)
    └── /health → proxy to ABE API /health
```

### ABE API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Service health check |
| `/api/abe/dashboard/ceo` | GET | CEO dashboard KPIs |
| `/api/abe/artists` | GET | List all artists |
| `/api/abe/artists/{id}` | GET | Single artist detail |
| `/api/abe/artists` | POST | Create artist |
| `/api/abe/dashboard/artist/{id}` | GET | Artist-specific KPIs |

### Telegram Bot

| Property | Value |
|---|---|
| Username | @Gucci_ortega_bot |
| Token | In `/home/ubuntu/sdc/.env` and `.env.local` |
| Chat ID | Abraham: 5738935134 |
| Commands | `/kpi`, `/full`, `/artistas`, `/dashboard` |

---

## Directory Layout (Production)

```
/home/ubuntu/sdc/
├── abe_server.py              # FastAPI server
├── docker-compose.yml          # Core services (PG, Redis, Neo4j, Qdrant)
├── .env                        # Environment variables (tokens, secrets)
├── data/
│   └── abe-music.json          # Artist & release data
├── static/
│   └── abe-command-center.html # Dashboard HTML
├── scripts/
│   └── abe-telegram-bot.py     # Telegram bot
├── venv/                       # Python virtual environment
└── logs/
    └── abe-telegram-bot.log    # Bot activity logs
```

---

## Data Model

### Artist

```json
{
  "id": "uuid (8 chars)",
  "nombre": "string",
  "genero": "string",
  "pais": "string",
  "status": "active | signed | development",
  "streams": "number (total Spotify streams)",
  "revenue": "number (estimated USD)",
  "releases_count": "number",
  "monthly_listeners": "number",
  "top_song": "string",
  "top_song_streams": "number",
  "spotify_url": "string",
  "instagram": "string",
  "tiktok": "string"
}
```

### Release

```json
{
  "id": "uuid",
  "artist_id": "string (FK to artist)",
  "titulo": "string",
  "tipo": "single | album",
  "streams": "number",
  "revenue": "number",
  "status": "published | draft"
}
```

Data source: JSON file at `~/sdc/data/abe-music.json`. No database — the API reads/writes this file directly.

---

## SSH Access

```bash
ssh -i ~/.ssh/id_ed25519_sdc ubuntu@149.56.46.173
```

---

## Deployment

To update the server after making local changes:

```bash
# Copy updated JSON data
scp -i ~/.ssh/id_ed25519_sdc data/abe-music.json ubuntu@149.56.46.173:~/sdc/data/

# Copy updated bot script
scp -i ~/.ssh/id_ed25519_sdc scripts/abe-telegram-bot.py ubuntu@149.56.46.173:~/sdc/scripts/

# Restart services
ssh -i ~/.ssh/id_ed25519_sdc ubuntu@149.56.46.173 "sudo systemctl restart abe-server.service"
ssh -i ~/.ssh/id_ed25519_sdc ubuntu@149.56.46.173 "sudo systemctl restart abe-telegram-bot.service"
```

---

## SSL

Certificate managed by Let's Encrypt / Certbot.

```bash
# Manual renewal test
sudo certbot renew --dry-run

# Auto-renewal: systemd timer
sudo systemctl status certbot.timer
```
