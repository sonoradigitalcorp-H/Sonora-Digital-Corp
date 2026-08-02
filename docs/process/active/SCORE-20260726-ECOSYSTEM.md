# SCORE — ECOSYSTEM

| Campo | Valor |
|-------|-------|
| **ID** | `SCORE-20260726-ECOSYSTEM` |
| **Spec** | `SPEC-20260726-ECOSYSTEM` |
| **Score** | 65 |
| **Gate** | ✅ PASS (≥60) |

## Metrics

| Métrica | Valor | Observaciones |
|---------|-------|---------------|
| Specs | 5 | 1 principal + 2 features + ADR + Score |
| Gherkin features | 3 | ecosistema, twilio, tokenomics |
| Gherkin scenarios | 20 | 6 + 5 + 4 + 5 = 20 escenarios |
| ADRs | 1 | ADR-20260726-ECOSYSTEM |
| FRs | 15 | 12 P0-P1 + 3 P2-P3 |
| Architecture | Diagrams | Sí (ASCII + en ADR) |

## Verification

- `make eval` → structural tests pasan
- `make score` → score ≥ 60
- Spec index actualizado
- Spec schema válido
