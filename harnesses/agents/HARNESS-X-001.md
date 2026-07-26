# Agent Harness — X Agent (Social Media Automation)

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: HARNESS-X-001
**Status**: Coming Soon

---

> **⚠️ COMING SOON — Especificación del agente a construir**
>
> Este harness describe el agente X Agent que será implementado en el próximo sprint.
> No existe código aún. Todo está por construir.
> Fecha objetivo: Q3 2026

---

## 1. Mission

Automatización completa de redes sociales: análisis de tendencias, generación de contenido, programación inteligente de publicaciones, y analytics cross-platform — para que la empresa mantenga presencia activa en X (Twitter), LinkedIn, Instagram y TikTok sin intervención humana.

## 2. Functional Requirements (Propuesta)

```
FR-X-01: Conectar y autenticar con APIs de X/Twitter, LinkedIn, Instagram, TikTok
FR-X-02: Analizar tendencias del nicho cada 6h y generar reporte
FR-X-03: Generar contenido textual con tono configurable por plataforma
FR-X-04: Generar imágenes/video corto con DALL·E / Stable Diffusion
FR-X-05: Programar publicaciones con calendario inteligente (mejor horario)
FR-X-06: Publicar automáticamente en hora programada (con aprobación opcional)
FR-X-07: Colectar analytics (impresiones, engagement, clicks, seguidores)
FR-X-08: Responder automáticamente a menciones y DMs con flujo configurable
FR-X-09: A/B testing de headlines y formatos
FR-X-10: Cross-posting con adaptación de formato por plataforma
FR-X-11: Memoria de contenido publicado (evitar repetición)
FR-X-12: Reporte semanal de performance con recomendaciones
```

## 3. Architecture (Propuesta)

```
┌─────────────────────────────────────────────────────────────────┐
│                    X AGENT — SOCIAL MEDIA ENGINE                  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Content Engine                        │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │    │
│  │  │ Trend        │  │ Content      │  │ Media        │  │    │
│  │  │ Analyzer     │─►│ Generator    │─►│ Generator    │  │    │
│  │  │ (6h cron)    │  │ (LLM)        │  │ (DALL·E/SD)  │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │    │
│  └──────────────────────────┬──────────────────────────────┘    │
│                             │ content                          │
│                             ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Scheduler Engine                      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │    │
│  │  │ Calendar     │  │ Queue        │  │ Publisher    │  │    │
│  │  │ (best time)  │─►│ (approval?)  │─►│ (API calls)  │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │    │
│  └──────────────────────────┬──────────────────────────────┘    │
│                             │ posts                            │
│                             ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Platform Connectors                   │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │    │
│  │  │ X/Twitter│  │ LinkedIn │  │ Instagram│  │ TikTok │  │    │
│  │  │ API v2   │  │ API      │  │ Graph API│  │ API    │  │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘  │    │
│  └──────────────────────────┬──────────────────────────────┘    │
│                             │ data                             │
│                             ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Analytics Engine                      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │    │
│  │  │ Collect      │  │ Report       │  │ Recommend    │  │    │
│  │  │ (daily cron) │─►│ Generator    │─►│ Engine       │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    MCP Gateway                           │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │    │
│  │  │ Engram   │  │ Neo4j    │  │ Qdrant   │  │ Events │  │    │
│  │  │ (memory) │  │ (graph)  │  │ (RAG)    │  │ JSONL  │  │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 4. Capabilities (Propuesta)

```
Capabilities:
- Trend Analysis: Monitor and analyze niche trends every 6h
  Events: trend_analysis_completed
- Content Generation: Generate text and media for all platforms
  Events: content_generated
- Smart Scheduling: Schedule posts at optimal times per platform
  Events: post_scheduled
- Auto Publishing: Publish content automatically or with approval
  Events: post_published, post_approved, post_rejected
- Social Listening: Monitor mentions, DMs, and brand keywords
  Events: mention_received, dm_received
- Auto Response: Respond to mentions and DMs with configurable flows
  Events: auto_response_sent
- Analytics: Collect and report cross-platform performance
  Events: analytics_collected, weekly_report_generated
- A/B Testing: Test headlines and formats for engagement
  Events: ab_test_started, ab_test_completed
- Cross-Posting: Adapt and post content across platforms
  Events: cross_post_completed
```

## 5. Skills (Propuesta)

```
Skills:
- x-connector: X/Twitter API v2 integration (tweets, search, stream)
  Source: skills/x-connector.skill.md [TODO]
- linkedin-connector: LinkedIn API integration (posts, analytics)
  Source: skills/linkedin-connector.skill.md [TODO]
