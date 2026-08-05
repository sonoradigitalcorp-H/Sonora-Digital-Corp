# SDC Cowork System — OpenClaw Integration

## Overview

The SDC Cowork System unifies all Sonora Digital Corp automation under OpenClaw orchestration. It combines AI agents, browser automation, voice interfaces, and memory systems into a single coordinated workflow.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    OpenClaw Gateway                     │
│                    (port 18789)                          │
└──────────────┬───────────┬──────────────┬───────────────┘
               │           │              │
    ┌──────────┴─┐   ┌─────┴────┐   ┌─────┴────────┐
    │ CEO Agent  │   │ RYE Agent│   │ Auto-Save    │
    │ (main)     │   │ (rye)    │   │ (cron 60min) │
    └────┬───────┘   └─────┬────┘   └──────────────┘
         │                  │
    ┌────┴────┐      ┌─────┴─────┐
    │Skills   │      │Skills     │
    │- ceo-   │      │- learning-│
    │  workflow│      │  loop    │
    │- health-│      │- agent    │
    │  check  │      │  -evolver │
    │- browser-│      │- close-loop│
    │  use    │      │- reflect  │
    │- github │      │           │
    │- notion │      │           │
    └─────────┘      └───────────┘
         │
    ┌────┴─────────────────────────────────────────┐
    │          Integraciones Externas             │
    │                                             │
    │ ┌─ Whisper STT: Audio → Texto               │
    │ ├─ Sherpa TTS: Texto → Audio                │
    │ ├─ Playwright: Browser Automation           │
    │ ├─ Browser-Use: Interacciones Web           │
    │ ├─ GitHub: Control de Versiones              │
    │ ├─ Telegram: Mensajería                     │
    │ ├─ WhatsApp: Mensajería                     │
    │ ├─ Discord: Comunicación Team               │
    │ ├─ Notion: Documentación                     │
    │ ├─ PostHog: Analytics                        │
    │ └─ Healthcheck: Monitoring                  │
    └─────────────────────────────────────────────┘
```

## Components

### 1. CEO Agent (`main`)
**Purpose:** Daily operations, security, monitoring
**Skills Active:**
- `ceo-workflow`: Preflight, deploy, monitoring
- `healthcheck`: System health audit
- `browser-use`: Browser automation
- `github`: GitHub operations
- `notion`: Documentation sync
- `coding-agent`: Code generation

### 2. RYE Agent (`rye`)  
**Purpose:** Production assistant, RAG, learning
**Skills Active:**
- `learning-loop`: Self-improvement
- `agent-evolver`: Agent optimization
- `close-loop`: Session automation
- `reflect`: Decision analysis
- `openai-whisper`: Speech-to-text
- `sherpa-onnx-tts`: Text-to-speech

### 3. Auto-Save System
**Purpose:** 24/7 memory persistence
**Schedule:** Every 60 minutes
**Actions:**
- Capture system state
- Save to Neo4j memory
- Feed Qdrant embeddings
- Archive JSON snapshots

### 4. Close-Loop System
**Purpose:** End-of-session workflow
**Actions:**
- Generate session summary
- Save learnings to engram
- Update specifications
- Create ADRs and scores

## Daily Workflow

### Morning (Startup)
1. OpenClaw gateway starts
2. CEO workflow preflight:
   - Security scan (API keys, secrets)
   - Service health check (docker, bots, ollama)
   - Git status
3. Auto-save captures initial state

### During Work
1. Tasks delegated through Dispatcher
2. RYE agent handles RAG queries
3. CEO agent monitors system health
4. Auto-save runs every 60 minutes
5. Learning loop captures insights

### Evening (Shutdown)
1. Close-loop workflow:
   - Session summary
   - Lessons learned extraction
   - Specification updates
   - Memory persistence
2. Git commit automation
3. Final auto-save

## Error Prevention

Based on lessons learned:

```yaml
# Critical rules (from DOCUMENTO_DE_ERRORES)
- NUNCA hardcodear API keys → siempre os.getenv()
- NUNCA affirmer ubicación de archivos sin grep -rn primero  
- NUNCA dar comandos de BotFather sin verificar docs reales
- NUNCA dejar repo público → siempre PRIVATE
- NUNCA saltarse preflight → SIEMPRE ejecutar primero
- NUNCA asumir, SIEMPRE preguntar o verificar
```

## Integration Points

### Whisper STT/TTS
- **Input:** Voice notes → Whisper STT → Text
- **Output:** Text → Sherpa TTS → Voice response
- **Use case:** Voice-driven task management

### Playwright
- **Input:** Web automation tasks
- **Output:** Browser actions + captured data
- **Use case:** Web scraping, testing, automation

### GitHub
- **Input:** Code changes, pull requests
- **Output:** Commits, PRs, deployments
- **Use case:** Automated code review, deployment

### Telegram/WhatsApp
- **Input:** Messages from users
- **Output:** Automated responses
- **Use case:** Customer support, notifications

## Commands

```bash
# Check system status
openclaw status

# Run CEO workflow
openclaw agent --message "Status del sistema" --agent main

# Run daily automation
python3 scripts/memory-save.py
bash scripts/close-session.sh

# Health check
openclaw agent --message "run healthcheck" --agent main

# Manual skill execution
openclaw <skill-name> --help
```

## Success Metrics

- **System Health:** >99.5% uptime
- **Response Time:** <2 seconds for 95% of queries
- **Error Rate:** <1% for automated tasks
- **Learning:** 10 lessons captured per week
- **Coverage:** 80% of daily tasks automated
