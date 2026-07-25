# Agent Harness — CRM Agent (Sales Pipeline)

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: HARNESS-CRM-001
**Status**: Live

---

## 1. Mission

Pipeline de ventas inteligente que captura leads, los califica por scoring automático, genera propuestas personalizadas, gestiona el pipeline desde lead hasta won/lost, y registra cada evento en la memoria persistente del sistema — todo sin intervención humana.

## 2. Functional Requirements

```
FR-CRM-01: Capturar leads desde Web UI, API REST, WhatsApp y Telegram
FR-CRM-02: Scoring automático por plan_interest, source, niche con threshold configurable
FR-CRM-03: Pipeline de 5 etapas: lead → qualified → proposal → negotiation → won/lost
FR-CRM-04: Generar propuestas en markdown desde catálogo de productos
FR-CRM-05: Eventos emitidos para cada transición de etapa
FR-CRM-06: Almacenar contactos en Neo4j con relación BELONGS_TO a tenant
FR-CRM-07: Persistir en Engram (layer 3, customer) para memoria cruzada
FR-CRM-08: Gamificación: XP (100) + badge "primera_venta" en deal won
FR-CRM-09: Dashboard visual del pipeline con métricas en tiempo real
FR-CRM-10: Sincronización bidireccional con SQLite CRM local
```

## 3. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CRM AGENT — SALES PIPELINE                     │
│                                                                  │
│  Channels                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐   │
│  │ Web UI   │  │ REST API │  │ WhatsApp │  │ Telegram Bot  │   │
│  │ (:5174)  │  │ (/sales) │  │ (Bridge) │  │ (Telegraf)    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬────────┘   │
│       │             │             │               │            │
│       └─────────────┼─────────────┼───────────────┘            │
│                     ▼             ▼                             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                 Sales Pipeline Engine                   │    │
│  │                                                        │    │
│  │  ┌──────────┐    ┌──────────┐    ┌───────────────┐    │    │
│  │  │ Lead     │───►│ Lead     │───►│ Proposal      │    │    │
│  │  │ Capture  │    │ Scorer   │    │ Generator     │    │    │
│  │  └──────────┘    └──────────┘    └───────┬───────┘    │    │
│  │                                           │            │    │
│  │              ┌────────────────────────────┘            │    │
│  │              ▼                                         │    │
│  │  ┌──────────────────────────────────────────────┐     │    │
│  │  │         Pipeline State Machine                │     │    │
│  │  │  lead → qualified → proposal → negotiation    │     │    │
│  │  │  → won | lost                                │     │    │
│  │  └────────────────────┬─────────────────────────┘     │    │
│  └───────────────────────┼──────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  Storage Layer                          │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │ │
│  │  │ Neo4j    │  │ Engram   │  │ SQLite   │  │ Events │ │ │
│  │  │ (Graph)  │  │ (Memory) │  │ (Local)  │  │ JSONL  │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 4. Capabilities

```
Capabilities:
- Lead Capture: Accept leads from all channels with dedup
  Events: lead_received
- Lead Scoring: Score leads by plan_interest, source, niche (threshold ≥10)
  Events: lead_scored, lead_qualified, lead_disqualified
- Proposal Generation: Generate markdown proposals from product catalog
  Events: proposal_generated, proposal_accepted
- Pipeline Management: Track deals through all 5 stages
  Events: deal_created, deal_moved, deal_won, deal_lost
- Customer Onboarding: Create customer in Neo4j + Engram on deal won
  Events: customer_onboarded
- CRM Search: Search contacts by name, phone, company with FTS
  Events: crm:search:executed
- Gamification: Award XP and badges for sales milestones
  Events: gamification:xp_awarded
- Dashboard: Real-time pipeline metrics and analytics
  Events: dashboard_updated
```

## 5. Skills

```
Skills:
- crm-client: Contact relationship management with multi-store sync
  Source: skills/crm-client.skill.md
- sales-pipeline: Full sales pipeline lifecycle
  Source: scripts/crm.py (CLI) + apps/webui/routes/sales_router.py (API)
- lead-scoring: Score leads by configured thresholds
  Source: core (embedded in SalesPipeline class)
- proposal-generator: Generate markdown proposals from catalog
  Source: core (embedded in ProposalGenerator class)
```