- instagram-connector: Instagram Graph API integration
  Source: skills/instagram-connector.skill.md [TODO]
- tiktok-connector: TikTok API integration
  Source: skills/tiktok-connector.skill.md [TODO]
- content-generator: LLM-powered content generation per platform
  Source: skills/content-generator.skill.md [TODO]
- media-generator: DALL·E / Stable Diffusion image generation
  Source: skills/media-generator.skill.md [TODO]
- social-scheduler: Smart scheduling with best-time algorithm
  Source: skills/social-scheduler.skill.md [TODO]
- social-analytics: Cross-platform analytics and reporting
  Source: skills/social-analytics.skill.md [TODO]
```

## 6. Policies (Propuesta)

```
Policies:
- Every post MUST be generated first, then scheduled (never direct publish)
- Auto-publish only for approved content categories (configurable)
- Mentions with negative sentiment MUST be flagged for human review
- No content may be published outside business hours unless scheduled
- Rate limits per platform MUST be respected (queue if needed)
- All published content MUST be stored in Engram for memory
- Analytics data MUST persist for minimum 90 days
- A/B tests require minimum 500 impressions per variant
- Weekly report MUST be generated every Monday 08:00
```

## 7. Memory Scope (Propuesta)

```
Memory Scope:
  Read: Layer 1 (Working), Layer 2 (Task), Layer 3 (Project), Layer 5 (Business)
  Write: Layer 1 (Working), Layer 2 (Task), Layer 6 (Historical)
```

## 8. Approval Requirements (Propuesta)

```
Approval Requirements:
- content generation: none
- content scheduling: none
- auto-publish (tier 1 - informational): none
- auto-publish (tier 2 - promotional): approve
- auto-publish (tier 3 - sales/critical): approve + notify
- auto-response to mentions: none (for positive/neutral)
- auto-response to negative sentiment: notify
- A/B test start: none
- weekly report send: none
```

## 9. Failure Modes (Propuesta)

```
Failure Modes:
- API rate limit: platform API returns 429 (backoff, queue)
- API auth failure: token expired or revoked (alert, retry with refresh)
- Content generation fail: LLM timeout or quality low (regenerate with stricter params)
- Media generation fail: DALL·E/SD timeout (fallback to text-only post)
- Scheduler miss: cron task fails to trigger (manual trigger, alert)
- Platform outage: API completely down (skip platform, continue others)
- Duplicate content: same post generated twice (dedup by hash in Engram)
```

## 10. Recovery Procedures (Propuesta)

```
Recovery Procedures:
- API rate limit: exponential backoff, max 3 retries, queue remaining
- API auth failure: attempt token refresh, if fail → alert ops, disable connector
- Content generation fail: regenerate with lower temperature, max 2 attempts
- Media generation fail: post text-only with "image coming soon" note
- Scheduler miss: manual trigger via API, alert, fix cron expression
- Platform outage: skip in analytics, resume when health check passes
- Duplicate content: skip post, log, update dedup hash in Engram
```

## 11. Metrics (Propuesta)

```
Metrics:
- engagement_rate: Given posts When published per week Then avg engagement
  Target: > 3%
- follower_growth: Given weekly period When measured Then growth %
  Target: > 5%/month
- content_velocity: Given content queue When published Then posts/day
  Target: 3-5 posts/day per platform
- auto_response_rate: Given mentions received When auto-responded Then %
  Target: > 80%
- trend_accuracy: Given trends detected When manually reviewed Then accuracy
  Target: > 70%
- weekly_report_latency: Given Monday 08:00 When report delivered Then delay
  Target: < 5min
```

## 12. Tests (Propuesta)

```gherkin
Feature: X Agent
  Scenario: Generate and schedule content
    Given a content calendar with slots available
    When trend analysis completes
    Then content is generated for all platforms
    And content is scheduled at optimal times
    And content_generated event fires

  Scenario: Publish approved content
    Given a scheduled post with approval tier "none"
    When publish time arrives
    Then post is published to target platform
    And post_published event fires

  Scenario: Respond to mention
    Given a mention with positive sentiment
    When auto-response flow matches
    Then auto-response is sent within 5 minutes
    And auto_response_sent event fires

  Scenario: Generate weekly report
    Given analytics data for past 7 days
    When Monday 08:00 cron triggers
    Then weekly report is generated
    And weekly_report_generated event fires
    And report is sent to configured channels
