# TRACE — {{TITLE}}

| Campo | Valor |
|-------|-------|
| **ID** | `TR-{{ID}}` |
| **Spec** | {{SPEC_ID}} |
| **Fecha** | {{DATE}} |

## Feature → Spec → Task → Commit → Deploy

```
Feature: {{FEATURE_NAME}}
  └── Spec: {{SPEC_ID}}
       └── Tasks:
            ├── {{TASK_1}} → Commit {{COMMIT_1}} → Deploy {{DEPLOY_1}}
            └── {{TASK_2}} → Commit {{COMMIT_2}} → Deploy {{DEPLOY_2}}
```

## ADRs

| ADR | Decision | Status |
|-----|----------|--------|
| {{ADR_1}} | {{DECISION_1}} | {{STATUS_1}} |

## Events

| Event | ID | Timestamp |
|-------|-----|-----------|
| {{EVT_1}} | {{EID_1}} | {{ETS_1}} |
