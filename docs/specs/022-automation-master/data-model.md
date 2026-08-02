# Data Model: Automation Master

---

## Neo4j Nodos

### FinancialTransaction
```
id: string (uuid)
type: "income" | "expense" | "refund" | "fee"
source: "mercadopago" | "stripe" | "manual"
amount: float (USD)
currency: string (USD/BRL/ARS)
description: string
product_id: string (ref)
timestamp: datetime
metadata: json (raw API response)
```

### Product
```
id: string (slug)
name: string
type: "course" | "template" | "guide" | "service"
status: "active" | "paused" | "retired"
price: float
cost: float (production + fees)
margin: float (calculated)
niche: string
created_at: datetime
last_sale: datetime
total_sales: int
total_revenue: float
```

### ContentPiece
```
id: string (uuid)
title: string
type: "blog" | "video" | "social" | "email"
platform: string
status: "draft" | "scheduled" | "published" | "failed"
url: string (published)
scheduled_at: datetime
published_at: datetime
metrics: json {views, likes, shares, comments, clicks}
seo_score: int
```

### ContentPlan
```
id: string (date-based)
week_start: date
theme: string
pieces: [ContentPiece]
status: "planned" | "active" | "completed"
performance_score: float
```

### CostCenter
```
id: string
name: string (VPS, OpenRouter, APIs, etc.)
monthly_cost: float
billing_cycle: "monthly" | "yearly" | "variable"
last_billed: date
next_billing: date
alert_threshold: float
```

### AgentRun (log de ejecución)
```
id: string (uuid)
agent: string (cfo, estratega, creador)
task: string
status: "ok" | "error" | "timeout"
duration_ms: int
tokens_used: int
result_summary: string
timestamp: datetime
error: string (nullable)
```

---

## Neo4j Relaciones

```
(Product)-[:HAS_SALE]->(FinancialTransaction)
(Product)-[:BELONGS_TO]->(Niche)
(ContentPlan)-[:INCLUDES]->(ContentPiece)
(ContentPiece)-[:PROMOTES]->(Product)
(AgentRun)-[:PRODUCED]->(Report)
(CostCenter)-[:CHARGED]->(FinancialTransaction)
```

---

## Engram Keys (caché de contexto)

| Key | Value | TTL |
|-----|-------|-----|
| `cfo:last_report` | Último reporte generado (texto completo) | 7d |
| `cfo:daily_summary:{date}` | Resumen diario estructurado | 30d |
| `cfo:trends_7d` | Tendencia de ingresos 7 días | 1d |
| `content:calendar:{week}` | Calendario semanal | 7d |
| `market:trending_topics` | Temas trending de la semana | 1d |
| `system:health:{service}` | Último healthcheck | 1h |

---

## n8n Workflow Data (webhook payloads)

### Incoming Webhook (from agents → n8n)
```json
{
  "action": "publish_content" | "send_email" | "create_product" | "schedule_post",
  "payload": { ... },
  "source": "agent_cfo" | "agent_creador" | "agent_estratega",
  "idempotency_key": "uuid"
}
```

### Outgoing Webhook (n8n → agents via Hermes)
```json
{
  "event": "content_published" | "payment_received" | "error",
  "data": { ... },
  "timestamp": "ISO8601"
}
```

---

## Archivos de Configuración

| Archivo | Propósito |
|---------|-----------|
| `config/n8n/` | 7 workflows JSON |
| `config/content-templates/` | Plantillas por tipo de contenido |
| `config/agents/cfo-config.json` | Config del agente CFO (APIs, schedule) |
| `config/agents/estratega-config.json` | Config del agente estratega |
| `.env` | API keys y secrets |