```

## 13. API Endpoints (Propuesta)

```
Content:
  GET    /api/x/trends                — Current trend analysis
  POST   /api/x/content/generate      — Generate content for a topic
  GET    /api/x/content/queue         — Content queue status
  POST   /api/x/content/schedule      — Schedule content

Publishing:
  GET    /api/x/posts                 — List published posts
  GET    /api/x/posts/{id}            — Post detail and performance
  POST   /api/x/posts/{id}/publish    — Publish a scheduled post
  POST   /api/x/posts/{id}/approve    — Approve post
  POST   /api/x/posts/{id}/reject     — Reject post

Social Listening:
  GET    /api/x/mentions              — Recent mentions
  POST   /api/x/mentions/{id}/respond — Respond to mention

Analytics:
  GET    /api/x/analytics/overview    — Cross-platform summary
  GET    /api/x/analytics/platform/{id} — Per-platform breakdown
  GET    /api/x/analytics/report/weekly — Latest weekly report

System:
  GET    /api/x/health                — Health check
  GET    /api/x/platforms             — Connected platforms status
```

## 14. Configuration (Propuesta)

```yaml
# config/x-agent.yaml
x_agent:
  platforms:
    twitter:
      enabled: true
      api_key: "${TWITTER_API_KEY}"
      api_secret: "${TWITTER_API_SECRET}"
      bearer_token: "${TWITTER_BEARER_TOKEN}"
      rate_limit: 300  # tweets per 15 min
    linkedin:
      enabled: false
      access_token: "${LINKEDIN_TOKEN}"
    instagram:
      enabled: false
      access_token: "${INSTAGRAM_TOKEN}"
    tiktok:
      enabled: false
      access_token: "${TIKTOK_TOKEN}"
  content:
    tone: "professional"  # professional | casual | humorous | inspirational
    languages: ["es", "en"]
    max_length_per_platform:
      twitter: 280
      linkedin: 3000
      instagram: 2200
      tiktok: 2200
    media:
      provider: "dalle"  # dalle | stability-ai
      model: "dall-e-3"
      size: "1024x1024"
  scheduling:
    best_time_algorithm: true
    default_hours: [08:00, 12:00, 18:00]
    timezone: "America/Mexico_City"
    max_posts_per_day:
      twitter: 5
      linkedin: 2
      instagram: 2
      tiktok: 3
  analytics:
    collect_interval_hours: 24
    report_day: "Monday"
    report_time: "08:00"
    retention_days: 90
  auto_response:
    enabled: false
    sentiment_threshold: 0.5  # positive/neutral only
    templates_dir: "config/x-agent/responses/"
```

## 15. Database Schema (Propuesta)

```
Engram (Layer 3 - Project):
─────────────────────────────────────────────────
Key: x:post:{post_id}
Value: JSON { platform, content, media_url, status, scheduled_at, published_at }
Layer: 3 (project)
Importance: 1 (medium)
Tags: "x-agent,{platform},post"

Key: x:trend:{date}
Value: JSON { trends, topics, recommendations }
Layer: 2 (task)
Importance: 2 (high)
Tags: "x-agent,trends"

Key: x:analytics:{platform}:{date}
Value: JSON { impressions, engagement, clicks, followers }
Layer: 5 (business)
Importance: 2 (high)
Tags: "x-agent,analytics,{platform}"

Neo4j Graph:
─────────────────────────────────────────────────
(Post { id, platform, content_hash, status, published_at })
-[POSTED_ON]->(Platform { name, handle })
-[MENTIONS]->(Topic { name, category })
```

## 16. Reseller / White-Label Setup (Propuesta)

```yaml
reseller:
  enabled: true
  markup: 30-50% over base price
  branding:
    agent_name: "Social Engine"  # Configurable per tenant
  tenant_config:
    - tenant_id: "{reseller_slug}"
      platforms: ["twitter", "linkedin"]
      content_tone: "professional"
      auto_approve: false
  features:
    white_label_domain: true
    custom_tone: true
    custom_content_templates: true
    custom_platforms: true
    analytics_dashboard: true
  setup_steps:
    1. Register platform API credentials per tenant
    2. Configure content tone and brand voice
    3. Set approval workflow (none / notify / approve)
    4. Configure posting schedule
    5. Deploy with env vars for API tokens
    6. Test with sample content generation
```

## 17. Pricing (Propuesta)

```
Base License:   $79/license/month
Includes:       Up to 3 platforms, 30 posts/month, trend analysis
Overages:       $1/post after 30

Reseller Tiers:
  Starter:      $79/mo — 1 platform, 30 posts/month
  Professional: $249/mo — 3 platforms, 150 posts/month, auto-response
  Enterprise:   $799/mo — unlimited platforms, unlimited posts, white-label

