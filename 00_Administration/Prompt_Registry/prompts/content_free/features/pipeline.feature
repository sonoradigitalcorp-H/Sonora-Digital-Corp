Feature: Pipeline de contenido libre end-to-end
  Como agente de marketing neutral
  Quiero generar un reel IG sin costo desde un guion
  Para publicar contenido diario de PyMEs

  Scenario: Genera reel con imagen HF y voz edge-tts
    Given un guion validado en config
    And FREE_TIER_ONLY=true
    When ejecuto el pipeline con nicho "restaurante"
    Then se genera una imagen via hf-zerogpu
    And se genera voz via edge-tts DaliaNeural
    And se compone un MP4 9:16 via ffmpeg
    And el video se publica en Instagram sin error
    And el costo total registrado es 0.00

  Scenario: Acepta activos manuales del Jefe
    Given una imagen y un audio provistos manualmente
    And FREE_TIER_ONLY=true
    When ejecuto solo la fase de composicion y publicacion
    Then se produce un MP4 9:16 y se publica en IG
    And no se llama a ningun generador de IA

  Scenario: Feedback loop ajusta pesos tras metricas
    Given metricas IG de un post publicado
    When feedback_loop procesa likes, reach, views
    Then actualiza peso_template en JSON persistente
    And el cambio es trazable en log
