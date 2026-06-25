# AGENTS.md — OpenClaw Agent Configuration
## Sonora Digital Corp System Description

This file is consumed by OpenClaw (`~/.openclaw/`) and describes the entire system architecture for AI agents.

## System Overview

This is a VPS-hosted AI infrastructure for Sonora Digital Corp running on OVH (149.56.46.173). All services are containerized via Docker Compose. Local AI inference via Ollama. Cloud fallback via OpenCode Go.

## Connection

```bash
ssh -i ~/.ssh/id_ed25519_sdc ubuntu@149.56.46.173
```

## Infrastructure Map

- nginx + certbot SSL: sonoradigitalcorp.com, n8n.sonoradigitalcorp.com
- Docker: Neo4j (7474/7687), Qdrant (6333/6334), PostgreSQL (5432), Redis (6379), n8n (5678)
- Ollama: nomic-embed-text (274MB, 768-dim), qwen2.5:1.5b (~1.1GB)
- Systemd: abe-server.service (8080), abe-telegram-bot.service
- n8n API: https://n8n.sonoradigitalcorp.com (JWT auth)

## MCP Servers

MCP servers are defined in `mcp-servers.json` at root. All servers connect to local Docker containers on 127.0.0.1.

## Models

- **Embeddings**: nomic-embed-text (local Ollama, 768-dim)
- **Chat**: qwen2.5:1.5b (local Ollama) or deepseek-v4-flash (OpenCode Go fallback)
- **Always prefer local models**. Use cloud fallback only when local response >5s.

## Directory Structure

- `~/sdc/`: All production files
- `~/sdc/ref/`: Bibliography, Methodology, Glossary
- `~/sdc/config/`: Unified MCP and workflow configs
- `~/sdc/scripts/`: Automation scripts
- `~/sdc/mcp/`: MCP ecosystem (gateway, CLI, SDK, servers)
- `~/sdc/data/`: Data files (abe-music.json)
- `~/sdc/static/`: Static HTML/JS for nginx
- `~/sdc/n8n-workflows/`: All n8n workflow JSONs

## Methodology

Pipeline: VDD -> EDD -> PDD -> ODD -> SDD -> BDD -> TDD
Every feature starts with a spec (SpecKit SDD), not with code.

## Secrets

Secrets are environment variables only. Never hardcode. Key ones:
- TELEGRAM_BOT_TOKEN
- N8N_API_KEY
- Any API keys

## Crisis

If system fails: check Docker, check nginx/SSL, check Ollama, run recovery from RECOVERY.md.
