Feature: Facturación recurrente (RESICO)
  As a dueño de Sonora Digital Corp (Régimen RESICO)
  I want que el sistema facture automáticamente a los clientes cada mes
  So that no tenga que hacer facturación manual

  Background:
    Given hay clientes activos con paquetes contratados (Esencial/Pro/Enterprise)
    And estamos a 1ro del mes

  Scenario: Facturación mensual automática
    Given el cliente "Fourgea México" tiene paquete "Profesional" ($12,000/mes)
    When el pipeline de billing detecta "es 1ro del mes"
    Then se genera CFDI 4.0 con:
      | Campo | Valor |
      | Régimen | 626 (RESICO) |
      | Uso CFDI | D01 (Gastos en general) |
      | Forma pago | Transferencia |
    And se timbra el CFDI via PAC (FacturoPorTi/SW SAP)
    And se envía PDF+XML al cliente por WhatsApp y Email
    And se registra el pago como "pendiente"

  Scenario: Cliente sin facturación activa
    Given el cliente tiene paquete cancelado
    When el pipeline de billing corre
    Then no se genera CFDI para ese cliente
    And se registra evento "billing:skipped:inactive_client"

  Scenario: Error al timbrar CFDI
    Given el PAC no responde
    When se intenta timbrar
    Then se reintenta 2 veces con 30s de espera
    And si falla, se envía alerta al admin
    And se registra evento "billing:cfdi:timbre_failed"
