# Spec 015: Infraestructura de Tests

## Objetivo
Modernizar la infraestructura de tests para mantener calidad post-modularización.

## Logrado

### Tests de integración modularizados
| Archivo original | Líneas | Reemplazado por |
|-----------------|--------|-----------------|
| `test_api.py` | 373 | `test_api_status.py` (136), `test_api_voice.py` (54), `test_api_stability.py` (223) |

### Logrotate configurado
Los logs rotan diario, comprimidos, 7 días de retención, max 50MB.

## Pendientes

- [ ] Añadir tests para los nuevos módulos de `routes/` y `agents/`
- [ ] Verificar cobertura de código (target: >80%)
- [ ] CI/CD: añadir step de logrotate check
- [ ] Tests de humo post-deploy (healthcheck endpoint)
