# SDD Verify

**Parent OS**: Agent OS
**Tier**: 2
**Description**: Valida cumplimiento de constitución, checklist y tests después de aplicar cambios

## Verification Gates
1. **Truth Gate** — validar contra `sonora-enterprise-os/constitution/`
2. **Tests Gate** — ejecutar tests y verificar que pasan
3. **Score Gate** — score final ≥ 60
4. **Lint Gate** — `ruff check --quiet`

## Output
- Resultado de cada gate (PASS/FAIL)
- Si algún gate falla, no se archivea

## References
- `scripts/verify-gate.py`
- `docs/PROTOCOLO.md`
