Feature: Gestión de lanzamientos
  Como artista musical
  Quiero programar y distribuir mis lanzamientos
  Para llegar a mi audiencia en todas las plataformas

  Background:
    Given soy un artista registrado en ABE Music

  Scenario: Programar un nuevo lanzamiento
    When programo un lanzamiento llamado "Nueva Ola" para el "2026-08-01"
    Then el lanzamiento queda registrado como "programada"
    And recibo una confirmación con la fecha

  Scenario: Notificar lanzamiento
    Given tengo un lanzamiento programado
    When notifico el lanzamiento a mis seguidores
    Then se envía mensaje a WhatsApp y Telegram

  Scenario: Distribuir lanzamiento
    When distribuyo el lanzamiento "Nueva Ola"
    Then se envía a todas las plataformas de streaming
    And recibo confirmación del distribuidor
