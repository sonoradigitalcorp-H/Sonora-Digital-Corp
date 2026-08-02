# SONORA DIGITAL CORP - Manual de Facturacion Automatizada

> **El Sigilo del Token: Cada transaccion se mide con precision divina.**

---

## 1. Flujo General de Facturacion

```
[CELERY BEAT - Scheduler]
    |
    | Cada dia a las 00:00 CST
    v
[Factura Worker] ---> Busca tenants con cobro hoy
    |                    |
    |                    +--> Para cada tenant:
    |                           |
    |                           v
    |                    [Calcular Monto]
    |                    - Precio base del paquete
    |                    - Prorrateo si es primer mes o upgrade
    |                    - Descuentos activos (afiliado, SON)
    |                    - Cargos adicionales (numeros extra, llamadas extra)
    |                    - IVA (16%)
    |                           |
    |                           v
    |                    [Crear Factura en BD]
    |                    status: "pending"
    |                           |
    |                           v
    |                    [Ejecutar Cobro]
    |                    - Metodo preferido del tenant
    |                    - Si falla: reintento en 24h
    |                           |
    |                           v
    |                    [Actualizar Status]
    |                    - "paid" -> activar/renovar servicio
    |                    - "failed" -> programar reintento
    |                    - "overdue" -> pausar agentes
    |                           |
    |                           v
    |                    [Generar CFDI]
    |                    - Solo si status = "paid"
    |                    - Datos fiscales del tenant
    |                    - Enviar por email
```

## 2. Metodos de Pago y Configuracion

### 2.1 MercadoPago
- **Tipo**: Integracion via API REST
- **Webhook**: POST /webhooks/mercadopago con firma HMAC-SHA256
- **Metodos aceptados**: tarjeta de credito/debito, SPEI, OXXO
- **Retention**: El customer_id de MercadoPago se almacena para cobros recurrentes
- **Reintentos**: 3 reintentos en 3 dias (dia 1, dia 2, dia 3)

### 2.2 Bitso (Criptomonedas)
- **Tipo**: Integracion via API REST v3
- **Monedas**: BTC, USDC, MXN digital
- **Flujo**: Generar direccion unica -> Esperar deposito -> Webhook confirma
- **Timeouts**: USDC 2 horas, BTC 30 minutos
- **Conversion**: Precio se consulta en tiempo real al momento de generar la referencia
- **No reembolsable**: Naturaleza irreversible de la blockchain

### 2.3 Efectivo (OXXO)
- **Tipo**: Generado via MercadoPago como referencia OXXO
- **Vigencia**: 72 horas
- **Verificacion**: Webhook de MercadoPago al pagar en tienda

### 2.4 Transferencia Bancaria
- **Tipo**: Solo paquetes Soberano y Oraculo
- **Proceso**: Se genera cuenta CLABE y referencia. El cliente transfiere manualmente.
- **Verificacion**: Conciliacion manual por equipo de Sonora (max 24h)

## 3. Reglas de Facturacion

### 3.1 Ciclo Mensual
- El cobro se ejecuta el mismo dia del mes en que el cliente se registro
- Si el dia de cobro es 31 y el mes tiene 30 dias: se cobra el dia 30
- Si el dia de cobro es 29 (febrero en ano no bisiesto): se cobra el 28

### 3.2 Prorrateo
- Primer mes: Se cobra desde el dia de activacion hasta el ultimo dia del mes
- Upgrade a mitad de mes: Credito proporcional de los dias restantes del paquete anterior
- Downgrade a mitad de mes: Se mantiene el paquete superior hasta el final del periodo

### 3.3 Periodo de Gracia
- Si el cobro falla: 3 dias de gracia con agentes activos
- Dias 1-3: Reintentos automaticos, agentes activos, notificaciones por WhatsApp
- Dia 4: Agentes se pausan, notificacion por email
- Dia 7: Si no hay pago, datos se empiezan a retener segun politica
- Dia 30: Cuenta se cancela, datos se eliminan segun retencion

### 3.4 CFDI (Factura Electronica)
- Solo se genera CFDI cuando el pago se confirma (status = "paid")
- Se usa el RFC y datos fiscales del perfil del cliente
- Metodo de pago SAT: segun metodo real (28 = tarjeta, 03 = transferencia, 01 = efectivo, 17 = crypto)
- La factura se envia automaticamente por email
- Si el cliente no tiene RFC: se emite nota simple (sin CFDI)

### 4. Herramientas del Sistema de Facturacion

| Herramienta | Funcion | Tecnologia |
|------------|---------|-----------|
| Celery Beat | Scheduler de cobros | Python Celery + Redis |
| Factura Worker | Calculo y ejecucion de cobros | Python FastAPI |
| MercadoPago SDK | Cobro tarjeta/SPEI/OXXO | SDK oficial Python |
| Bitso API Client | Generacion de depositos crypto | REST API v3 |
| CFDI Generator | Generacion de factura electronica | Libreria CFDI Python o servicio externo |
| Email Service | Envio de facturas por email | Resend |
| Notification Service | Alertas WhatsApp/Telegram | python-telegram-bot + wacli |

## 5. Reportes Financieros

### 5.1 Reporte Diario (6:00 AM CST)
- Cobros ejecutados ayer
- Cobros fallidos con motivo
- Pagos crypto pendientes
- MRR (Monthly Recurring Revenue) actual
- Churn risk (pagos fallidos > 2 dias)

### 5.2 Reporte Semanal
- MRR vs semana anterior
- Nuevos clientes por paquete
- Upgrades y downgrades
- Ingresos por metodo de pago
- Comisiones de afiliados pagadas

### 5.3 Reporte Mensual
- Revenue total por paquete
- Churn rate por paquete
- LTV promedio por paquete
- CAC (Costo de Adquisicion de Cliente)
- Revenue por tenant (top 10)

---

*Sonora Digital Corp - El Sigilo del Token*