## 6. Policies

```
Policies:
- Every lead MUST be scored within 5 minutes of acquisition
- No proposal may be sent without a scored lead (threshold ≥10)
- Lead data MUST be stored in Neo4j + Engram + SQLite simultaneously
- Deal stage changes MUST emit events to events.jsonl
- Phone numbers MUST be stored in E.164 format without +
- Tags MUST be comma-separated, lowercase
- Contact data MUST NOT include secrets or API keys
- Gamification is best-effort (non-blocking)
- Dashboard cache refreshes every 60 seconds
```

## 7. Memory Scope

```
Memory Scope:
  Read: Layer 1 (Working), Layer 3 (Project), Layer 4 (Customer)
  Write: Layer 1 (Working), Layer 3 (Project), Layer 4 (Customer), Layer 6 (Historical)
```

## 8. Approval Requirements

```
Approval Requirements:
- lead capture: none
- lead qualify: none
- lead disqualify: notify
- proposal send: none
- deal won: none
- deal lost: notify
- discount > 20%: approve
- customer onboarding: none
```

## 9. Failure Modes

```
Failure Modes:
- Neo4j down: graph unavailable for write (queue in SQLite, sync when back)
- Engram write fail: memory persistence fails (log, continue with other stores)
- Scoring timeout: >30s to score a lead (fallback to heuristic rules)
- Duplicate lead: same phone/email captured twice (merge on crm_id)
- Proposal generation fail: product catalog unavailable (fallback text)
- SQLite full: disk space exhausted (alert, switch to in-memory)
```

## 10. Recovery Procedures

```
Recovery Procedures:
- Neo4j down: cache lead in SQLite, retry sync every 60s, emit neo4j_sync_failed event
- Engram write fail: skip memory, continue pipeline, try again on next event
- Scoring timeout: use heuristic rules (source + niche), flag for manual review
- Duplicate lead: search by phone before insert, update existing on match
- Proposal generation fail: send fallback text with link to pricing page
- SQLite full: auto-clean old archived deals (>90 days), alert ops
```

## 11. Metrics

```
Metrics:
- lead_to_deal_rate: Given qualified leads When converted Then percentage
  Target: > 20%
- pipeline_velocity: Given lead created When closed Then days
  Target: < 30d
- lead_response_time: Given lead received When scored Then minutes
  Target: < 5min
- scoring_accuracy: Given scored leads When manually reviewed Then correct rate
  Target: > 85%
- proposal_acceptance: Given proposals sent When accepted Then percentage
  Target: > 40%
- customer_onboarding_time: Given deal won When onboarded Then hours
  Target: < 24h
```

## 12. Tests

```gherkin
Feature: CRM Agent
  Scenario: Capture and qualify a new lead
    Given a new lead with name, phone, company, and plan_interest
    When the lead is captured via POST /api/sales/leads
    Then lead is stored in Neo4j with stage "lead"
    And lead_scored event fires
    And if score ≥ 10, lead transitions to "qualified"

  Scenario: Generate proposal for qualified lead
    Given a qualified lead with known product interest
    When POST /api/sales/leads/{id}/proposal is called
    Then a markdown proposal is generated
    And proposal_generated event fires
    And lead stage updates to "proposal"

  Scenario: Close won deal
    Given a lead in "proposal" or "negotiation" stage
    When POST /api/sales/leads/{id}/won is called
    Then deal stage becomes "won"
    And deal_won event fires
    And customer is onboarded in Neo4j
    And 100 XP is awarded

  Scenario: Search contacts
    Given contacts exist in CRM
    When GET /api/crm/search?q=name is called
    Then matching contacts are returned
    And crm:search:executed event fires

  Scenario: Duplicate lead detection
    Given a lead with phone "521234567890" exists
    When a new lead with same phone arrives
    Then existing lead is updated with new info
    And no duplicate is created
```

## 13. API Endpoints

