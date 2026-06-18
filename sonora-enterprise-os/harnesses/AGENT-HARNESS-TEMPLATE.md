# Agent Harness Template — Sonora Digital Corp

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: HARNESS-TPL-001

---

Every agent harness must define all 12 fields below. A harness is not valid unless all fields are complete.

---

## 1. Mission

What this agent exists to do. One sentence. Measurable.

```
Mission: <one sentence describing the agent's purpose>
```

---

## 2. Capabilities

What capabilities this agent provides. Each capability must map to an event.

```
Capabilities:
- <capability name>: <description>
  Events: <event1>, <event2>
```

---

## 3. Skills

What skills this agent can execute. Each skill must reference a skill definition.

```
Skills:
- <skill name>: <description>
  Source: skills/<skill-name>.skill.md
```

---

## 4. Policies

Rules this agent must always follow.

```
Policies:
- <policy statement>
```

---

## 5. Memory Scope

Which memory layers this agent can read and write.

```
Memory Scope:
  Read: Layer 1 (Working), Layer 2 (Task)
  Write: Layer 1 (Working), Layer 3 (Project)
```

---

## 6. Approval Requirements

When this agent needs human approval.

```
Approval Requirements:
- <action>: <approval level (none/notify/approve/escalate)>
```

---

## 7. Failure Modes

What can go wrong and how it is detected.

```
Failure Modes:
- <failure>: <detection method>
```

---

## 8. Recovery Procedures

How this agent recovers from each failure.

```
Recovery Procedures:
- <failure>: <step 1>, <step 2>, <step N>
```

---

## 9. Metrics

How this agent's performance is measured.

```
Metrics:
- <metric name>: <gherkin definition>
  Target: <value>
```

---

## 10. Tests

Gherkin tests that validate this agent exists and works.

```gherkin
Feature: <Agent Name>
  Scenario: <scenario name>
    Given <precondition>
    When <action>
    Then <expected outcome>
```

---

## 11. Observability

What this agent exposes for monitoring.

```
Observability:
- Health endpoint: </health>
- Metrics endpoint: </metrics>
- Log level: <INFO/DEBUG>
```

---

## 12. Dependencies

What other agents, skills, or services this agent depends on.

```
Dependencies:
- <dependency name>: <type (agent/skill/service)>
```

---

## Validation Checklist

- [ ] Mission is one sentence, measurable
- [ ] All capabilities map to events
- [ ] All skills reference existing skill definitions
- [ ] All policies are enforceable
- [ ] Memory scope is defined for read and write
- [ ] Approval requirements cover all critical actions
- [ ] All failure modes have recovery procedures
- [ ] All metrics have Gherkin definitions
- [ ] Tests exist and pass
- [ ] Observability endpoints are defined
- [ ] All dependencies are documented
