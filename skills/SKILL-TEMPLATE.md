# Skill Template — Sonora Digital Corp

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-TPL-001

---

Every skill definition must include all 14 fields below. A skill is not valid unless all fields are complete.

---

## 1. Business Objective

What business value this skill provides.

```
Business Objective: <one sentence describing the business value>
```

---

## 2. Inputs (Gherkin)

What conditions must be true for this skill to execute.

```gherkin
Given <precondition>
And <additional precondition>
When <trigger condition>
```

---

## 3. Outputs (Gherkin)

What outcomes this skill produces.

```gherkin
Then <primary outcome>
And <secondary outcome>
```

---

## 4. Events

What events this skill fires.

```
Events:
- <event_name>: <when it fires>
```

---

## 5. Dependencies

What other skills, services, or data this skill needs.

```
Dependencies:
- <dependency>: <type (skill/service/data)>
```

---

## 6. Tools

What tools this skill uses to execute.

```
Tools:
- <tool name>: <purpose>
```

---

## 7. Policies

What rules constrain this skill's execution.

```
Policies:
- <policy statement>
```

---

## 8. Success Metrics

How success is measured.

```
Success Metrics:
- <metric>: <gherkin definition>
  Target: <value>
```

---

## 9. Failure Conditions

What constitutes failure.

```
Failure Conditions:
- <condition>: <detection method>
```

---

## 10. Recovery Procedure

How to recover from failure.

```
Recovery Procedure:
1. <step>
2. <step>
```

---

## 11. Business Value

Quantified value this skill provides.

```
Business Value: <quantified value>
```

---

## 12. Parent OS

Which sub-OS this skill belongs to.

```
Parent OS: <OS name>
```

---

## 13. Version

Semantic version of this skill.

```
Version: <semver>
```

---

## 14. Audit Trail

Where this skill's decisions are logged.

```
Audit Trail:
- ADR: <reference>
- Events: <event list>
- Logs: <log location>
```

---

## Validation Checklist

- [ ] Business objective is quantified
- [ ] Inputs are defined in Gherkin
- [ ] Outputs are defined in Gherkin
- [ ] All events are registered in event catalog
- [ ] Dependencies are documented
- [ ] Tools are listed
- [ ] Policies are enforceable
- [ ] Success metrics have targets
- [ ] Failure conditions are detectable
- [ ] Recovery procedure exists
- [ ] Business value is quantified
- [ ] Parent OS is specified
- [ ] Version is set
- [ ] Audit trail is documented
