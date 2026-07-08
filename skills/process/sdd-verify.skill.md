# SDD Verify

**Parent OS**: Agent OS
**Tier**: 2
**Description**: Valida cumplimiento de constitución, checklist y tests después de aplicar cambios

## Verification Gates
1. **Git Sync Gate** — correr `scripts/git-sync.sh --status` para verificar que el repo está sincronizado con origin/main (GIT-006)
2. **Truth Gate** — validar contra `constitution/`
3. **Tests Gate** — ejecutar tests y verificar que pasan
4. **Score Gate** — score final ≥ 60
5. **Lint Gate** — `ruff check --quiet`

## Output
- Resultado de cada gate (PASS/FAIL)
- Si algún gate falla, no se archivea

## References
- `scripts/verify-gate.py`
- `docs/PROTOCOLO.md`
