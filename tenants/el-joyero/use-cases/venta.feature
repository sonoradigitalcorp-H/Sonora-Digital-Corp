Feature: Venta de joyería
  As a cliente de joyería
  I want cotizar y comprar joyas
  So that reciba mi producto a tiempo y en buen estado

  Background:
    Given el sistema está operativo
    And el tenant "joyeria_{cliente}" está activo
    And la API key de OpenRouter está configurada

  @flow-principal
  Scenario: Cliente cotiza un anillo de compromiso
    Given un cliente solicita cotización de un anillo de compromiso
    When el agente sales-joyeria recibe la solicitud
    Then el sistema responde con precio, tiempo de entrega y opciones de personalización
    And la cotización se guarda en el CRM

  @flow-principal
  Scenario: Cliente realiza una compra
    Given un cliente acepta una cotización
    When el agente registra la orden en Shopify
    Then la orden se confirma con número de seguimiento
    And se notifica al cliente por WhatsApp

  @flow-secundario
  Scenario: Cliente solicita devolución
    Given un cliente recibió un producto defectuoso
    When el cliente solicita devolución dentro de los 30 días
    Then el sistema genera una guía de devolución
    And programa la recogida con el paquetería
