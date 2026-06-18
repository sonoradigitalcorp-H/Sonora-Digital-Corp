# spawn-agent — Agent Lifecycle Management

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-AGT-001

---

## 1. Business Objective

Spawn, configure, monitor, and retire agents on demand with zero human intervention.

## 2. Inputs (Gherkin)

```gherkin
Given a task request arrives
When task matches an existing agent capability
And agent capacity is available
```

## 3. Outputs (Gherkin)

```gherkin
Then agent is spawned with correct harness
And agent is configured with task parameters
And agent executes assigned task
And agent_spawned event fires
And when task completes, agent_completed event fires
```

## 4. Events

```
Events:
- agent_spawned: agent created and configured
- agent_completed: agent finished task successfully
- agent_failed: agent encountered unrecoverable error
- agent_retired: agent terminated after task completion
```

## 5. Dependencies

```
Dependencies:
- Agent OS: agent registry and capability mapping
- opencode.json: agent definitions
- Harness definitions: harnesses/*.md
```

## 6. Tools

```
Tools:
- opencode CLI: spawn and manage agents
- python3: capability matching logic
- sqlite3: task queue management
```

## 7. Policies

```
Policies:
- Every agent must have a matching harness before spawning
- Agents must be tagged with their parent OS
- No more than 5 concurrent agents per OS
- Idle agents are retired after 30 minutes
- Agent lifecycle must be fully traceable
```

## 8. Success Metrics

```gherkin
Success Metrics:
- spawn_time: Given request When agent ready Then seconds elapsed
  Target: < 10s
- task_completion_rate: Given agents spawned When completed Then rate
  Target: > 95%
- agent_utilization: Given active agents When utilized Then percentage
  Target: > 80%
```

## 9. Failure Conditions

```
Failure Conditions:
- No harness found: task has no matching harness (reject with explanation)
- Capacity full: max concurrent agents reached (queue until slot available)
- Agent crash: agent process exits unexpectedly (log, restart once)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If no harness found → reject task, notify requesting OS with gap analysis
2. If capacity full → queue task, notify when slot opens
3. If agent crashes → restart once, if crashes again → escalate to Ops OS
4. Log all attempts to state/logs/skills/spawn-agent.log
```

## 11. Business Value

```
Business Value: Fully automated agent lifecycle. Eliminates manual agent management. Estimated 5h/week saved.
```

## 12. Parent OS

```
Parent OS: Agent
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: agent_spawned, agent_completed, agent_failed, agent_retired
- Logs: state/logs/skills/spawn-agent.log
```
