# Tasks: Automation Master

**Spec**: 022-automation-master | **Duration**: 6 meses (5 fases)

---

## Fase 1: Estabilización (Semanas 1-8)

### Diagnóstico (S1-2)
- [ ] T1.1: Auditoría de servicios activos (docker ps, systemctl, n8n workflows)
- [ ] T1.2: Identificar puntos de fallo recurrentes en logs últimos 30 días
- [ ] T1.3: Documentar dependencias críticas (APIs keys, tokens, saldos)
- [ ] T1.4: Crear dashboard de estado (HTML estático servido por FastAPI)

### Automatización Mantenimiento (S3-4)
- [ ] T1.5: Healthchecks cada 15 min vía cron + script `/scripts/healthcheck.sh`
- [ ] T1.6: Auto-reparación: systemd restart on failure + script recovery
- [ ] T1.7: Backup diario con verificación (sum checksum + log)
- [ ] T1.8: Limpieza automática de logs >30 días y temporales

### Monitoreo (S5-6)
- [ ] T1.9: Alertas vía Hermes → Telegram (servicio caído, disco >90%, OOM)
- [ ] T1.10: Umbrales: CPU >80%, RAM >85%, disco >90%, uptime <1h
- [ ] T1.11: Reporte semanal de salud (domingos 9PM)
- [ ] T1.12: Validación: 7 días sin intervención manual

### Skills (S7-8)
- [ ] T1.13: Skill maintenance en OpenClaw (restart, cleanup, backup)
- [ ] T1.14: Runbook de desastres en `specs/022/runbook.md`
- [ ] T1.15: Validación final: 14 días sin intervención manual

---

## Fase 2: Pipeline Contenido (Semanas 9-16)

### Ideación (S9-10)
- [ ] T2.1: Agente Estratega semanal basado en AgenteEstratega en orquestador
- [ ] T2.2: Fuentes: GitHub trending, Reddit top, Google Trends API
- [ ] T2.3: Calendario editorial 30d en Neo4j (nodo ContentPlan)
- [ ] T2.4: Skill `content-strategist` en OpenClaw

### Generación (S11-12)
- [ ] T2.5: Pipeline blog: research → outline → draft → SEO → publish
- [ ] T2.6: Pipeline video: script → TTS (ElevenLabs/sag) → captions → publish
- [ ] T2.7: Pipeline redes: extract → adapt → schedule per platform
- [ ] T2.8: Plantillas por tipo en `config/content-templates/`

### Publicación (S13-14)
- [ ] T2.9: n8n workflow `workflow-daily-content.json` → blog + redes
- [ ] T2.10: n8n workflow `workflow-video-publish.json` → YouTube/TikTok
- [ ] T2.11: SEO auto: meta, keywords, schema.org JSON-LD
- [ ] T2.12: Schedule optimizado por plataforma (Buffer-style)

### Métricas (S15-16)
- [ ] T2.13: Dashboard rendimiento (views, engagement, conversions)
- [ ] T2.14: A/B testing headlines (2 variantes por post)
- [ ] T2.15: Ajuste automático de strategy basado en data
- [ ] T2.16: Validación: 30 días contenido sin intervención

---

## Fase 3: Negocio Autónomo (Semanas 17-24)

### Investigación (S17-18)
- [ ] T3.1: Auto-análisis de demanda por nicho (trends + search volume)
- [ ] T3.2: Identificación de oportunidades de producto digital
- [ ] T3.3: Benchmarking competitivo automático

### Creación (S19-20)
- [ ] T3.4: Pipeline producto digital: idea → outline → content → assets → landing
- [ ] T3.5: Landing pages autogeneradas desde template + copy
- [ ] T3.6: Copywriting con hooks + beneficios + CTAs persuasivos
- [ ] T3.7: Assets visuales (canva API, DALL-E / fal.ai)

### Ventas (S21-22)
- [ ] T3.8: Integración MP/Stripe vía `src/core/payments.py` existente
- [ ] T3.9: Checkout automatizado (link de pago → confirmación → entrega)
- [ ] T3.10: Email post-venta (gracias, acceso, seguimiento)
- [ ] T3.11: Precios dinámicos basados en demanda y competencia

### Validación (S23-24)
- [ ] T3.12: Dashboard ventas en tiempo real
- [ ] T3.13: Detección baja conversión (productos <2% conversion rate)
- [ ] T3.14: Iteración de producto basada en datos de ventas
- [ ] T3.15: Validación: primera venta 100% autónoma

---

## Fase 4: Agente CFO (Semanas 25-32)

### Recolección (S25-26)
- [ ] T4.1: Conector Mercado Pago API (ventas, comisiones, reembolsos)
- [ ] T4.2: Conector Stripe API (ventas, suscripciones, fees)
- [ ] T4.3: Conector costos (VPS $30, OpenRouter $200, APIs $50)
- [ ] T4.4: Conector analytics (tráfico → conversiones → costo adquisición)

### Motor ETL (S27-28)
- [ ] T4.5: Pipeline ETL diario: raw → clean → metrics → report
- [ ] T4.6: Cálculo de márgenes por producto y canal
- [ ] T4.7: Proyecciones 7d/30d/90d con tendencia lineal
- [ ] T4.8: Detección de anomalías (caída >20% vs promedio 7d)

### Agente CFO (S29-30)
- [ ] T4.9: Skill `agent-cfo` con memoria Neo4j (historial transacciones)
- [ ] T4.10: Contexto Engram para reportes anteriores
- [ ] T4.11: Generación reporte: texto + tabla + gráfico (ASCII/mermaid)
- [ ] T4.12: Ejecución diaria 8AM vía cron → hermes → telegram

### Canales (S31-32)
- [ ] T4.13: Reporte Telegram (resumen: ganancia/día, top producto, alertas)
- [ ] T4.14: Reporte Notion (detalle completo con tablas)
- [ ] T4.15: Dashboard web (FastAPI + Chart.js)
- [ ] T4.16: Alertas financieras (ingresos -20%, costos +30%, saldo OpenRouter bajo)
- [ ] T4.17: Validación: 30 días de reportes sin intervención

---

## Fase 5: Escala Autónoma (Semanas 33-40)

### Optimización Costos (S33-34)
- [ ] T5.1: Análisis automático gastos por servicio
- [ ] T5.2: Recomendaciones de optimización (cambio tier, proveedor)
- [ ] T5.3: Auto-escalado (más RAM si demanda, menos si no)

### Optimización Contenido (S35-36)
- [ ] T5.4: Algoritmo de contenido que aprende de CTR, engagement, conversiones
- [ ] T5.5: Ajuste automático de estrategia editorial semanal
- [ ] T5.6: Priorización de canales con mejor ROI

### Optimización Productos (S37-38)
- [ ] T5.7: Detección de oportunidades de nuevo producto (gap analysis)
- [ ] T5.8: Retiro automático de productos no rentables (0 ventas en 60d)
- [ ] T5.9: Ajuste de precios basado en elasticidad de demanda

### Pipeline Único (S39-40)
- [ ] T5.10: Integración de todos los agentes en pipeline secuencial
- [ ] T5.11: Agente CFO como único output visible al humano
- [ ] T5.12: Supervisión humana reducida a 15 min/semana
- [ ] T5.13: Dashboard ejecutivo con KPIs: ingresos, costos, ganancia, trend
- [ ] T5.14: Validación: 60 días de operación autónoma continua

---

**Total**: 70 tasks | **5 fases** | **40 semanas**
