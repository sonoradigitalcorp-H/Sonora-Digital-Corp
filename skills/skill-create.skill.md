# skill-create — Meta-Skill for Skill Creation

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-CRT-001

---

## 1. Business Objective

Create new skills following SKILL-TEMPLATE.md with all 14 fields guaranteed complete and validated.

## 2. Inputs (Gherkin)

```gherkin
Given skill specification is provided (name, description, tools, business value, parent OS)
When SKILL-TEMPLATE.md exists at skills/SKILL-TEMPLATE.md
And existing skills are available for reference
```

## 3. Outputs (Gherkin)

```gherkin
Then skill.md file is created with all 14 fields populated
And skill is validated against the template checklist
And skill is registered in the capability catalog
```

## 4. Events

```
Events:
- skill:created: new skill file written and registered
- skill:validated: skill passed all 14-field checks
```

## 5. Dependencies

```
Dependencies:
- SKILL-TEMPLATE.md: skills/SKILL-TEMPLATE.md
- Existing skills: reference implementations
- Catalog: skills registry index
```

## 6. Tools

```
Tools:
- engram_search: retrieve existing skill patterns
- llm_chat: generate field content from specification
- filesystem: write skill file to skills/ directory
```

## 7. Policies

```
Policies:
- Every new skill must pass all 14-field validation before registration
- Skills must use the exact field headers defined in SKILL-TEMPLATE.md
- Skills must be registered in the capability catalog
- Duplicate names are not allowed
```

## 8. Success Metrics

```gherkin
Success Metrics:
- creation_time: Given specification When skill created Then minutes
  Target: < 5 min
- validation_pass_rate: Given created skills When validated Then percentage
  Target: 100%
```

## 9. Failure Conditions

```
Failure Conditions:
- Template missing: SKILL-TEMPLATE.md not found (restore from git)
- Validation fails: one or more fields missing or malformed
- Registration fails: catalog write error
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If template missing → restore from process/templates/SKILL-TEMPLATE.md
2. If validation fails → identify missing fields, regenerate
3. If registration fails → check catalog permissions, retry
4. Log all attempts to state/logs/skills/skill-create.log
```

## 11. Business Value

```
Business Value: New skills created in minutes with guaranteed completeness.
```

## 12. Parent OS

```
Parent OS: Quality
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: skill:created, skill:validated
- Logs: state/logs/skills/skill-create.log
```
