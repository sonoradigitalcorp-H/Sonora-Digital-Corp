# Agent Registry — MANIFEST.md

## Levels of Autonomy

| Level | Name | Description |
|-------|------|-------------|
| L0 | Manual | Full human control. Agent proposes, human executes. |
| L1 | Assisted | Agent executes, reports result, human can cancel. |
| L2 | Supervised | Agent acts autonomously, human reviews periodic summary. |
| L3 | Delegated | Agent acts independently, human only for exceptions. |
| L4 | Autonomous | Full autonomy. Agent sets own goals within its domain. |

---

## Current Agents

| Agent | Role | Level | Capabilities | SLA | Budget |
|-------|------|-------|-------------|-----|--------|
| **OpenClaw** | Primary Operator | L1 | Code, infra, pipeline | On-demand | — |
| **JARVIS Core** | System Orchestrator | L1 | Orchestration, monitoring, memory | 24/7 | — |
| **ABE** | Music Production Agent | L1 | Music gen, delivery gate, Telegram | 24/7 | — |
| **Engram** | Memory System | L2 | Store, query, promote, decay | 24/7 | — |
| **Enterprise Score** | Metrics & Governance | L1 | Score calculation, event logging | On-demand | — |

## Planned Agents

| Agent | Role | Target Level | Dependencies |
|-------|------|-------------|--------------|
| Sales Agent | Lead → Qualify → Quote → Onboard | L2 | CRM pipeline, n8n |
| Support Agent | Ticket → Diagnose → Resolve → Learn | L2 | Support OS, n8n |
| FinOps Agent | Track costs → Budget → Alert → Report | L2 | FinOps pipeline |
| Content Agent | Generate → Review → Publish → Measure | L2 | Content OS |
| QA Agent | Test → Report → Re-test → Approve | L2 | Test harness |
| DevOps Agent | Deploy → Monitor → Recover → Report | L3 | Infra OS |
| Research Agent | Discover → Analyze → Summarize → Recommend | L1 | Knowledge OS |

## Event Bus (Redis + n8n)

All agents communicate via events on Redis pub/sub. n8n workflows subscribe to events and trigger actions.

| Topic | Producers | Consumers |
|-------|-----------|-----------|
| `spec.created` | Pipeline | Engram, CATALOG |
| `spec.completed` | Pipeline | Engram, Score, CATALOG |
| `spec.rejected` | Pipeline | — |
| `score.calculated` | Score.sh | Dashboard, FinOps |
| `deployment.started` | DevOps Agent | Status page |
| `deployment.completed` | DevOps Agent | Status page, Events |
| `error.detected` | JARVIS | Error Correction, Dashboard |
| `error.recovered` | JARVIS | Dashboard, Lecciones |
| `knowledge.stored` | Engram | Knowledge OS |
| `revenue.recorded` | Sales Agent | FinOps, Dashboard |
| `agent.failed` | Any | JARVIS Orchestrator |

---

## Policies

1. **No agent may exceed its budget** without human approval (enforced by FinOps)
2. **Every agent action must emit at least one event** (enforced by the agent harness)
3. **L3+ agents must have a documented recovery procedure** before promotion
4. **Agent capabilities are permanent, agents are temporary** — skills outlive agents
