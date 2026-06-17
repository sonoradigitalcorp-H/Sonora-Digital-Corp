# 6. Ventas y Negocios con Telegram

## Bot de Ventas (AzRECBot)
Ya creado en:
```
/home/mystic/products/azrec/telegram/bot-azrec.py
```

### Flujo de Venta
```
Usuario escribe "quiero una gorra"
  → Bot muestra producto y precio
  → Usuario: "la quiero"
  → Bot: "Completa tu pedido:
     - Modelo: Gorra AzREC Classic
     - Color: Negro
     - Talla: Unica
     - Direccion: ...
     - Pago: OXXO / Transferencia"
  → Bot envia resumen al admin (Alejandro)
  → Admin confirma / ajusta
  → Bot da instrucciones de pago
```

### Comandos de Venta
```
/comprar [producto] — Iniciar compra
/pedido [id] — Ver estado de pedido
/catalogo — Ver productos
/pagar — Instrucciones de pago
/envio — Politicas de envio
```

### Metodos de Pago (Mexico)
| Metodo | Comision | Tiempo |
|--------|----------|--------|
| OXXO | 0% (fee fijo ~$15) | 24-48h |
| Transferencia SPEI | 0% | inmediato |
| Mercado Pago Link | ~3% | inmediato |
| Efectivo (recogida) | 0% | en persona |

### Notificaciones al Admin
Cuando alguien compra, el bot le envia al admin:
```
🛒 NUEVO PEDIDO #001
Producto: Gorra AzREC Classic
Cliente: @usuario
Total: $399 MXN
Pago: OXXO pendiente
```

### Politicas Automaticas
El bot puede:
- Confirmar pedido
- Enviar numero de seguimiento
- Recordar pago pendiente (24h, 48h)
- Preguntar review post-entrega
