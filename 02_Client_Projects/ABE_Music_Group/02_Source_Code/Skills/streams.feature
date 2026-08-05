Feature: Consulta de streams
  Como artista musical
  Quiero consultar mis reproducciones en plataformas
  Para medir mi rendimiento y crecimiento

  Background:
    Given soy un artista registrado en ABE Music

  Scenario: Consultar streams totales
    When consulto mis streams del último mes
    Then recibo el total de reproducciones
    And veo el desglose por plataforma
    And veo el porcentaje de crecimiento

  Scenario: Consultar streams por plataforma específica
    When consulto mis streams en "Spotify"
    Then veo solo las reproducciones de Spotify
    And veo oyentes únicos en esa plataforma

  Scenario: Generar reporte de streams
    When solicito un reporte de streams del periodo "30d"
    Then recibo un enlace para descargar el PDF
