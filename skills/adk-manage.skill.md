# adk-manage — ADK Agent Management

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-ADK-001

---

## 1. Business Objective

List, inspect, and trigger ADK agents via the ADK Bridge with zero setup per agent.

## 2. Inputs (Gherkin)

```gherkin
Given ADK Bridge is connected via opencode_bridge.py
When agent list is requested
Or specific agent execution is triggered
```

## 3. Outputs (Gherkin)

```gherkin
Then all available agents are listed with metadata
And selected agent executes with provided input
And execution result is returned as structured data
```

## 4. Events

```
Events:
- adk:agent:listed: agent catalog retrieved
- adk:agent:executed: agent run completed
```

## 5. Dependencies

```
Dependencies:
- ADK Bridge: opencode_bridge.py
- Agent definitions: 36 pre-built YAML configs
- Runtime: ADK execution environment
```

## 6. Tools

```
Tools:
- adk_execute: run agent via opencode_bridge.py bridge
```

## 7. Policies

```
Policies:
- Agent execution must be authorized per capability policy
- Rate limits apply per agent type (max 10/min)
- Long-running agents must report progress via events
- Agent execution must respect cost budgets
```

## 8. Success Metrics

```gherkin
Success Metrics:
- list_time: Given agent list request When completed Then milliseconds
  Target: < 1 s
- execution_success_rate: Given agent executions in period When succeeded Then rate
  Target: > 95%
```

## 9. Failure Conditions

```
Failure Conditions:
- Bridge disconnected: ADK Bridge process not running (restart bridge)
- Agent not found: requested agent missing from registry (verify YAML)
- Execution timeout: agent takes longer than 60s (terminate, escalate)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If bridge disconnected → restart opencode_bridge.py, verify connection
2. If agent not found → check agents/registry.yaml, re-register if missing
3. If execution timeout → terminate agent, log partial results, escalate
4. Log all attempts to state/logs/skills/adk-manage.log
```

## 11. Business Value

```
Business Value: 36 pre-built agents available from any channel. Zero setup per agent.
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
- Events: adk:agent:listed, adk:agent:executed
- Logs: state/logs/skills/adk-manage.log
```
