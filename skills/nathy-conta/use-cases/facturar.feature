Feature: Facturar CFDI
  La contadora puede timbrar CFDI de ingreso, pago y nómina

  Scenario: Timbrar factura de ingreso
    Given la contadora tiene los datos del cliente "FOURGEAMEXICO"
    And el monto total es $15,000.00 MXN
    When solicita timbrar CFDI de ingreso
    Then el sistema genera el XML con cadena original
    And envía al PAC para timbrar
    And devuelve UUID válido
    And guarda en carpeta del cliente

  Scenario: Cancelar factura por acuerdo
    Given existe un CFDI con UUID "12345678-1234-1234-1234-123456789abc"
    When la contadora solicita cancelación por motivo 02 (acuerdo)
    Then el sistema solicita cancelación al PAC
    And genera XML de sustitución
    And actualiza estado a cancelado

  Scenario: Error al timbrar con RFC inválido
    Given el RFC "XXXX010101XXX" no está activo en SAT
    When la contadora intenta timbrar
    Then el sistema rechaza el timbrado
    And muestra error: "RFC no válido o no activo"
