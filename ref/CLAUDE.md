# CLAUDE.md — Claude Code Configuration
## Sonora Digital Corp System Description

This file is consumed by Claude Code (claude.ai) and describes how to interact with the SDC infrastructure.

## Project Structure

This is a dual-environment project:
- **VPS (production)**: OVH 149.56.46.173 — all Docker services, Ollama, n8n
- **Local (dev)**: /home/mystic/sonora-digital-corp/ — source code, configs

## Key Paths

### Local
- `/home/mystic/sonora-digital-corp/`: Main project directory
- `/home/mystic/sonora-digital-corp/config/n8n/`: n8n workflows (general)
- `/home/mystic/sonora-digital-corp/config/n8n-sdc/`: n8n workflows (SDC-specific)
- `/home/mystic/sonora-digital-corp/apps/`: Web UI, Hermes bridge
- `/home/mystic/sonora-digital-corp/data/abe-music.json`: Real artist data
- `/home/mystic/sonora-digital-corp/ref/`: Reference library (BIBLIOGRAPHY.md, METHODOLOGY.md, etc.)
- `/home/mystic/.hermes/`: Hermes Agent config
- `/home/mystic/.openclaw/`: OpenClaw config
- `/home/mystic/.config/opencode/`: OpenCode config
- `/home/mystic/jarvis/`: JARVS Core

### VPS
- `~/sdc/`: All production files
- `~/sdc/ref/`: Reference library
- `~/sdc/config/`: Unified configs
- `~/sdc/scripts/`: Automation scripts
- `~/sdc/mcp/`: MCP ecosystem
- `~/sdc/static/`: Static files for nginx
- `~/sdc/docker-compose.yml`: All containers
- `~/sdc/abe_server.py`: ABE FastAPI
- `~/sdc/data/abe-music.json`: Artist data

## Workflow for Changes

1. Always check `ref/METHODOLOGY.md` first
2. Follow pipeline: VDD -> EDD -> PDD -> ODD -> SDD -> BDD -> TDD
3. Write spec before code (SpecKit SDD)
4. Use local models first (Ollama on VPS)
5. Test locally before pushing to VPS

## Tests

- Python: `pytest` in respective directories
- No formal test framework established yet — verify manually

## SSH Access

```bash
ssh -i ~/.ssh/id_ed25519_sdc ubuntu@149.56.46.173
```

## Copy to VPS

```bash
rsync -avz -e "ssh -i ~/.ssh/id_ed25519_sdc" /home/mystic/sonora-digital-corp/ref/ ubuntu@149.56.46.173:~/sdc/ref/
```
