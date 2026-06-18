# Sub-OS MANIFEST — Sonora Digital Corp

**Version**: 1.0.0
**Constitution**: `OMEGA-PROMPT-v10.0.md`
**Soul**: `SOUL.md`
**Total Sub-OS**: 10

---

## Inheritance Chain

```
OMEGA PROMPT v10.0 (root constitution)
    └── SOUL.md (meta-soul, inherited by all)
        └── Each Sub-OS prompt inherits both
            └── Each Agent inherits its OS prompt
                └── Each Skill references its parent OS
```

---

## Sub-OS Catalog

| # | OS | Domain | Capabilities | Events | Dependencies |
|---|----|--------|-------------|--------|-------------|
| 1 | Sales | Go-to-market | Lead gen, qualification, proposals, pipeline | `lead_received`, `lead_qualified`, `proposal_generated`, `contract_signed` | Knowledge (contacts→memory), Finance (deals→revenue) |
| 2 | Dev | Software delivery | CI/CD, architecture, code review, deployments | `deployment_started`, `deployment_completed`, `build_failed`, `deploy_failed` | Quality (tests must pass), Knowledge (ADRs) |
| 3 | Support | Client care | Tickets, SLAs, escalations, satisfaction | `ticket_created`, `ticket_escalated`, `ticket_resolved`, `satisfaction_recorded` | Knowledge (solutions→playbooks), Ops (infra) |
| 4 | Agent | Agent lifecycle | MCP governance, skill registry, harness mgmt | `agent_spawned`, `agent_failed`, `harness_updated`, `skill_registered` | ALL (harness for every OS) |
| 5 | Knowledge | Memory & docs | 7-layer memory, ADRs, knowledge capture | `knowledge_stored`, `adr_created`, `memory_pruned`, `knowledge_retrieved` | ALL (feeds every OS) |
| 6 | Finance | FinOps & revenue | Cost tracking, billing, revenue, ROI | `payment_received`, `cost_recorded`, `invoice_generated`, `roi_calculated` | Sales (deals→revenue), Ops (infra costs) |
| 7 | Security | Trust & compliance | Secrets mgmt, audit, incident response | `security_alert`, `audit_triggered`, `incident_detected`, `access_revoked` | Ops (infra security), ALL (compliance) |
| 8 | Ops | Infrastructure | Deployments, monitoring, recovery, scaling | `server_down`, `container_crashed`, `disk_full`, `service_recovered` | ALL (infra for all) |
| 9 | Quality | Testing & evaluation | Test frameworks, process audits, evaluations | `test_failed`, `audit_completed`, `evaluation_done`, `score_updated` | Dev (tests), Strategy (score) |
| 10 | Strategy | Direction & growth | Roadmap, initiatives, enterprise score, entropy | `initiative_created`, `score_updated`, `quarter_started`, `initiative_killed` | ALL (evaluates all OS) |

---

## Event Flow Between OS

```
Sales ──contract_signed──→ Finance ──payment_received──→ Knowledge
  │                          │
  │                          └──cost_recorded──→ Strategy
  │
  └──lead_qualified──→ Support ──ticket_created──→ Ops ──server_down──→ Security
                           │                        │                    │
                           └──ticket_resolved──→ Knowledge              └──incident_detected──→ Quality
                                                                            │
                                                                            └──audit_completed──→ Strategy
```

---

## Skills Catalog

| # | OS | Skill | ID | Version |
|---|----|-------|----|---------|
| 1 | Sales | qualify-lead | SKILL-SLS-001 | 1.0.0 |
| 2 | Dev | deploy-code | SKILL-DEV-001 | 1.0.0 |
| 3 | Support | resolve-ticket | SKILL-SUP-001 | 1.0.0 |
| 4 | Agent | spawn-agent | SKILL-AGT-001 | 1.0.0 |
| 5 | Knowledge | capture-knowledge | SKILL-CK-001 | 1.0.0 |
| 6 | Finance | track-finance | SKILL-FIN-001 | 1.0.0 |
| 7 | Security | audit-security | SKILL-SEC-001 | 1.0.0 |
| 8 | Ops | monitor-service | SKILL-MS-001 | 1.0.0 |
| 9 | Quality | validate-quality | SKILL-QTY-001 | 1.0.0 |
| 10 | Strategy | plan-strategy | SKILL-STR-001 | 1.0.0 |

## Harnesses Catalog

| # | OS | Harness | ID | Status |
|---|----|---------|----|--------|
| 1 | Sales | sales-harness | HARNESS-SLS-001 | Active |
| 2 | Dev | dev-harness | HARNESS-DEV-001 | Active |
| 3 | Support | support-harness | HARNESS-SUP-001 | Active |
| 4 | Agent | agent-harness | HARNESS-AGT-001 | Active |
| 5 | Knowledge | knowledge-harness | HARNESS-KNW-001 | Active |
| 6 | Finance | finance-harness | HARNESS-FIN-001 | Active |
| 7 | Security | security-harness | HARNESS-SEC-001 | Active |
| 8 | Ops | ops-harness | HARNESS-OPS-001 | Active |
| 9 | Quality | quality-harness | HARNESS-QTY-001 | Active |
| 10 | Strategy | strategy-harness | HARNESS-STR-001 | Active |

## Initiatives Catalog

| # | Initiative | OS | Score | Status |
|---|-----------|----|-------|--------|
| 1 | improve-automation-coverage | Ops | 64/100 | Active |
| 2 | finops-baseline | Finance | 67/100 | Active |
| 3 | knowledge-immortality | Knowledge | 71/100 | Active |

## Enterprise Score Contribution

| OS | Metrics Contributed to Score |
|----|------------------------------|
| Sales | Revenue Impact, Scalability |
| Dev | Reusability, Reliability |
| Support | Customer Value |
| Agent | Automation Impact, Scalability |
| Knowledge | Knowledge Impact |
| Finance | Revenue Impact, FinOps Efficiency |
| Security | Reliability |
| Ops | Operational Simplicity |
| Quality | Reliability |
| Strategy | Founder Independence |
