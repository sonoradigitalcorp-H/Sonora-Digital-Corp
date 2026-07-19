# adr-generate — Auto-generate Architecture Decision Records

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-ADR-001

---

## 1. Business Objective

Auto-generate Architecture Decision Records for every feature implementation, following ADR.md template.

## 2. Inputs (Gherkin)

```gherkin
Given feature specification is complete
When implementation phase begins
And ADR template exists at docs/templates/ADR.md
```

## 3. Outputs (Gherkin)

```gherkin
Then ADR document is generated with all required sections
And decision context is archived to engram
And ADR is linked from the feature specification
```

## 4. Events

```
Events:
- adr:generated: new ADR created and persisted
- adr:archived: ADR moved to long-term storage
```

## 5. Dependencies

```
Dependencies:
- ADR template: docs/templates/ADR.md
- Filesystem: write access to process/adr/ directory
- Engram: observation persistence for cross-session recall
```

## 6. Tools

```
Tools:
- llm_chat: generate ADR content from feature context
- engram_save: persist ADR decision to cross-session memory
- filesystem: write ADR markdown file to process/adr/
```

## 7. Policies

```
Policies:
- Every feature must have an ADR before implementation begins
- ADRs must follow the ADR.md template structure
- ADRs must be linked from the originating SPEC
- Generated ADRs must be reviewed before archiving
```

## 8. Success Metrics

```gherkin
Success Metrics:
- generation_time: Given feature spec When ADR generated Then seconds
  Target: < 2 min
- coverage: Given features in period When ADR count Then percentage
  Target: 100%
```

## 9. Failure Conditions

```
Failure Conditions:
- Template not found: ADR.md missing from expected path
- Generation fails: llm_chat returns incomplete content
- Persistence fails: filesystem write error
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If template missing → restore from SKILL-TEMPLATE.md, adapt header
2. If generation fails → retry with more context, fall back to manual
3. If write fails → check permissions, try alternate path
4. Log all attempts to state/logs/skills/adr-generate.log
```

## 11. Business Value

```
Business Value: Documents every decision in under 2 minutes. No more undocumented architecture.
```

## 12. Parent OS

```
Parent OS: Knowledge
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: adr:generated, adr:archived
- Logs: state/logs/skills/adr-generate.log
```
