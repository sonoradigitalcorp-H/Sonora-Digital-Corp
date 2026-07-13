# Stripe Payments

- **MCP Server**: payments_mcp
- **Tools**: stripe_create_checkout, stripe_create_payment, stripe_create_product, stripe_list_products
- **Input**: price_id, success_url, cancel_url (checkout); amount_cents, currency (payment)
- **Output**: `{url, session_id}` o `{id, status, amount}`
- **Ejemplo**: `stripe_create_checkout("price_abc", "https://.../success", "https://.../cancel")`
- **Permisos**: requiere STRIPE_API_KEY
- **Endpoint**: POST :8180/mcp/execute