```
Sales Pipeline:
  POST   /api/sales/leads                         — Capture new lead
  GET    /api/sales/leads                         — List leads (filter by stage)
  GET    /api/sales/leads/{id}                    — Get lead detail
  POST   /api/sales/leads/{id}/qualify            — Qualify lead (score)
  GET    /api/sales/leads/{id}/proposal           — Generate proposal
  POST   /api/sales/leads/{id}/accept             — Accept proposal
  POST   /api/sales/leads/{id}/won                — Close won
  POST   /api/sales/leads/{id}/lost               — Close lost
  GET    /api/sales/dashboard                     — Pipeline dashboard

CRM Contacts:
  GET    /api/crm/contacts                        — List contacts
  GET    /api/crm/contacts/{id}                   — Get contact detail
  GET    /api/crm/search?q={query}                — Search contacts
  POST   /api/crm/contacts                        — Create contact
  PUT    /api/crm/contacts/{id}                   — Update contact
  GET    /api/crm/summary                         — Contact statistics

System:
  GET    /api/enterprise-score                    — Live enterprise score
  GET    /api/enterprise-score/history            — Score history
  GET    /api/health                              — Health check
```

## 14. Configuration

```yaml
# config/sales-pipeline.yaml
sales_pipeline:
  scoring:
    threshold: 10
    weights:
      plan_interest: 5
      source_organic: 3
      source_referral: 4
      niche_match: 3
      has_website: 1
  stages:
    - lead
    - qualified
    - proposal
    - negotiation
    - won
    - lost
  proposal:
    templates_dir: "config/proposals/"
    default_catalog: "config/products.yaml"
  gamification:
    xp_on_won: 100
    badge_primera_venta: true
    badge_id: "primera_venta"
  neo4j:
    uri: "bolt://127.0.0.1:7687"
    user: "neo4j"
    database: "sdc"
  engram:
    layer: 3
    importance: 2
    tags_prefix: "crm,customer"
```

## 15. Database Schema

```
Neo4j Graph:
─────────────────────────────────────────────────
(Lead:Contact {
  crm_id: "CT-{timestamp}-{uuid}",
  name: str,
  phone: str (E.164),
  company: str,
  email: str,
  source: str,
  stage: str (lead|qualified|proposal|negotiation|won|lost),
  score: int,
  plan_interest: str,
  niche: str,
  notes: text,
  tags: str (comma-separated),
  created_at: datetime,
  updated_at: datetime
})-[BELONGS_TO]->(Tenant { id: str })

Engram (Layer 3 - Customer):
─────────────────────────────────────────────────
Key: crm:contact:{crm_id}
Value: JSON { full contact data }
Layer: 3 (customer)
Importance: 2 (high)
Tags: "crm,customer,{source}"

SQLite (Local fallback):
─────────────────────────────────────────────────
Table: contacts
  crm_id TEXT PRIMARY KEY,
  name TEXT,
  phone TEXT,
  company TEXT,
  email TEXT,
  source TEXT,
  stage TEXT,
  score INTEGER,
  plan_interest TEXT,
  niche TEXT,
  notes TEXT,
  tags TEXT,
  created_at TEXT,
  updated_at TEXT

Events (events.jsonl):
─────────────────────────────────────────────────
Event types: lead_received, lead_scored, lead_qualified,
  lead_disqualified, proposal_generated, proposal_accepted,
  deal_created, deal_won, deal_lost, customer_onboarded,
  gamification:xp_awarded, crm:contact:upserted
```

## 16. Reseller / White-Label Setup

```yaml
reseller:
  enabled: true
  markup: 30-50% over base price
  branding:
    crm_name: "Sales Pipeline"     # Configurable per tenant
    dashboard_logo: null           # Custom logo URL per reseller
  tenant_config:
    - tenant_id: "{reseller_slug}"
      scoring_threshold: 10          # Configurable per tenant
      custom_stages: []              # Custom pipeline stages
      proposal_templates_dir: "config/proposals/{tenant}/"
      products_catalog: "config/products/{tenant}.yaml"
  features:
    white_label_domain: true
    custom_proposal_templates: true
    custom_scoring_weights: true
    custom_pipeline_stages: true
    custom_gamification: true
    analytics_dashboard: true
  setup_steps:
    1. Create tenant in config/tenants.json
    2. Set scoring threshold and weights per tenant
    3. Upload proposal templates to config/proposals/{tenant}/
    4. Upload product catalog to config/products/{tenant}.yaml
    5. Configure Neo4j database per tenant (or shared with label)
    6. Test with sample lead through full pipeline
```

## 17. Pricing

