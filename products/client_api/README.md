# Sonora Client API

FastAPI service exposing client learning data from the Sonora Memory System.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/clients` | List all clients (filter by niche, active_only) |
| GET | `/clients/stats` | Global client statistics |
| GET | `/clients/health` | Health check |
| GET | `/clients/{id}` | Client profile + recent interactions + analysis |
| POST | `/clients/{id}/interaction` | Record a client interaction |
| PUT | `/clients/{id}` | Update client profile |
| GET | `/clients/{id}/patterns` | Client-specific patterns |
| GET | `/clients/{id}/recommendations` | Recommendations for this client |
| GET | `/niches/{niche}/insights` | Aggregated niche insights |
| GET | `/insights` | All niche insights |
| GET | `/report` | Full cross-client learning report |

## Running

```bash
PYTHONPATH=/path/to/sonora-digital-corp python3 -m products.client_api.main
```

## Tests

```bash
PYTHONPATH=/path/to/sonora-digital-corp python3 -m pytest products/client_api/tests/ -v
```
