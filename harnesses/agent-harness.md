# Agent Harness — Agent Lifecycle Agent

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: HARNESS-AGT-001

---

## 1. Mission

Manage the complete lifecycle of all sub-agents from spawning to retirement with zero human intervention.

## 2. Capabilities

```
Capabilities:
- Agent Spawning: Create and configure agents on demand
  Events: agent_spawned
- Agent Monitoring: Track agent health and performance
  Events: agent_health_report
- Agent Retirement: Terminate idle or failed agents
  Events: agent_retired
- Capability Mapping: Match tasks to available agent capabilities
  Events: task_routed
```

## 3. Skills

```
Skills:
- spawn-agent: Create, configure, and manage agent lifecycles
  Source: skills/spawn-agent.skill.md
```

## 4. Policies

```
Policies:
- Every agent must have a matching harness before spawning
- No more than 5 concurrent agents per OS
- Idle agents retired after 30 minutes
- Agent lifecycle must be fully traceable via events
```

## 5. Memory Scope

```
Memory Scope:
  Read: Layer 1 (Working), Layer 2 (Task), Layer 3 (Project)
  Write: Layer 1 (Working), Layer 2 (Task), Layer 6 (Historical)
```

## 6. Approval Requirements

```
Approval Requirements:
- agent spawn: none
- agent retire: none
- new capability registration: notify
- agent destruction: approve (for persistent agents)
```

## 7. Failure Modes

```
Failure Modes:
- Spawn failure: agent process fails to start (retry, escalate)
- Agent crash: agent exits unexpectedly (restart once, log)
- Resource exhaustion: too many agents (block spawn, queue)
```

## 8. Recovery Procedures

```
Recovery Procedures:
- spawn failure: retry with fresh config, escalate after 3 failures
- agent crash: restart once, capture crash dump, escalate if repeats
- resource exhaustion: queue request, retire oldest idle agent
```

## 9. Metrics

```
Metrics:
- spawn_time: Given request When agent ready Then seconds
  Target: < 10s
- agent_uptime: Given spawned agents When running Then percentage
  Target: > 99%
- task_completion: Given tasks assigned When completed Then percentage
  Target: > 95%
```

## 10. Tests

```gherkin
Feature: Agent Harness
  Scenario: Spawn agent for task
    Given a task request arrives
    When a matching agent exists
    Then agent is spawned and configured
    And agent_spawned event fires

  Scenario: Retire idle agent
    Given an agent has been idle > 30 min
    When retirement check runs
    Then agent is terminated
    And agent_retired event fires
```

## 11. Observability

```
Observability:
- Health endpoint: via Web UI status
- Metrics: spawn_time, agent_uptime, task_completion
- Log level: INFO
- Log location: state/logs/harnesses/agent-harness.log
```

## 12. Dependencies

```
Dependencies:
- spawn-agent: skill (skills/spawn-agent.skill.md)
- opencode.json: agent definitions
- Harness definitions: all harness files
```

---

## Validation Checklist

- [x] Mission is one sentence, measurable
- [x] All capabilities map to events
- [x] All skills reference existing skill definitions
- [x] All policies are enforceable
- [x] Memory scope is defined for read and write
- [x] Approval requirements cover all critical actions
- [x] All failure modes have recovery procedures
- [x] All metrics have Gherkin definitions
- [x] Tests exist and pass
- [x] Observability endpoints are defined
- [x] All dependencies are documented
