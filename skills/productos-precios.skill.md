# productos-precios — SDC Product Catalog & Pricing

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-SDC-PROD-001
**Parent OS**: Sales

---

## 1. Business Objective

Enable any agent to present, recommend, and sell all SDC products and packages with accurate pricing, features, and upgrade paths — eliminating the need for human product knowledge during prospect conversations.

## 2. Inputs (Gherkin)

```gherkin
Given the system has the SDC product catalog loaded
When a prospect asks about products, pricing, or packages
Or when a sales flow requires product recommendation
```

## 3. Outputs (Gherkin)

```gherkin
Then the agent responds with accurate product/pricing information
And recommends the best-fit product or package based on prospect needs
And includes a clear CTA (diagnóstico gratis, demo, or purchase)
And logs the inquiry as a sales event
```

## 4. Events

```
Events:
- sdc:products:queried: product/pricing information delivered
- sdc:products:recommended: specific product recommended
- sdc:products:upgrade-offered: package or product upgrade suggested
```

## 5. Dependencies

```
Dependencies:
- Product catalog: skill (this file — embedded data)
- Pricing data: skill (this file — embedded data)
- Sales pipeline: service (skills/harnesses/sales-harness.md)
```

## 6. Tools

```
Tools:
- llm_chat: compose product/pricing response
- sales/qualify-lead: capture and score lead if interest detected
```

## 7. Policies

```
Policies:
- Prices must be in Mexican pesos (MXN) with monthly (mensual) denomination
- Packages must be presented with clear savings vs. buying individual products
- Every pricing response must include a low-barrier entry (Starter Gratis or Diagnóstico Gratis)
- All products must be listed in response — never omit options
- Products can be combined into custom packages on request
- Pricing is subject to change — verify against billing system for final quotes
```

## 8. Success Metrics

```gherkin
Success Metrics:
- product_accuracy: Given product query When answered Then correct price/features
  Target: 100%
- recommendation_rate: Given product info When user continues conversation Then percentage
  Target: > 30%
- upgrade_offered: Given single-product user When package mentioned Then conversion interest
  Target: > 15%
```

## 9. Failure Conditions

```
Failure Conditions:
- Mismatched price: quoted price differs from billing system
- Missing product: a product is omitted from the response
- Wrong recommendation: product recommended does not match prospect's stated need
- Unavailable product: product has been deprecated but still offered
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If price mismatch → apologize, verify against billing, re-send correct quote
2. If missing product → check catalog completeness, regenerate with full list
3. If wrong recommendation → ask clarifying questions about the prospect's needs
4. If unavailable product → offer alternatives and explain deprecation timeline
5. Log all corrections to state/logs/skills/productos-precios.log
6. Fire event: sdc:products:correction-applied
```

## 11. Business Value

```
Business Value: Eliminates human product knowledge dependency for sales conversations. Enables 24/7 automated selling across all channels (WhatsApp, Telegram, Web, Social) with 10 products + packages. Estimated: 40+ hours/month saved in manual product explanation.
```

## 12. Parent OS

```
Parent OS: Sales
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: sdc:products:queried, sdc:products:recommended, sdc:products:upgrade-offered
- Logs: state/logs/skills/productos-precios.log
```

---

## Appendix A — SDC Product Catalog (Single Source of Truth)

### Individual Products

| # | Producto | Precio (MXN/mes) | Descripción |
|---|----------|-----------------|-------------|
| 1 | **Cyber Diagnosis Express** | $999 | Auditoría de ciberseguridad express con audio + reporte |
| 2 | **SSL Guardian** | $299 | Monitoreo de certificados SSL/TLS con alertas 24/7 |
| 3 | **DNS Guardian** | $399 | Protección DNS contra spoofing y phishing |
| 4 | **Email Guardian** | $399 | Protección contra spoofing de correo corporativo |
| 5 | **Call Engine Mini** | $999 | Agente de llamadas IA que vende por ti |
| 6 | **Super Seller Agent** | $1,499 | Agente de ventas IA con contexto completo de productos, paquetes y precios |
| 7 | **Clone Mini** | $999 | Réplica facial + voz para contenido promocional |
| 8 | **WhatsApp Agent Mini** | $599 | Bot WhatsApp IA que vende 24/7 |
| 9 | **Uptime Guardian** | $199 | Monitoreo de disponibilidad 24/7 |
| 10 | **Backup Guardian** | $499 | Backups automáticos con verificación |

### Paquetes

| Paquete | Precio | Incluye |
|---------|--------|---------|
| **Starter Gratis** | $0/mes | 1 diagnóstico gratuito, 1 dominio monitoreado, Reporte HTML + Audio Mystic |
| **Seguridad Total** | $499/mes | Diagnóstico semanal automático, Monitoreo SSL + DNS + Email Guardian, Alertas 24/7, Dashboard unificado |

### Tono de ventas

- Profesional, cálido, mexicano
- Explicar beneficios antes que características técnicas
- Ofrecer siempre el Starter Gratis como primer paso sin riesgo
- Usar "diagnóstico gratis" como puerta de entrada
- Mencionar que Mystic (IA) puede personalizar cualquier paquete
