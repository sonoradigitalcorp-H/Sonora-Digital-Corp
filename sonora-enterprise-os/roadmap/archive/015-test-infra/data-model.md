# Data Model: Infraestructura de Tests
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| TestFile | name, path, test_count, type | Archivo de test |
| TestSuite | name, test_count, pass_count, fail_count, duration | Suite de tests |
| CoverageReport | file, lines, covered, percentage | Reporte de cobertura |
## Relaciones
```
(TestSuite)-[:CONTAINS]->(TestFile)
(TestFile)-[:HAS_COVERAGE]->(CoverageReport)
```
