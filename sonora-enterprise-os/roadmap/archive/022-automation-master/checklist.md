# Quality Checklist: Automation Master

---

## QA General

- [ ] Cada fase completada 100% antes de avanzar
- [ ] Todos los servicios tienen healthcheck
- [ ] Todas las APIs tienen manejo de errores + retry
- [ ] Ninguna API key hardcodeada (solo env vars)
- [ ] Logs estructurados (JSON) para todo pipeline
- [ ] Alertas configuradas para cada servicio crítico
- [ ] Backups automáticos verificados con checksum
- [ ] Documentación actualizada por cada fase
- [ ] Tests de integración para cada nuevo conector

## Seguridad

- [ ] Sin secrets en código (`.env` + vault)
- [ ] Rate limiting en endpoints públicos
- [ ] Validación de webhooks (firma HMAC)
- [ ] Acceso mínimo por API key (scoped permissions)
- [ ] Logs sin datos sensibles (PII, tokens)
- [ ] HTTPS forzado en todos los endpoints

## Performance

- [ ] n8n workflows <30s de ejecución
- [ ] Agente CFO reporte <60s (incluyendo LLM)
- [ ] Dashboard carga <2s
- [ ] Pipeline contenido blog <5min total
- [ ] Pipeline video <15min total (con TTS)
- [ ] Healthcheck <5s por servicio

## Monitoreo

- [ ] Dashboard de estado accesible 24/7
- [ ] Alertas funcionando (probadas con fallo simulado)
- [ ] Logs rotados diariamente
- [ ] Métricas de éxito visibles en dashboard

## Validación por Fase

| Fase | Check | Método |
|------|-------|--------|
| 1 | 0 intervenciones manuales 14d | Log de acciones humanas vs automáticas |
| 2 | 30d contenido automático | Calendario vs publicaciones reales |
| 3 | 1 venta 100% autónoma | Trazabilidad: idea → producto → pago → entrega |
| 4 | 30d reportes CFO sin fallos | Log de ejecución del agente CFO |
| 5 | 60d operación continua | Uptime + intervenciones + revenue consistency |
