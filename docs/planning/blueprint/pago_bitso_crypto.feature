# language: es
Caracteristica: Pago via Bitso (Criptomonedas)
  Como cliente que prefiere privacidad y cripto
  Quiero pagar con BTC o USDC a traves de Bitso
  Para mantener mi privacidad financiera

  Escenario: Pago exitoso con USDC
    Dado que el cliente "crypto-carlos" elige pagar con USDC via Bitso
    Y tiene wallet de USDC verificada en Bitso
    Cuando genera su pago mensual de Soberano ($50,000 MXN)
    Entonces el sistema consulta el tipo de cambio USDC/MXN en tiempo real
    Y genera una direccion de deposito USDC unica por transaccion
    Y envia la direccion y monto exacto por email y Telegram
    Y la direccion expira en 2 horas
    Cuando Carlos envia el monto exacto de USDC a la direccion
    Entonces Bitso confirma la transaccion en la blockchain
    Y el webhook de Bitso notifica a Sonora con status "confirmed"
    Y el servicio se activa inmediatamente
    Y se registra en PostgreSQL: {tenant_id, monto_mxn, monto_crypto, crypto, tx_hash, status}

  Escenario: Pago con BTC - conversion automatica
    Dado que el cliente "minero-miguel" elige pagar con BTC
    Cuando genera su pago mensual de Elevar ($1,499 MXN)
    Entonces el sistema calcula el equivalente en BTC al precio actual
    Y genera una direccion BTC unica
    Y muestra un countdown de 30 minutos (volatilidad del BTC)
    Y muestra el monto en BTC con 8 decimales
    Cuando Miguel envia BTC
    Entonces el sistema verifica la transaccion en la blockchain
    Y confirma 3 bloquees (aprox 30 min)
    Y el servicio se activa
    NOTA: Los pagos en crypto NO son reembolsables por naturaleza irreversible

  Escenario: Pago con MXN via Bitso (pesos digitales)
    Dado que el cliente "digital-diana" tiene cuenta de Bitso con saldo en MXN
    Cuando Diana selecciona pagar con MXN via Bitso
    Entonces se genera un link de pago directo a Bitso
    Y Diana es redirigida a Bitso para autorizar el cargo
    Y Bitso confirma el pago via webhook
    Y el servicio se activa

  Escenario: Pago expirado por timeout
    Dado que el cliente genera una direccion de pago crypto
    Y no envia los fondos en el tiempo limite (2 horas USDC, 30 min BTC)
    Entonces la direccion se marca como expirada
    Y se envia notificacion: "Tu referencia de pago expiro. Genera una nueva."
    Y los agentes siguen activos durante el periodo de gracia de 3 dias

  # Metricas:
  # | Metrica | Target | Medicion |
  # |---------|--------|----------|
  # | Consulta tipo de cambio | < 1s | Bitso API response |
  # | Generacion direccion deposito | < 2s | API processing |
  # | Confirmacion blockchain (USDC) | < 5 min | Block confirmations |
  # | Confirmacion blockchain (BTC) | < 45 min | 3 block confirmations |
  # | Webhook processing | < 10s | Server processing time |