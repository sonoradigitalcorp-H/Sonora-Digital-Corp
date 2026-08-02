# language: es
Caracteristica: Pago via MercadoPago
  Como cliente que quiere pagar su suscripcion
  Quiero pagar de forma segura con tarjeta o SPEI
  Para activar o renovar mi servicio

  Escenario: Pago exitoso con tarjeta de credito en paquete Elevar
    Dado que el cliente "roberto-contador" esta en el paquete Elevar
    Y su fecha de cobro es hoy
    Y tiene tarjeta de credito registrada en MercadoPago
    Cuando se ejecuta el cobro automatico mensual
    Entonces MercadoPago crea un cargo por $1,499 MXN
    Y el cargo se procesa exitosamente
    Y se genera factura CFDI con los datos fiscales de Roberto
    Y se envia la factura por email a Roberto
    Y el periodo de servicio se renueva por 30 dias
    Y se registra la transaccion en PostgreSQL: {tenant_id, monto, metodo, status, timestamp}

  Escenario: Pago fallido - tarjeta rechazada
    Dado que el cliente "ana-reposteria" tiene fondos insuficientes
    Cuando se ejecuta el cobro automatico
    Entonces MercadoPago retorna status "rejected"
    Y se programa reintento para 24 horas despues
    Y se envia notificacion por WhatsApp a Ana: "Tu pago fue rechazado. Actualiza tu metodo de pago."
    Y los agentes de Ana siguen activos durante el periodo de gracia
    Cuando pasan 3 reintentos fallidos
    Entonces los agentes de Ana se pausan
    Y se envia email: "Tu servicio ha sido pausado. Actualiza tu pago para reactivar."

  Escenario: Pago con OXXO (efectivo)
    Dado que el cliente "don-felipe" elige pagar en OXXO
    Cuando genera su pago mensual
    Entonces MercadoPago genera una referencia de pago OXXO
    Y la referencia se envia por WhatsApp y email a Don Felipe
    Y la referencia es valida por 72 horas
    Cuando Don Felipe paga en OXXO antes de las 72 horas
    Entonces MercadoPago envia webhook con status "approved"
    Y el servicio se activa inmediatamente
    Y se envia confirmacion: "Pago recibido. Servicio activo por 30 dias."

  Escenario: Upgrade de paquete con prorrateo
    Dado que "ana-reposteria" esta en Despertar ($299) a mitad del mes
    Cuando Ana selecciona upgrade a Elevar ($1,499)
    Entonces se calcula el prorrateo: $299/2 = $149.50 de credito
    Y el cargo inicial de Elevar es: $1,499 - $149.50 = $1,349.50
    Y el siguiente cobro mensual sera $1,499 completos
    Y se ejecuta el cobro via MercadoPago por $1,349.50
    Y Ana recibe acceso inmediato a todas las features de Elevar

  # Metricas:
  # | Metrica | Target | Medicion |
  # |---------|--------|----------|
  # | Tiempo de generacion de referencia OXXO | < 2s | API response time |
  # | Tiempo de activacion post-pago | < 30s | Webhook processing time |
  # | Reintentos programados | 3 en 3 dias | Celery retry count |
  # | Periodo de gracia agents activos | 3 dias | Config value |
  # | Factura generada | < 5s post-pago | CFDI generation time |