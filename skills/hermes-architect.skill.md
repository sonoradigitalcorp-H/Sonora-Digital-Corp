# hermes-architect — Hermes Technical Architect

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-HAR-001

---

## 1. Business Objective

Design technical architecture and provide implementation guidance for Hermes SaaS solutions targeting Mexican SMEs.

## 2. Inputs (Gherkin)

```gherkin
Given user requests architectural design or technical guidance
When trigger keywords are detected: "arquitectura", "diseñar", "cómo implementar", "propuesta técnica", "diseño técnico"
```

## 3. Outputs (Gherkin)

```gherkin
Then architecture recommendation is provided with rationale
And alternatives are listed with trade-off analysis
And implementation steps are outlined with risks
```

## 4. Events

```
Events:
- hermes:architect:executed: architecture recommendation delivered
```

## 5. Dependencies

```
Dependencies:
- LLM: senior architect prompt
- Stack context: FastAPI, Next.js 14, PostgreSQL, Redis, Docker, N8N, Telegram, WhatsApp
- Engram: decision persistence
```

## 6. Tools

```
Tools:
- llm_complete: execute senior architect prompt with user context
- engram_save: persist architectural decisions
```

## 7. Policies

```
Policies:
- Every recommendation must include alternatives considered
- Risks must be documented for each recommended option
- Implementation steps must be ordered by dependency
- Stack must align with existing Hermes architecture
```

## 8. Success Metrics

```gherkin
Success Metrics:
- recommendation_time: Given architecture request When completed Then minutes
  Target: < 3 min
- implementation_rate: Given recommendations in period When implemented Then percentage
  Target: > 60%
```

## 9. Failure Conditions

```
Failure Conditions:
- Outdated stack knowledge: LLM recommends deprecated patterns
- Missing context: insufficient understanding of constraints
- Over-engineered: solution complexity exceeds actual needs
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If outdated → validate against current stack versions
2. If missing context → gather requirements before architecting
3. If over-engineered → simplify, focus on MVP path
4. Log all attempts to state/logs/skills/hermes-architect.log
```

## 11. Business Value

```
Business Value: Senior-level architecture guidance available 24/7 without hiring a solutions architect.
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
- Events: hermes:architect:executed
- Logs: state/logs/skills/hermes-architect.log
```