```
Base License:   $99/license/month
Includes:       Up to 200 leads/month, all pipeline stages, dashboard
Overages:       $0.25/lead after 200

Reseller Tiers:
  Starter:      $99/mo — up to 500 leads, 1 tenant
  Professional: $299/mo — up to 2,500 leads, 5 tenants
  Enterprise:   $999/mo — unlimited leads, unlimited tenants, white-label

Add-ons:
  WhatsApp Integration:   $49/mo (lead capture from WhatsApp)
  Telegram Integration:   $29/mo (lead capture from Telegram)
  Custom Scoring Model:   $199 one-time (train custom ML scoring)
  API Access:             included in all tiers
  CSV Export:             included in all tiers
```

## 18. Setup Steps

```bash
# 1. Ensure infrastructure is running
docker compose -f infra/docker-compose.yml up -d sdc-neo4j sdc-postgres sdc-redis

# 2. Verify Neo4j is healthy
curl http://127.0.0.1:7687  # Should respond to bolt

# 3. Initialize database schema
python -c "from src.core.neo4j_store import init_store; init_store()"

# 4. Test CRM CLI
python scripts/crm.py contacts
python scripts/crm.py summary

# 5. Start Web UI (includes sales pipeline routes)
docker compose -f infra/docker-compose.yml up -d sdc-jarvis-webui

# 6. Verify API
curl http://127.0.0.1:5174/api/health
curl http://127.0.0.1:5174/api/sales/dashboard

# 7. Create a test lead
curl -X POST http://127.0.0.1:5174/api/sales/leads \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Lead", "phone": "521234567890", "company": "Test Corp", "plan_interest": "agent_ia"}'
```

## 19. Testing Instructions

```bash
# Unit tests for CRM client
pytest tests/clients/test_crm.py -v

# Gherkin test for manage-crm
pytest tests/gherkin/test_manage_crm.py -v

# Integration tests
pytest tests/integration/test_sales_pipeline.py -v

# Test CLI
python scripts/crm.py contacts
python scripts/crm.py search --q "Test"
python scripts/crm.py summary

# Test API with curl
# Capture lead
curl -s -X POST http://127.0.0.1:5174/api/sales/leads \
  -H "Content-Type: application/json" \
  -d '{"name": "Demo", "phone": "521111111111", "company": "Demo Inc", "plan_interest": "cyber_security"}' | jq .

# List leads
curl -s http://127.0.0.1:5174/api/sales/leads | jq .

# Test proposal generation
LEAD_ID=$(curl -s http://127.0.0.1:5174/api/sales/leads | jq -r '.leads[0].id')
curl -s http://127.0.0.1:5174/api/sales/leads/$LEAD_ID/proposal | jq .

# Load test
python scripts/load-test-crm.py --leads 100 --concurrent 10

# Neo4j query test
python -c "
from src.core.neo4j_store import search_contacts
results = search_contacts(query='Demo')
print(f'Found {len(results)} contacts')
"
```

## 20. Observability

```
Observability:
- Health endpoint: GET /api/health
- Dashboard: GET /api/sales/dashboard
- Metrics: lead_to_deal_rate, pipeline_velocity, lead_response_time
- Events: state/events/events.jsonl (all pipeline transitions)
- Logs: state/logs/harnesses/crm-harness.log
- Log level: INFO
- Tracing: via MCP Gateway (when LangFuse available)
```

## 21. Dependencies

```
Dependencies:
- Neo4j: service (port 7687, primary graph store)
- Engram MCP: service (memory persistence layer 3)
- SQLite3: stdlib (local fallback CRM store)
- FastAPI: HTTP server (Web UI routes)
- Qdrant: service (port 6333, optional vector search)
- Events file: state/events/events.jsonl
- httpx: async HTTP for Neo4j/Qdrant sync
```

## Validation Checklist

- [x] Mission is one sentence, measurable
- [x] All FRs are numbered and testable
- [x] Architecture diagram describes data flow
- [x] All capabilities map to events
- [x] DB schema defined (Neo4j + Engram + SQLite + Events)
- [x] API endpoints fully documented (13 endpoints)
- [x] All failure modes have recovery procedures
- [x] Reseller/white-label configuration documented
- [x] Pricing defined with tiers
- [x] Setup steps are executable
- [x] Tests cover happy path, edge cases, and failure modes
- [x] Observability endpoints defined
