Feature: Cotización de joyería personalizada
  As a cliente
  I want cotizar joyería con diseño personalizado
  So that tenga una pieza única

  Background:
    Given el sistema está operativo
    And el tenant "joyeria_{cliente}" está activo

  @flow-personalizado
  Scenario: Cliente solicita diseño personalizado
    Given un cliente describe una pieza personalizada
    When el agente registra los detalles del diseño
    Then el sistema cotiza con markup por personalización (50%)
    And el tiempo de entrega es de 10-15 días hábiles

  @flow-express
  Scenario: Cliente necesita entrega urgente
    Given un cliente necesita una joya en menos de 24 horas
    When el agente verifica disponibilidad en tiendas físicas
    Then el sistema ofrece recogida en tienda o envío express con costo adicional
