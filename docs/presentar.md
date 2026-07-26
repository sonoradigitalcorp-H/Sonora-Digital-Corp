# Skill: Presentar — Generador de Presentaciones Ejecutivas

**Business Objective**: Cada vez que el fundador diga "deploy" o "presentame", generar automaticamente una presentacion reveal.js con todo el estado del sistema, desplegarla en ~/evolucion/ y servirla en :8080.

---

## Inputs

```gherkin
Given a session has completed
And session data exists in memory/learning/session-YYYYMMDD.json
When the user says "presentame" or "deploy" or "presentacion"
```

## Outputs

```gherkin
Then a reveal.js presentation is generated at ~/evolucion/presentacion-YYYYMMDD.html
And it is served at http://VPS_IP:8080/presentacion-YYYYMMDD.html
And the session summary is appended to memory/learning/events.jsonl
```

## Events

```
Events:
- presentation_generated: when presentation is created
- presentation_deployed: when presentation is live on :8080
```

## Dependencies

```
Dependencies:
- scripts/presentar.py: Python generator (skill)
- ~/evolucion/: output directory
- evolucion-dashboard.service: systemd serving :8080
- memory/learning/session-*.json: session data input
```

## Tools

```
Tools:
- scripts/presentar.py --session <path>: generates the presentation
- systemctl --user restart evolucion-dashboard: restarts the server if needed
```

## Success Metrics

```
Success Metrics:
- presentation_generated: HTTP 200 on /presentacion-YYYYMMDD.html
  Target: 100% of sessions
```

## Failure Conditions

```
Failure Conditions:
- No session JSON found: no memory/learning/session-*.json for today
- Error en generacion: presentar.py exits non-zero
- Port 8080 not accessible: evolucion-dashboard service down
```

## Recovery Procedure

```
Recovery Procedure:
1. Check session JSON exists in memory/learning/
2. Run python3 scripts/presentar.py --session <path>
3. If :8080 down: systemctl --user restart evolucion-dashboard
```

## Business Value

```
Business Value: Zero founder effort for executive reporting. 
Each session produces a polished, navigable presentation 
automatically. No slides, no design, no deployment steps.
```

## Parent OS

```
Parent OS: Knowledge OS / Strategy OS
```

## Version

```
Version: 1.0.0
```

## Audit Trail

```
Audit Trail:
- ADR: ADR-20260701-004 (Capability Registry)
- Events: presentation_generated, presentation_deployed
- Logs: memory/learning/events.jsonl
```
