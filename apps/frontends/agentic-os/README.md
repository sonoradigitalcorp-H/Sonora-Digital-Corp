# Sonora Agentic OS

Autonomous AI Dashboard with 3D Galaxy Navigation and JARVIS Voice/Text Interface.

## Features

- **6 Galaxies**: NEURA (Knowledge), CLIENTARA (Clients), AGENTARA (Agents), DEVOPSARA (Infra), CONTENTARA (Content), ECONARA (Revenue)
- **3D Navigation**: Smooth phase transitions (Macro → Galaxy → Solar System → Planet → Moon)
- **JARVIS Autonomous**: Voice commands, proactive actions, WebSocket real-time events
- **Cosmic Motion Design**: Framer Motion + GSAP + Three.js post-processing
- **Multi-tenant**: Real-time tenant monitoring, MCP management, revenue analytics

## Quick Start

```bash
# Install dependencies
cd apps/frontends/agentic-os
npm install

# Start dev server
npm run dev

# Or via opencode
opencode run agentic:dev
```

## Commands

| Command | Description |
|---------|-------------|
| `agentic:dev` | Start dev server (port 5173) |
| `agentic:build` | Production build |
| `agentic:typecheck` | TypeScript check |
| `agentic:lint` | ESLint |
| `agentic:install` | Install dependencies |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `⌘K` | Open Command Palette |
| `` ` `` | Toggle JARVIS |
| `Esc` | Close modals/palette |

## Architecture

```
src/
├── components/
│   ├── galaxy/       # GalaxyNavigator, GalaxyCore, SolarSystem, Planet, etc.
│   ├── jarvis/       # JARVISInterface, CommandPalette
│   ├── ui/           # Button, Card, Modal, Tooltip, Badge, Avatar
│   └── layout/       # Sidebar, TopBar, PhaseTransition
├── contexts/
│   ├── GalaxyContext.tsx    # Galaxy navigation state
│   ├── JARVISContext.tsx    # JARVIS autonomous loop
│   ├── TenantContext.tsx    # Multi-tenant data
│   └── MotionContext.tsx    # Performance/motion preferences
├── hooks/
│   ├── useGalaxyNavigator.ts
│   ├── useAPI.ts
│   └── useMotion.ts
├── galaxies/
│   ├── neura/        # Knowledge/Brain (Neural lattice, Engram orbits, RAG nebulae)
│   ├── clientara/    # Clients/Tenants (Star systems, service planets, MCP moons)
│   ├── agentara/     # Agent swarms (Constellations, workflow orbits)
│   ├── devopsara/    # Infrastructure (Asteroid fields, deployment rings)
│   ├── contentara/   # Content/IG (Trend nebulae, viral comets)
│   └── econara/      # Revenue (Pulsars, gravity wells, trade routes)
├── lib/
│   ├── api.ts        # REST + WebSocket client
│   └── three/        # Custom shaders, geometries, materials
└── types/            # TypeScript definitions
```

## Galaxy Navigation Phases

1. **MACRO_VIEW** - All 6 galaxies in cosmic web
2. **GALAXY_ENTER** - Wormhole transition animation
3. **SOLAR_SYSTEM** - Star (tenant) with planet (services) orbits
4. **PLANET_SURFACE** - Service detail with MCP moons
5. **MOON_DETAIL** - Individual MCP server detail

## JARVIS Capabilities

- `tenant_provisioning` - Full client onboarding
- `mcp_deployment` - Spin up MCP servers
- `campaign_creation` - End-to-end marketing campaigns
- `agent_spawning` - Create new agent skills
- `infrastructure_scaling` - K8s, Docker, serverless
- `content_generation` - IG reels, landing pages, videos
- `revenue_optimization` - $BEAT mechanics, pricing
- `knowledge_synthesis` - RAG queries, brain vault updates
- `security_auditing` - Cyber diagnosis, compliance
- `autonomous_evolution` - Self-improving code/skills

## Integration Points

- **Sonora Engine**: WebSocket `/ws/{tenant_id}` + REST `/api/v1/*`
- **OpenClaw**: File inbox → JARVIS processing
- **Voice**: `apps/voice/assistant.py` bridge
- **MCP**: `skills/mcp/` registry
- **Skills**: `skill-creator.sh` dynamic loading
- **Engram**: `memory-api.py` memory storage
- **Brain Vault**: Obsidian → Qdrant → RAG

## Development

```bash
# Type check
npm run typecheck

# Lint
npm run lint

# Build
npm run build

# Preview production build
npm run preview
```

## Deployment

```bash
# Deploy to Vercel
vercel --prod

# Or Docker
docker build -t sonora/agentic-os .
docker run -p 3000:3000 sonora/agentic-os
```