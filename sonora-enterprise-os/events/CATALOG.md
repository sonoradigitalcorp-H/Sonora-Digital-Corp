# Enterprise Event Catalog — Sonora Digital Corp

**Version**: 1.0.0
**Audit ID**: EVENTS-CATALOG-001

---

All business activity originates from events. Every event is owned by a sub-OS and may be consumed by others.

---

## Sales OS Events

| Event | Trigger | Producer | Consumers | Payload |
|-------|---------|----------|-----------|---------|
| `lead_received` | Contact form submission | Sales OS | Sales OS, Knowledge OS | `{source, contact, timestamp}` |
| `lead_qualified` | Lead score > threshold | Sales OS | Sales OS, Sales OS | `{lead_id, score, intent}` |
| `proposal_generated` | Proposal created from qualified lead | Sales OS | Sales OS, Knowledge OS | `{lead_id, proposal_id, value}` |
| `lead_generated_from_data` | High-value artist detected during data sync | Data OS (Scrapers) | Sales OS, Knowledge OS | `{artist_id, artist_name, streams, followers}` |
| `data_sync_completed` | Live data pipeline sync cycle finished | Data OS (Scrapers) | Knowledge OS, Strategy OS | `{artists_synced, total_artists}` |
| `contract_signed` | Client accepts terms | Sales OS | Finance OS, Knowledge OS | `{deal_id, value, terms}` |
| `deal_stage_changed` | Deal moves to next pipeline stage | Sales OS | Sales OS, Strategy OS | `{deal_id, from_stage, to_stage}` |

## Dev OS Events

| Event | Trigger | Producer | Consumers | Payload |
|-------|---------|----------|-----------|---------|
| `feature_implemented` | Code written for spec | Dev OS | Dev OS, Quality OS | `{feature_id, branch, author}` |
| `build_passed` | CI pipeline succeeds | Dev OS | Dev OS, Ops OS | `{build_id, commit, tests}` |
| `build_failed` | CI pipeline fails | Dev OS | Dev OS, Quality OS | `{build_id, commit, failures}` |
| `deployment_started` | Deploy begins | Dev OS | Ops OS, All OS | `{service, version, strategy}` |
| `deployment_completed` | Deploy succeeds | Dev OS | Ops OS, All OS | `{service, version, healthy}` |
| `review_completed` | Code review approved | Dev OS | Dev OS | `{pr_id, reviewer, verdict}` |
| `review_failed` | Code review rejected | Dev OS | Dev OS | `{pr_id, reviewer, reasons}` |

## Support OS Events

| Event | Trigger | Producer | Consumers | Payload |
|-------|---------|----------|-----------|---------|
| `ticket_created` | Support request received | Support OS | Support OS, Knowledge OS | `{ticket_id, client, priority}` |
| `ticket_triaged` | Ticket assigned and prioritized | Support OS | Support OS | `{ticket_id, agent, priority}` |
| `ticket_escalated` | Ticket requires senior attention | Support OS | Support OS, Strategy OS | `{ticket_id, reason, severity}` |
| `ticket_resolved` | Issue resolved and confirmed | Support OS | Knowledge OS, Quality OS | `{ticket_id, resolution, satisfaction}` |
| `sla_breach_warning` | SLA threshold approaching | Support OS | Support OS | `{ticket_id, sla_remaining}` |
| `sla_breached` | SLA not met | Support OS | Strategy OS, Quality OS | `{ticket_id, sla_exceeded_by}` |
| `satisfaction_recorded` | Client feedback collected | Support OS | Support OS, Quality OS | `{ticket_id, score, comments}` |

## Agent OS Events

| Event | Trigger | Producer | Consumers | Payload |
|-------|---------|----------|-----------|---------|
| `harness_created` | New harness defined | Agent OS | Agent OS, Knowledge OS | `{harness_id, os, version}` |
| `harness_validated` | Harness passes all checks | Agent OS | Agent OS | `{harness_id, valid, fields}` |
| `skill_registered` | New skill added to registry | Agent OS | Agent OS, All OS | `{skill_id, os, version}` |
| `skill_deprecated` | Skill marked for removal | Agent OS | Agent OS | `{skill_id, replacement}` |
| `agent_spawned` | New agent instantiated | Agent OS | All OS | `{agent_id, harness, os}` |
| `agent_failed` | Agent health check fails | Agent OS | Agent OS, Ops OS | `{agent_id, failure, last_heartbeat}` |
| `agent_retired` | Agent decommissioned | Agent OS | Knowledge OS | `{agent_id, reason, lessons}` |
| `agent_performance_recorded` | Agent metrics collected | Agent OS | Strategy OS, Finance OS | `{agent_id, metrics, period}` |
| `mcp_permission_granted` | Tool access approved | Agent OS | Security OS | `{agent_id, tool, permission}` |
| `mcp_permission_revoked` | Tool access removed | Agent OS | Security OS | `{agent_id, tool}` |

## Knowledge OS Events

| Event | Trigger | Producer | Consumers | Payload |
|-------|---------|----------|-----------|---------|
| `knowledge_stored` | New knowledge captured | Knowledge OS | All OS | `{asset_id, source, layer}` |
| `knowledge_retrieved` | Knowledge searched | Knowledge OS | All OS | `{query, results, latency}` |
| `adr_created` | Decision record documented | Knowledge OS | All OS | `{adr_id, title, status}` |
| `adr_updated` | Decision record modified | Knowledge OS | All OS | `{adr_id, status, superseded_by}` |
| `memory_pruned` | Old knowledge archived | Knowledge OS | Knowledge OS | `{asset_id, archived_at}` |
| `relationship_created` | Knowledge graph link established | Knowledge OS | Knowledge OS | `{from_node, to_node, type}` |