Add-ons:
  Additional Platform:   $29/mo each
  AI Media Generation:   $49/mo (DALL·E / Stable Diffusion)
  Social Listening:      $99/mo (mention monitoring + auto-response)
  Custom Analytics:      $149/mo (custom dashboards + export)
  API Access:            included in Professional+
```

## 18. Setup Steps (Propuesta)

```bash
# 1. Create directory structure
mkdir -p apps/x-agent/
mkdir -p config/x-agent/responses/

# 2. Install dependencies
pip install tweepy requests python-dotenv schedule Pillow

# 3. Set environment variables
export TWITTER_API_KEY="..."
export TWITTER_API_SECRET="..."
export TWITTER_BEARER_TOKEN="..."
export X_AGENT_PORT=9100

# 4. Initialize database
python -m apps.x-agent.init_db

# 5. Start agent
python -m apps.x-agent.main

# 6. Verify health
curl http://127.0.0.1:9100/api/x/health

# 7. Configure platforms
curl -X POST http://127.0.0.1:9100/api/x/platforms \
  -H "Content-Type: application/json" \
  -d '{"platform": "twitter", "enabled": true}'
```

## 19. Testing Instructions (Propuesta)

```bash
# Unit tests
pytest apps/x-agent/tests/ -v

# Test trend analysis
python -c "
from apps.x_agent.trend_analyzer import TrendAnalyzer
ta = TrendAnalyzer()
trends = ta.analyze('technology')
print(f'Found {len(trends)} trends')
"

# Test content generation
python -c "
from apps.x_agent.content_generator import ContentGenerator
cg = ContentGenerator()
post = cg.generate('AI trends 2026', platform='twitter')
print(f'Generated: {post[:100]}...')
"

# Test platform connector
python -c "
from apps.x_agent.connectors.twitter import TwitterConnector
tc = TwitterConnector()
health = tc.health()
print(f'Twitter API: {health}')
"

# Integration test: full content pipeline
pytest tests/integration/test_x_agent_pipeline.py -v

# Load test: 100 concurrent post generations
python scripts/load-test-x-agent.py --posts 100
```

## 20. Observability (Propuesta)

```
Observability:
- Health endpoint: GET /api/x/health
- Platform status: GET /api/x/platforms
- Metrics: engagement_rate, follower_growth, content_velocity, auto_response_rate
- Events: state/events/events.jsonl
- Logs: state/logs/harnesses/x-agent-harness.log
- Log level: INFO
- Tracing: via MCP Gateway (when LangFuse available)
- Alerts: platform auth failure, rate limit near max, content generation failure
```

## 21. Dependencies (Propuesta)

```
Dependencies:
- MCP Gateway: service (Engram, Neo4j, Qdrant, Events)
- Twitter API v2: external (tweepy)
- LinkedIn API: external (requests)
- Instagram Graph API: external
- TikTok API: external
- OpenAI/DALL·E: external (media generation)
- Stable Diffusion: external or local (media generation)
- schedule: Python lib (cron jobs)
- Engram MCP: service (memory for posted content dedup)
```

## 22. Implementation Roadmap

```
Sprint 1 (Foundation):
  - Project scaffolding + directory structure
  - Twitter connector (auth, post, search, stream)
  - Health endpoint + basic config

Sprint 2 (Content Engine):
  - Trend analyzer (6h cron)
  - Content generator (LLM-based, per platform)
  - Media generator (DALL·E integration)

Sprint 3 (Scheduler + Publisher):
  - Smart calendar (best-time algorithm)
  - Post queue + approval workflow
  - Publisher with rate limit handling

Sprint 4 (Analytics + Social Listening):
  - Cross-platform analytics collector
  - Weekly report generator
  - Mention monitoring + auto-response

Sprint 5 (Polish + Scale):
  - LinkedIn, Instagram, TikTok connectors
  - A/B testing engine
  - Cross-posting with adaptation
  - Reseller/white-label config
  - Load testing + documentation
```

## Validation Checklist

- [x] Mission is one sentence, measurable
- [x] All FRs are numbered and testable
- [x] Architecture diagram describes data flow
- [x] All capabilities map to events
- [x] DB schema defined (Engram + Neo4j)
- [x] API endpoints documented
- [x] All failure modes have recovery procedures
- [x] Reseller/white-label configuration documented
- [x] Pricing defined with tiers
- [x] Setup steps outlined
- [x] Implementation roadmap defined
- [x] Observability endpoints defined
- [ ] **[ ] No code exists yet — Coming Soon**
