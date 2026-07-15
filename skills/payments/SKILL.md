---
name: payments
description: Process payments, reconcile transactions, manage refunds via MercadoPago. Use when handling payments, orders, or financial operations.
version: 1.0.0
updated: 2026-07-13
---

# Payments Skill

Handle payment processing, reconciliation, and financial operations via MercadoPago.

## Tools que usa
- `mp_create_preference` — crear checkout
- `mp_get_payment` — consultar estado
- `mp_handle_webhook` — procesar IPN
- `mp_list_products` — listar productos
- `hasura_query` — consultar transacciones
- `hasura_mutate` — actualizar estados
- `engram_save` — registrar operación

## Pipeline diario (12:00)
1. `hasura_query` → transacciones del día
2. `mp_get_payment` — verificar estado de cada una
3. `hasura_mutate` — actualizar transacciones pendientes
4. `engram_save` — guardar reconciliación diaria

## Ejemplo
```
Revisa pagos pendientes de ayer y reconciliación
```
