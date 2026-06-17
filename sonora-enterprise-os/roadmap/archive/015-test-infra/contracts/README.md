# Contracts: Infraestructura de Tests
**Spec**: spec.md
---
## API Contracts
- `GET /api/tests/status` — Estado de los tests
- `GET /api/tests/coverage` — Reporte de cobertura
## Data Contracts
```json
{ "test_suite": { "name": "string", "total": "int", "passed": "int", "failed": "int", "duration": "float" } }
{ "coverage": { "file": "string", "lines": "int", "covered": "int", "percentage": "float" } }
```
