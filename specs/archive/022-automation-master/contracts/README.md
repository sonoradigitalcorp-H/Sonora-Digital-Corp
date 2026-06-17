# API Contracts: Automation Master

---

## 1. Agente CFO → Hermes (Reporte Diario)

**Trigger**: Cron 8AM → `agent-cfo` skill → generate report → POST Hermes

```
POST /hermes/send
Content-Type: application/json
{
  "channel": "telegram",
  "chat_id": "{{TELEGRAM_CHAT_ID}}",
  "message": "📊 *Reporte Diario - {date}*\n\nIngresos: ${revenue}\nCostos: ${costs}\nGanancia: ${profit} (${margin}%)\n\nTop Producto: {top_product}\nAlertas: {alerts}\n\n---\nSistema Autónomo • 24/7"
}
```

## 2. Agente Creador → n8n (Publicar Contenido)

**Trigger**: Content ready → webhook POST → n8n workflow

```
POST /n8n/webhook/publish
Content-Type: application/json
{
  "action": "publish_content",
  "payload": {
    "type": "blog",
    "title": "string",
    "content": "markdown string",
    "platform": "ghost" | "wordpress" | "medium",
    "seo": {
      "meta_title": "string",
      "meta_description": "string",
      "keywords": ["string"],
      "slug": "string"
    },
    "schedule": "ISO8601 datetime (optional)"
  },
  "source": "agent_creador"
}
```

## 3. n8n → Agentes (Webhook Callback)

**Trigger**: Action completed → callback

```
POST /hermes/agents/callback
Content-Type: application/json
{
  "event": "content_published" | "payment_received" | "error",
  "data": {
    "content_id": "uuid",
    "url": "https://...",
    "status": "published" | "failed",
    "published_at": "ISO8601"
  },
  "original_action": { "action": "...", "payload": { ... } }
}
```

## 4. Mercado Pago Webhook → Agente CFO

**Trigger**: Payment received/refunded via MP

```
POST /webhooks/mercadopago
Content-Type: application/json
x-signature: HMAC-SHA256
{
  "action": "payment.created" | "payment.updated" | "payment.refunded",
  "api_version": "v1",
  "data": {
    "id": "payment_id"
  },
  "date_created": "ISO8601"
}
```

## 5. Stripe Webhook → Agente CFO

**Trigger**: Payment received/refunded via Stripe

```
POST /webhooks/stripe
Content-Type: application/json
stripe-signature: HMAC-SHA256
{
  "type": "payment_intent.succeeded" | "charge.refunded" | "invoice.paid",
  "data": {
    "object": { "id": "pi_xxx", "amount": 1000, "currency": "usd" }
  }
}
```

## 6. Healthcheck Endpoint

```
GET /health
Response: {
  "status": "ok" | "degraded" | "down",
  "services": {
    "neo4j": "ok",
    "qdrant": "ok",
    "n8n": "ok",
    "hermes": "ok",
    "openclaw": "ok"
  },
  "uptime_hours": 123.4,
  "last_failure": "ISO8601 or null",
  "memory_usage_percent": 45.2,
  "disk_usage_percent": 62.1
}
```

## 7. Agente CFO Report Endpoint

```
GET /api/cfo/report/today
Response: {
  "date": "2026-06-10",
  "revenue": 450.00,
  "costs": 120.50,
  "profit": 329.50,
  "margin_percent": 73.2,
  "top_product": {"name": "Template Pack", "revenue": 200.00},
  "products_sold": 12,
  "trend_7d": +5.2,
  "alerts": ["OpenRouter balance bajo: $18.50"],
  "generated_at": "2026-06-10T08:00:00Z",
  "execution_time_ms": 45230
}
```

---

## Auth

| Endpoint | Método | Auth |
|----------|--------|------|
| `/hermes/send` | POST | HMAC key |
| `/n8n/webhook/publish` | POST | n8n webhook key |
| `/webhooks/mercadopago` | POST | Signature verification |
| `/webhooks/stripe` | POST | Signature verification |
| `/health` | GET | None (internal) |
| `/api/cfo/report` | GET | Bearer token |
