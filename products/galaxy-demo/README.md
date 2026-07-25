# Agent Galaxy — Aztro Tech Demo Package

> **⚠️ PREVIEW MODE** — This is a demo package for client presentations. Not production-ready.

## What This Is

A complete demo package for presenting **Agent Galaxy** to **Aztro Tech** — a potential client wanting to buy AI agents for their own customers.

Agent Galaxy is a multi-tenant platform where each "planet" is an autonomous AI agent with specific capabilities. The demo showcases the full system: agents, voice, onboarding, pricing, and multi-tenant architecture.

## Quick Start

```bash
# 1. Navigate to the demo directory
cd products/galaxy-demo/

# 2. Open the presentation in a browser
open presentation.html        # macOS
xdg-open presentation.html    # Linux
start presentation.html       # Windows

# 3. Follow the DEMO-SCRIPT.md for the 15-minute presentation
```

## Package Contents

```
galaxy-demo/
├── DEMO-SCRIPT.md          # Step-by-step presentation script (15 min)
├── demo-config.json        # Demo configuration with pre-loaded tenant & sample data
├── presentation.html       # Single-page HTML presentation (dark galaxy theme)
├── openclaw-config.json    # OpenClaw agent config for the demo
├── hermes-config.json      # Hermes bridge config (multi-channel + voice)
├── README.md               # This file
└── evals/
    └── promptfoo.yaml      # Evaluation config for testing LLM, STT/TTS, onboarding
```

## File Descriptions

### DEMO-SCRIPT.md
Complete 15-minute presentation script with timestamps:
- **0:00** — Opening + Galaxy visualization
- **1:00** — Galaxy overview (6 agents/planets)
- **3:00** — Agent deep dive (Sales Agent example)
- **6:00** — 30-second onboarding demo
- **8:00** — Voice demo (STT → LLM → TTS via WhatsApp)
- **10:00** — Multi-tenant architecture
- **12:00** — Pricing plans (Explorador, Conquistador, Imperio)
- **14:00** — Closing + Call to Action

### demo-config.json
Pre-loaded demo configuration:
- Tenant: `aztro-tech-demo` (all capabilities enabled)
- LLM: DeepSeek V4 Flash (primary) + OpenRouter fallback
- Demo mode: cached responses, no real API calls
- Sample data for all 6 agents with realistic metrics
- Pricing tiers: Explorador ($297), Conquistador ($797), Imperio ($1,997)
- Channel configs: WhatsApp, Telegram, Web

### presentation.html
Single-page dark-themed HTML presentation:
- Animated starfield background
- Embedded 3D galaxy visualization (iframe)
- Agent cards with live metrics
- Onboarding flow visualization
- Pricing table with feature comparison
- Tech stack badges
- CTA section with WhatsApp + Email links

### openclaw-config.json
OpenClaw agent configuration:
- Primary LLM: DeepSeek V4 Flash via OpenCode Go
- Fallback: OpenRouter free tier (Llama 3.1 8B)
- Event handlers for onboarding, leads, proposals, voice
- Task routing rules per agent type
- Skills activation per tenant
- Observability and alerting config

### hermes-config.json
Hermes multi-channel bridge configuration:
- WhatsApp Business API (text + voice)
- Telegram Bot API (text)
- Web chat (text + voice)
- Voice pipeline: STT → LLM → TTS (full flow)
- Multi-tenant resolution
- Health checks and metrics

### evals/promptfoo.yaml
promptfoo evaluation configuration:
- LLM quality tests (sales, support, code generation)
- Primary vs fallback model comparison
- STT transcription accuracy
- TTS naturalness checks
- Onboarding flow simulation
- Quality thresholds defined for each metric

## How to Present

### Before the Demo
1. Open `presentation.html` in a browser (Chrome recommended)
2. Verify the 3D galaxy loads correctly
3. Review `DEMO-SCRIPT.md` — memorize the flow, don't read it
4. Have WhatsApp open on your phone for the voice demo
5. Test all links and CTAs

### During the Demo
1. Follow the script timestamps — keep it to 15 minutes
2. Let the visuals do the talking — don't over-explain
3. Emphasize **30-second onboarding** — this is the wow moment
4. Show real metrics from `demo-config.json` sample data
5. Close with the pilot offer — 30 days, no commitment

### After the Demo
1. Send follow-up email within 2 hours
2. Share the demo link
3. Log interaction in Engram (memory layer: customer)
4. Create tenant `aztro-tech-pilot` if approved

## Configuration Guide

### API Keys (Demo Mode)
In preview mode, no real API calls are made. All responses are cached/simulated.

For a live demo with real API calls:
1. Set `OPENCODE_GO_API_KEY` environment variable
2. Set `OPENROUTER_API_KEY` environment variable (fallback)
3. Update `demo-config.json`: set `demo_mode.enabled` to `false`
4. Configure WhatsApp Business API credentials in `hermes-config.json`

### Customizing for Other Clients
To adapt this demo for a different client:

1. Update tenant ID in all config files
2. Replace "Aztro Tech" branding in `presentation.html`
3. Adjust pricing if needed in `demo-config.json` and `presentation.html`
4. Update channel numbers/tokens in `hermes-config.json`
5. Modify sample data to match client's industry

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Primary LLM | DeepSeek V4 Flash |
| Fallback LLM | Meta Llama 3.1 8B (via OpenRouter, free tier) |
| API Provider | OpenCode Go |
| Agent Framework | OpenClaw |
| MCP Bridge | Hermes |
| STT | Whisper-compatible |
| TTS | Edge TTS |
| Channels | WhatsApp, Telegram, Web |
| Database | PostgreSQL, Neo4j, Qdrant, Redis |
| Infra | Docker |

## Pricing Plans

| Feature | Explorador | Conquistador | Imperio |
|---------|-----------|--------------|---------|
| Price | $297/mo | $797/mo | $1,997/mo |
| Agents | 1 | 3 | 6+ |
| Channels | 1 | 2 | All |
| Skills | 3 | 8 | All |
| Voice | ❌ | ✅ | ✅ |
| Custom LLM | ❌ | ❌ | ✅ |
| SLA | 95% | 99% | 99.9% |
| Support | Email | Chat + Email | Dedicated |

## Next Steps

### Immediate
- [ ] Present demo to Aztro Tech
- [ ] Collect feedback
- [ ] Adjust pricing/features based on feedback

### If Pilot Approved
- [ ] Create production tenant `aztro-tech-pilot`
- [ ] Configure real API keys
- [ ] Set up WhatsApp Business API
- [ ] Deploy to VPS
- [ ] 30-day pilot with weekly check-ins

### If Not Ready
- [ ] Schedule follow-up in 2 weeks
- [ ] Share recorded demo
- [ ] Address specific concerns
- [ ] Adjust proposal based on objections

## Known Limitations (Preview Mode)

- 3D galaxy iframe requires `../galaxy-3d/index.html` to exist
- Voice demo uses simulated responses (no real STT/TTS)
- WhatsApp number is placeholder (replace with real number)
- Metrics are sample data, not live
- No real API calls are made in demo mode
- Tenant expiration: 2026-08-23 (30-day demo window)

## Contact

- **Sonora Digital Corp**: partners@sonoradigitalcorp.com
- **WhatsApp**: +52-XXX-XXX-XXXX (replace with real number)
- **GitHub**: github.com/sonoradigitalcorp-H/Sonora-Digital-Corp

---

*Demo package v1.0 | Created: 2026-07-23 | Mode: PREVIEW*
