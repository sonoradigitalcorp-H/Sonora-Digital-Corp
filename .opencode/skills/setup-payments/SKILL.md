---
name: setup-payments
description: >
  Configura procesador de pagos para un cliente.
  Soporta Stripe y Mercado Pago. Crea productos, precios,
  webhooks y almacena credenciales.
license: MIT
compatibility: opencode
metadata:
  domain: finance
  capabilities: payments, stripe, mercado-pago
---

## Qué hace

Configura el sistema de pagos para un cliente:
- Crea productos en Stripe/Mercado Pago
- Configura precios y suscripciones
- Conecta webhooks para eventos de pago
- Almacena credenciales cifradas

## Cuándo usarlo

- Cuando un nuevo cliente necesita cobrar
- Cuando se agrega un nuevo producto/suscripción
- Cuando se cambia de procesador

## Pasos

1. **Preguntar preferencias**
   - Stripe o Mercado Pago?
   - Lista de productos/servicios con precios
   - Suscripciones? (precio, frecuencia)

2. **Configurar en Stripe (si aplica)**
   - Usar MCP stripe para crear productos y precios
   - Crear webhook endpoint
   - Probar: crear un payment link

3. **Configurar en Mercado Pago (si aplica)**
   - Usar API de Mercado Pago
   - Crear preferencias de pago
   - Configurar webhook

4. **Guardar credenciales**
   - Almacenar en config/secrets/ cifrado
   - No exponer en texto plano

5. **Probar flujo completo**
   - Crear un pago de prueba
   - Verificar webhook

## Referencias

- Stripe MCP: config en opencode.json
- Mercado Pago API: docs en developers.mercadopago.com