## Finance OS Events

| Event | Trigger | Producer | Consumers | Payload |
|-------|---------|----------|-----------|---------|
| `payment_received` | Revenue collected | Finance OS | Finance OS, Sales OS | `{amount, source, customer}` |
| `cost_recorded` | AI execution cost logged | Finance OS | Finance OS, Strategy OS | `{provider, model, cost, tokens}` |
| `invoice_generated` | Invoice created and sent | Finance OS | Finance OS, Knowledge OS | `{invoice_id, customer, amount}` |
| `invoice_paid` | Invoice marked as paid | Finance OS | Finance OS | `{invoice_id, amount, date}` |
| `roi_calculated` | ROI analysis complete | Finance OS | Strategy OS, Knowledge OS | `{initiative, roi, period}` |
| `subscription_created` | New subscription active | Finance OS | Finance OS, Sales OS | `{customer, plan, value}` |
| `subscription_cancelled` | Subscription terminated | Finance OS | Finance OS, Support OS | `{customer, plan, reason}` |

## Security OS Events

| Event | Trigger | Producer | Consumers | Payload |
|-------|---------|----------|-----------|---------|
| `secret_rotated` | Credential refreshed | Security OS | Security OS, Ops OS | `{secret_name, version}` |
| `secret_leaked` | Credential exposed | Security OS | Security OS, All OS | `{secret_name, severity}` |
| `security_alert` | Suspicious activity detected | Security OS | Security OS, All OS | `{alert_id, severity, source}` |
| `incident_detected` | Security incident confirmed | Security OS | Security OS, All OS | `{incident_id, severity, vector}` |
| `incident_contained` | Threat isolated | Security OS | Security OS | `{incident_id, containment_method}` |
| `incident_resolved` | Incident fully resolved | Security OS | Knowledge OS | `{incident_id, lessons, playbook}` |
| `audit_triggered` | Compliance audit begins | Security OS | Security OS, Quality OS | `{audit_id, scope, period}` |
| `audit_completed` | Compliance audit ends | Security OS | Knowledge OS, Strategy OS | `{audit_id, score, findings}` |
| `access_granted` | Permission assigned | Security OS | Security OS | `{user, resource, level}` |
| `access_revoked` | Permission removed | Security OS | Security OS | `{user, resource}` |

## Ops OS Events

| Event | Trigger | Producer | Consumers | Payload |
|-------|---------|----------|-----------|---------|
| `service_down` | Health check fails | Ops OS | Ops OS, All OS | `{service, downtime, impact}` |
| `service_recovered` | Service restored | Ops OS | Ops OS, All OS | `{service, downtime, resolution}` |
| `service_degraded` | Performance degraded | Ops OS | Ops OS, Security OS | `{service, metric, threshold}` |
| `container_crashed` | Container exits unexpectedly | Ops OS | Ops OS | `{container, exit_code, logs}` |
| `disk_full` | Storage exceeds threshold | Ops OS | Ops OS, All OS | `{mount, usage_pct}` |
| `scaled_up` | Resources increased | Ops OS | Finance OS | `{service, from, to}` |
| `scaled_down` | Resources decreased | Ops OS | Finance OS | `{service, from, to}` |
| `deployment_rolled_back` | Deploy reverted | Ops OS | Dev OS, All OS | `{service, from_version, to_version}` |
| `backup_created` | Backup completed | Ops OS | Ops OS | `{backup_id, size, location}` |
| `backup_verified` | Backup integrity confirmed | Ops OS | Ops OS | `{backup_id, valid}` |

## Quality OS Events

| Event | Trigger | Producer | Consumers | Payload |
|-------|---------|----------|-----------|---------|
| `test_suite_passed` | All tests green | Quality OS | Dev OS, Ops OS | `{suite, count, coverage}` |
| `test_suite_failed` | Tests have failures | Quality OS | Dev OS | `{suite, failures, regressions}` |
| `regression_detected` | Previously passing test fails | Quality OS | Dev OS, Quality OS | `{test, last_passed, regression}` |
| `evaluation_done` | Score evaluation complete | Quality OS | Strategy OS, Knowledge OS | `{entity, type, score}` |
| `compliance_checked` | Template compliance verified | Quality OS | Agent OS | `{artifact, template, compliant}` |

## Strategy OS Events

| Event | Trigger | Producer | Consumers | Payload |
|-------|---------|----------|-----------|---------|
| `initiative_created` | New initiative approved | Strategy OS | All OS | `{initiative_id, os, score}` |
| `initiative_killed` | Initiative terminated | Strategy OS | All OS, Knowledge OS | `{initiative_id, reason, lessons}` |
| `score_updated` | Enterprise score recalculated | Strategy OS | All OS | `{score, delta, breakdown}` |
| `quarter_started` | New quarter begins | Strategy OS | All OS | `{quarter, objectives, entropy_items}` |
| `quarter_planned` | Quarter planning complete | Strategy OS | Knowledge OS | `{quarter, roadmap, initiatives}` |
| `vision_updated` | Long-term vision revised | Strategy OS | All OS | `{year, direction, changes}` |
| `health_review_completed` | Weekly OS health review done | Strategy OS | All OS | `{report, risks, recommendations}` |

---

## Event Delivery Guarantees

| Guarantee | Standard | Critical |
|-----------|----------|----------|
| Delivery | At least once | Exactly once |
| Retry | 3 attempts | 5 attempts |
| Timeout | 30s | 10s |
| Dead letter | After retries exhausted | After retries exhausted |
| Priority | Normal | Immediate alert |
